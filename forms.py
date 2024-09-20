from fastapi import Form, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import re

class LoginForm(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @classmethod
    def as_form(
        cls,
        username: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        password: str = Form(...)
    ) -> 'LoginForm':
        return cls(username=username, email=email, password=password)

class SignUpForm(BaseModel):
    first_name: str
    last_name: str
    gender: str
    age: int
    date_of_birth: date
    address: str
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    body_weight: Optional[float] = None  
    height: Optional[float] = None  
    bmr: Optional[float] = None  
    hydration_level: Optional[float] = None  
    muscle_mass: Optional[float] = None  
    injury_history: Optional[str] = None  
    medical_condition: Optional[str] = None 
    allergies: Optional[str] = None  
    sports_playing: Optional[str] = None
    position: Optional[str] = None
    contact_number: str
    emergency_contact: str
    emergency_contact_number: str
    training_goal: Optional[str] = None 
    photo: Optional[str] = None 
    registration_date: Optional[date] = None

    @classmethod
    def as_form(
        cls,
        first_name: str = Form(...),
        last_name: str = Form(...),
        gender: str = Form(...),
        age: int = Form(...),
        date_of_birth: date = Form(...),
        address: str = Form(...),
        username: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        body_weight: Optional[float] = Form(None),
        height: Optional[float] = Form(None),
        bmr: Optional[float] = Form(None),
        hydration_level: Optional[float] = Form(None),
        muscle_mass: Optional[float] = Form(None),
        injury_history: Optional[str] = Form(None),
        medical_condition: Optional[str] = Form(None),
        allergies: Optional[str] = Form(None),
        sports_playing: str = Form(...),
        position: str = Form(...),
        contact_number: str = Form(...),
        emergency_contact: str = Form(...),
        emergency_contact_number: str = Form(...),
        training_goal: Optional[str] = Form(None),
        photo: Optional[str] = Form(None),
        registration_date: Optional[date] = Form(None)
    ) -> 'SignUpForm':
        form = cls(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            age=age,
            date_of_birth=date_of_birth,
            address=address,
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            body_weight=body_weight,
            height=height,
            bmr=bmr,
            hydration_level=hydration_level,
            muscle_mass=muscle_mass,
            injury_history=injury_history,
            medical_condition=medical_condition,
            allergies=allergies,
            sports_playing=sports_playing,
            position=position,
            contact_number=contact_number,
            emergency_contact=emergency_contact,
            emergency_contact_number=emergency_contact_number,
            training_goal=training_goal,
            photo=photo,
            registration_date=registration_date or date.today()
        )

        if form.password != form.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        return form
