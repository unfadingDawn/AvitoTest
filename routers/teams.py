from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db

from schemas import raise_api_error, CreateTeamRequest, TeamMemberSchema
from models import DBUser, DBTeam



router = APIRouter(
    prefix="/team",
    tags=["Teams"]
)


@router.post("/add", status_code=201)
def create_team(payload: CreateTeamRequest, db: Session = Depends(get_db)):
    
    if db.query(DBTeam).filter(DBTeam.name == payload.team_name).first():
        return raise_api_error("TEAM_EXISTS", "team_name already exists", 400)

    
    new_team = DBTeam(name=payload.team_name)
    for m in payload.members:
        
        if db.query(DBUser).filter(DBUser.id == m.user_id).first():
            
            pass 
        new_user = DBUser(id=m.user_id, username=m.username, is_active=m.is_active)
        new_team.members.append(new_user)
    
    try:
        db.add(new_team)
        db.commit()
        db.refresh(new_team)
    except IntegrityError:
        db.rollback()
        return raise_api_error("TEAM_EXISTS", "Error creating team", 400)

    return {"team": payload} 

@router.get("/get")
def get_team(team_name: str, db: Session = Depends(get_db)):
    team = db.query(DBTeam).filter(DBTeam.name == team_name).first()
    if not team:
        return raise_api_error("NOT_FOUND", "Team not found", 404)
    
    
    members_list = [
        TeamMemberSchema(user_id=u.id, username=u.username, is_active=u.is_active) 
        for u in team.members
    ]
    return {
        "team_name": team.name,
        "members": members_list
    }



