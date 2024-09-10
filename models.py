from sqlalchemy import Column, Integer, String, Float, Date
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

    body_weight = Column(Float, nullable=True)
    bmr = Column(Float, nullable=True)
    hydration_level = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)