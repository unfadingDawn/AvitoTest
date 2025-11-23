from pydantic import BaseModel
from typing import List, Optional
import datetime
from fastapi.responses import JSONResponse

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail

class TeamMemberSchema(BaseModel):
    user_id: str
    username: str
    is_active: bool

    class Config:
        from_attributes = True

class TeamSchema(BaseModel):
    team_name: str
    members: List[TeamMemberSchema]

    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    user_id: str
    username: str
    team_name: str
    is_active: bool

class PullRequestSchema(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: str
    assigned_reviewers: List[str] 
    createdAt: Optional[datetime.datetime] = None
    mergedAt: Optional[datetime.datetime] = None

class PullRequestShortSchema(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: str


class CreateTeamRequest(TeamSchema):
    pass

class SetActiveRequest(BaseModel):
    user_id: str
    is_active: bool

class CreatePRRequest(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str

class MergePRRequest(BaseModel):
    pull_request_id: str

class ReassignRequest(BaseModel):
    pull_request_id: str
    old_user_id: str

class ReviewerStat(BaseModel):
    user_id: str
    username: str
    assigned_reviews_count: int

class GlobalStatsResponse(BaseModel):
    total_prs: int
    merged_prs: int
    reviewers_stats: List[ReviewerStat]

def raise_api_error(code: str, message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}}
    )
