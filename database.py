from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Create database engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Define models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin' or staff role
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(DateTime)
    contact_number = Column(String)
    address = Column(String)
    medical_history = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    appointments = relationship("Appointment", back_populates="patient")

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('users.id'))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String)  # 'scheduled', 'completed', 'cancelled'
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient", back_populates="appointments")

class Inventory(Base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    unit = Column(String)
    unit_price = Column(Float)
    reorder_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String)

# Create all tables
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
