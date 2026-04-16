from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, nullable=False)
    contact_name = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    contact_email = Column(String(255), nullable=True)

    date = Column(String(20), nullable=False)
    time = Column(String(20), nullable=False)
    duration_minutes = Column(Integer, default=30)

    status = Column(String(50), default="pending")
    notes = Column(Text, nullable=True)

    booked_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)


class CallSession(Base):
    __tablename__ = "call_sessions"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(50), nullable=True)
    agent_id = Column(String(255), nullable=True)

    status = Column(String(50), default="started")
    transcript = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
