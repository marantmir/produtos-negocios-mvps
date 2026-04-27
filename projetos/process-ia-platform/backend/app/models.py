from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    processes = relationship("Process", back_populates="owner", cascade="all, delete-orphan")


class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    area = Column(String(255), nullable=True)
    objective = Column(Text, nullable=True)
    customer = Column(String(255), nullable=True)
    start_event = Column(String(255), nullable=True)
    end_event = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="processes")
    steps = relationship("ProcessStep", back_populates="process", cascade="all, delete-orphan")
    interviews = relationship("ProcessInterview", back_populates="process", cascade="all, delete-orphan")
    insights = relationship("ProcessAIInsight", back_populates="process", cascade="all, delete-orphan")


class ProcessStep(Base):
    __tablename__ = "process_steps"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    step_name = Column(String(255), nullable=False)
    step_order = Column(Integer, nullable=False)
    owner = Column(String(255), nullable=True)
    execution_time = Column(Float, default=0.0)
    waiting_time = Column(Float, default=0.0)
    adds_value = Column(Boolean, default=True)
    has_rework = Column(Boolean, default=False)
    approvals = Column(Integer, default=0)
    notes = Column(Text, nullable=True)

    process = relationship("Process", back_populates="steps")


class ProcessInterview(Base):
    __tablename__ = "process_interviews"
    process = relationship("Process", back_populates="insights")
