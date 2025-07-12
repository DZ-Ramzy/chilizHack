from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    sport = Column(String(50), nullable=False)  # football, basketball, etc.
    league = Column(String(100), nullable=True)  # Premier League, NBA, etc.
    country = Column(String(50), nullable=True)
    logo_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    external_id = Column(String(50), nullable=True, index=True)  # ESPN API ID
    team_metadata = Column(Text, nullable=True)  # JSON string for additional team data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("UserTeam", back_populates="team")
    events_home = relationship("SportsEvent", foreign_keys="SportsEvent.home_team_id", back_populates="home_team")
    events_away = relationship("SportsEvent", foreign_keys="SportsEvent.away_team_id", back_populates="away_team")
    quests = relationship("Quest", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', sport='{self.sport}')>"