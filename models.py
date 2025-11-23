from sqlalchemy import Column, String, Boolean, ForeignKey, Table, DateTime
import datetime

from sqlalchemy.orm import  declarative_base, relationship
Base = declarative_base()

pr_reviewers = Table(
    'pr_reviewers',
    Base.metadata,
    Column('pull_request_id', String, ForeignKey('pull_requests.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True)
)

class DBTeam(Base):
    __tablename__ = "teams"
    name = Column(String, primary_key=True, index=True) 
    members = relationship("DBUser", back_populates="team", cascade="all, delete-orphan")

class DBUser(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True) 
    username = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    team_name = Column(String, ForeignKey("teams.name"))
    
    team = relationship("DBTeam", back_populates="members")
    authored_prs = relationship("DBPullRequest", back_populates="author")
    assigned_reviews = relationship("DBPullRequest", secondary=pr_reviewers, back_populates="reviewers")

class DBPullRequest(Base):
    __tablename__ = "pull_requests"
    id = Column(String, primary_key=True, index=True) 
    title = Column(String, nullable=False) 
    author_id = Column(String, ForeignKey("users.id"))
    status = Column(String, default="OPEN") 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    merged_at = Column(DateTime, nullable=True)

    author = relationship("DBUser", back_populates="authored_prs")
    reviewers = relationship("DBUser", secondary=pr_reviewers, back_populates="assigned_reviews")



