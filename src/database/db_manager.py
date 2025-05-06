import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from .models import Base, League, Team, TeamStatistics

class DatabaseManager:
    def __init__(self, db_path: str = "sqlite:///sports_stats.db"):
        """Initialize database connection."""
        self.engine = create_engine(db_path)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def save_league_data(self, league_name: str, country: str, season: str) -> League:
        """Create or update a league entry."""
        with self.get_session() as session:
            league = session.query(League).filter_by(name=league_name).first()
            if not league:
                league = League(name=league_name, country=country, season=season)
                session.add(league)
            else:
                league.country = country
                league.season = season
            session.commit()
            return league
    
    def save_team_stats(self, league_id: int, team_data: dict) -> TeamStatistics:
        """Save team statistics from OCR data."""
        with self.get_session() as session:
            # Get or create team
            team = session.query(Team).filter_by(
                name=team_data['Team'],
                league_id=league_id
            ).first()
            
            if not team:
                team = Team(name=team_data['Team'], league_id=league_id)
                session.add(team)
                session.flush()  # Get the team ID
            
            # Create new statistics entry
            stats = TeamStatistics(
                team_id=team.id,
                position=team_data['Position'],
                matches_played=team_data['MP'],
                over_count=team_data['O'],
                under_count=team_data['U'],
                goals_for=int(team_data['G'].split(':')[0]) if ':' in team_data['G'] else 0,
                goals_against=int(team_data['G'].split(':')[1]) if ':' in team_data['G'] else 0,
                goals_per_match=float(team_data['G/M'])
            )
            
            session.add(stats)
            session.commit()
            return stats
    
    def get_team_stats(self, team_name: str, league_name: str = None) -> list:
        """Get historical statistics for a team."""
        with self.get_session() as session:
            query = session.query(TeamStatistics).join(Team)
            if league_name:
                query = query.join(League)
                query = query.filter(League.name == league_name)
            query = query.filter(Team.name == team_name)
            query = query.order_by(TeamStatistics.timestamp.desc())
            return query.all()
    
    def get_league_standings(self, league_name: str) -> list:
        """Get current standings for a league."""
        with self.get_session() as session:
            # Get the most recent statistics for each team in the league
            return session.query(TeamStatistics)\
                .join(Team)\
                .join(League)\
                .filter(League.name == league_name)\
                .order_by(TeamStatistics.position)\
                .all() 