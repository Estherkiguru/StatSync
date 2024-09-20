from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from db import Base

class Athlete(Base):
    __tablename__ = 'athletes'

    # Personal Information
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    gender = Column(String)
    age = Column(Integer)
    date_of_birth = Column(Date)
    address = Column(String)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # Physical Information
    body_weight = Column(Float, nullable=True)
    Height = Column(Float, nullable=True)
    
    # Performance Metrics
    bmr = Column(Float, nullable=True)
    hydration_level = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)

    # Health Metrics
    injury_history = Column(String, nullable=True)
    medical_condition = Column(String, nullable=True)
    allergies = Column(String, nullable=True)

    #Additional Fields
    sports_playing = Column(String, nullable=True)
    position = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    emergency_contact_number = Column(String, nullable=True)
    training_goal = Column(String, nullable=True)
    registration_date = Column(Date, nullable=True)
    photo = Column(String, nullable=True)


    # Add a foreign key to link to the Trainer model
    trainer_id = Column(Integer, ForeignKey('trainers.id'))

    # Create a relationship with Trainer
    trainer = relationship('Trainer', back_populates='athletes')

class Trainer(Base):
    __tablename__ = 'trainers'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    username = Column(String, unique=True, index=True)
    date_of_birth = Column(Date)
    specialties = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    registration_date = Column(Date, nullable=True)
    photo = Column(String, nullable=True)

    # Create the relationship with Athlete
    athletes = relationship('Athlete', back_populates='trainer')