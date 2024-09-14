from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from db import Base

class Athlete(Base):
    __tablename__ = 'athletes'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    gender = Column(String)
    age = Column(Integer)
    date_of_birth = Column(Date)
    residence = Column(String)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # Fields to be field out by the Trainer
    body_weight = Column(Float, nullable=True)
    bmr = Column(Float, nullable=True)
    hydration_level = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)

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

    # Create the relationship with Athlete
    athletes = relationship('Athlete', back_populates='trainer')