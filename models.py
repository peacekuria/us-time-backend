# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Disorder(Base):
    """Model for mental health disorders"""
    __tablename__ = "disorders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    symptoms = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with remedies
    remedies = relationship("Remedy", back_populates="disorder", cascade="all, delete")

class Remedy(Base):
    """Model for treatment remedies"""
    __tablename__ = "remedies"
    
    id = Column(Integer, primary_key=True, index=True)
    disorder_id = Column(Integer, ForeignKey("disorders.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String)  # therapy, medication, lifestyle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship back to disorder
    disorder = relationship("Disorder", back_populates="remedies")

class Assessment(Base):
    """Model for user assessments"""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)  # Anonymous session tracking
    answers = Column(JSON, nullable=False)  # Store as JSON: ["yes", "no", "unsure", ...]
    result = Column(String, nullable=False)  # low, medium, high
    severity_score = Column(Integer, nullable=False)  # 0-5
    suggested_disorder_ids = Column(JSON)  # Array of disorder IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Question(Base):
    """Model for assessment questions"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    category = Column(String)  # mood, sleep, energy, appetite, interest
    weight = Column(Integer, default=1)  # Importance weight for scoring
    order_index = Column(Integer, default=0)  # Display order
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())