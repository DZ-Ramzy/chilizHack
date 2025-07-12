from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class SportsEvent(Base):
    __tablename__ = "sports_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sport = Column(String(50), nullable=False)
    league = Column(String(100), nullable=True)
    
    # Teams
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Event timing
    event_date = Column(DateTime(timezone=True), nullable=False)
    venue = Column(String(200), nullable=True)
    
    # Event status
    status = Column(String(50), default="scheduled")  # scheduled, live, finished, cancelled
    is_active = Column(Boolean, default=True)
    
    # External data
    external_id = Column(String(100), nullable=True)  # ID from sports API
    source = Column(String(50), default="espn")  # Source of the event data
    event_metadata = Column(Text, nullable=True)  # JSON string for additional event data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="events_home")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="events_away")
    quests = relationship("Quest", back_populates="event")

    def __repr__(self):
        return f"<SportsEvent(id={self.id}, title='{self.title}', date='{self.event_date}')>"