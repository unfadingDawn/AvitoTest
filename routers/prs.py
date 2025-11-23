from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import datetime
import random

from schemas import MergePRRequest, raise_api_error, ReassignRequest, CreatePRRequest
from models import DBPullRequest, DBUser

router = APIRouter(
    prefix="/pullRequest",
    tags=["PullRequests"]
)

@router.post("/merge")
def merge_pr(payload: MergePRRequest, db: Session = Depends(get_db)):
    pr = db.query(DBPullRequest).filter(DBPullRequest.id == payload.pull_request_id).first()
    
    if not pr:
        return raise_api_error("NOT_FOUND", "PR not found", 404)
    
    
    if pr.status == "MERGED":
        pass 
    else:
        pr.status = "MERGED"
        pr.merged_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(pr)

    return {"pr": {
        "pull_request_id": pr.id,
        "pull_request_name": pr.title,
        "author_id": pr.author_id,
        "status": pr.status,
        "assigned_reviewers": [u.id for u in pr.reviewers],
        "mergedAt": pr.merged_at
    }}


@router.post("/reassign")
def reassign_reviewer(payload: ReassignRequest, db: Session = Depends(get_db)):
    pr = db.query(DBPullRequest).filter(DBPullRequest.id == payload.pull_request_id).first()
    
    
    if not pr:
        return raise_api_error("NOT_FOUND", "PR not found", 404)
    
    
    if pr.status == "MERGED":
        return raise_api_error("PR_MERGED", "cannot reassign on merged PR", 409)

    
    current_reviewer_ids = [u.id for u in pr.reviewers]
    if payload.old_user_id not in current_reviewer_ids:
        return raise_api_error("NOT_ASSIGNED", "reviewer is not assigned to this PR", 409)

    
    
    author = pr.author
    
    candidates = db.query(DBUser).filter(
        DBUser.team_name == author.team_name,
        DBUser.is_active == True,
        DBUser.id != author.id,
        DBUser.id.notin_(current_reviewer_ids) 
    ).all()

    if not candidates:
        return raise_api_error("NO_CANDIDATE", "no active replacement candidate in team", 409)

    new_reviewer = random.choice(candidates)

    
    old_reviewer_obj = next(u for u in pr.reviewers if u.id == payload.old_user_id)
    pr.reviewers.remove(old_reviewer_obj)
    pr.reviewers.append(new_reviewer)
    
    db.commit()
    db.refresh(pr)

    return {
        "pr": {
            "pull_request_id": pr.id,
            "pull_request_name": pr.title,
            "author_id": pr.author_id,
            "status": pr.status,
            "assigned_reviewers": [u.id for u in pr.reviewers]
        },
        "replaced_by": new_reviewer.id
    }


@router.get("/getReview")
def get_user_reviews(user_id: str, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    
    if not user:
        
        return {"user_id": user_id, "pull_requests": []}

    prs = []
    for pr in user.assigned_reviews:
        prs.append({
            "pull_request_id": pr.id,
            "pull_request_name": pr.title,
            "author_id": pr.author_id,
            "status": pr.status
        })

    return {
        "user_id": user_id,
        "pull_requests": prs
    }

@router.post("/create", status_code=201)
def create_pr(payload: CreatePRRequest, db: Session = Depends(get_db)):
    
    if db.query(DBPullRequest).filter(DBPullRequest.id == payload.pull_request_id).first():
        return raise_api_error("PR_EXISTS", "PR id already exists", 409)

    
    author = db.query(DBUser).filter(DBUser.id == payload.author_id).first()
    if not author:
        return raise_api_error("NOT_FOUND", "Author not found", 404)

    
    
    candidates = db.query(DBUser).filter(
        DBUser.team_name == author.team_name,
        DBUser.is_active == True,
        DBUser.id != author.id
    ).all()

    
    selected_reviewers = []
    if candidates:
        count = min(len(candidates), 2)
        selected_reviewers = random.sample(candidates, count)

    
    new_pr = DBPullRequest(
        id=payload.pull_request_id,
        title=payload.pull_request_name,
        author_id=payload.author_id,
        status="OPEN",
        reviewers=selected_reviewers
    )
    
    db.add(new_pr)
    db.commit()
    db.refresh(new_pr)

    return {"pr": {
        "pull_request_id": new_pr.id,
        "pull_request_name": new_pr.title,
        "author_id": new_pr.author_id,
        "status": new_pr.status,
        "assigned_reviewers": [u.id for u in new_pr.reviewers],
        "createdAt": new_pr.created_at,
        "mergedAt": new_pr.merged_at
    }}

