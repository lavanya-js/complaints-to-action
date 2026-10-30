from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from .db import Base


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    tracking_code = Column(String, unique=True, index=True)
    text = Column(Text)
    category = Column(String)
    category_confidence = Column(Float, default=0.0)
    summary = Column(Text, default="")
    lat = Column(Float)
    lng = Column(Float)
    image_path = Column(String, nullable=True)
    status = Column(String, default="Submitted")
    priority_score = Column(Float, default=0.0)
    priority_factors = Column(Text, default="[]")  # JSON list
    priority_explanation = Column(Text, default="")
    duplicate_of = Column(Integer, nullable=True)
    duplicate_confidence = Column(Float, nullable=True)
    cluster_id = Column(Integer, nullable=True)
    ai_source = Column(String, default="classifier")  # classifier | rules
    created_at = Column(DateTime, default=datetime.utcnow)


class StatusHistory(Base):
    __tablename__ = "status_history"
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, index=True)
    status = Column(String)
    note = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, index=True)
    team = Column(String)
    assigned_at = Column(DateTime, default=datetime.utcnow)


class Cluster(Base):
    __tablename__ = "clusters"
    id = Column(Integer, primary_key=True)
    label = Column(String)
    summary = Column(Text, default="")
    center_lat = Column(Float)
    center_lng = Column(Float)
    report_count = Column(Integer, default=0)