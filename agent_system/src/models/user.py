from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(100), unique=True, index=True, nullable=False)
    preferences = Column(Text, nullable=True)  # JSON string for user preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teams = relationship("UserTeam", back_populates="user")
    quests = relationship("Quest", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, address='{self.address}')>"