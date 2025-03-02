from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Odds(Base):
    __tablename__ = "odds"

    id = Column(Integer, primary_key=True, index=True)
    match = Column(String, nullable=False)
    bookmaker = Column(String, nullable=False)
    home_win = Column(Float, nullable=False)
    draw = Column(Float, nullable=False)
    away_win = Column(Float, nullable=False)
    actionable = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
