from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class League(Base):
    __tablename__ = 'leagues'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    country = Column(String(100))
    season = Column(String(20))  # e.g., "2023-2024"
    teams = relationship("Team", back_populates="league")
    
    def __repr__(self):
        return f"<League {self.name} ({self.season})>"

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    league = relationship("League", back_populates="teams")
    statistics = relationship("TeamStatistics", back_populates="team")
    
    # Add unique constraint for team name within a league
    __table_args__ = (
        UniqueConstraint('name', 'league_id', name='uix_team_league'),
    )
    
    def __repr__(self):
        return f"<Team {self.name}>"

class TeamStatistics(Base):
    __tablename__ = 'team_statistics'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    position = Column(Integer)
    matches_played = Column(Integer)
    over_count = Column(Integer)
    under_count = Column(Integer)
    goals_for = Column(Integer)
    goals_against = Column(Integer)
    goals_per_match = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="statistics")
    
    # Add indexes for frequently queried columns
    __table_args__ = (
        Index('ix_team_statistics_team_id', 'team_id'),
        Index('ix_team_statistics_position', 'position'),
        Index('ix_team_statistics_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        # Safer repr that won't fail if team relationship isn't loaded
        team_name = self.team.name if self.team else f"Team ID: {self.team_id}"
        return f"<TeamStatistics {team_name} - {self.timestamp}>" 