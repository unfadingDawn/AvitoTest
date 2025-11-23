from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from schemas import GlobalStatsResponse, ReviewerStat
from database import get_db
from models import DBPullRequest, DBUser, pr_reviewers



router = APIRouter(
    prefix="/stats",
    tags=["Health"]
)

@router.get("", response_model=GlobalStatsResponse, tags=["Health"])
def get_statistics(db: Session = Depends(get_db)):
    """
    Получить общую статистику по системе:
    - Всего PR
    - Влитых PR
    - Рейтинг ревьюверов (кто сколько проверил)
    """
    
    total_prs_count = db.query(DBPullRequest).count()
    merged_prs_count = db.query(DBPullRequest).filter(DBPullRequest.status == "MERGED").count()

    reviewers_query = (
        db.query(
            DBUser.id,
            DBUser.username,
            func.count(pr_reviewers.c.pull_request_id).label("count")
        )
        .outerjoin(pr_reviewers, DBUser.id == pr_reviewers.c.user_id)
        .group_by(DBUser.id, DBUser.username)
        .order_by(desc("count")) # Сортируем от самых нагруженных к ленивым
        .all()
    )

    # 3. Собираем ответ
    stats_list = [
        ReviewerStat(
            user_id=row.id, 
            username=row.username, 
            assigned_reviews_count=row.count
        ) 
        for row in reviewers_query
    ]

    return {
        "total_prs": total_prs_count,
        "merged_prs": merged_prs_count,
        "reviewers_stats": stats_list
    }
