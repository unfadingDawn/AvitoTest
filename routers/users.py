from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

from schemas import raise_api_error, SetActiveRequest 
from models import DBUser

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/setIsActive")
def set_is_active(payload: SetActiveRequest, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == payload.user_id).first()
    if not user:
        return raise_api_error("NOT_FOUND", "User not found", 404)
    
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    
    return {"user": {
        "user_id": user.id,
        "username": user.username,
        "team_name": user.team_name,
        "is_active": user.is_active
    }}

