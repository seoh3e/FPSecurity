from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from .db import Base

class RawLog(Base):
    __tablename__ = "raw_logs"
    id = Column(Integer, primary_key=True)
    player_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    player_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    alert = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())