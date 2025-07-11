from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base


class QuestType(PyEnum):
    INDIVIDUAL = "individual"
    CLASH = "clash"
    COLLECTIVE = "collective"
    SEASONAL = "seasonal"


class QuestStatus(PyEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    quest_type = Column(Enum(QuestType), nullable=False)
    status = Column(Enum(QuestStatus), default=QuestStatus.PENDING)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for collective quests
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("sports_events.id"), nullable=True)
    
    # Quest Configuration
    target_metric = Column(String(100), nullable=True)  # tweets, posts, etc.
    target_value = Column(Integer, nullable=True)  # 100, 1000, etc.
    current_progress = Column(Integer, default=0)
    
    # Timing
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Content and Validation
    content_template = Column(Text, nullable=True)  # Template for generated content
    validation_rules = Column(Text, nullable=True)  # JSON string for validation rules
    rewards = Column(Text, nullable=True)  # JSON string for rewards
    
    # Metadata
    quest_metadata = Column(Text, nullable=True)  # JSON string for additional quest data
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="quests")
    team = relationship("Team", back_populates="quests")
    event = relationship("SportsEvent", back_populates="quests")

    def __repr__(self):
        return f"<Quest(id={self.id}, title='{self.title}', type='{self.quest_type}', status='{self.status}')>"