from fastapi import Form, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import re

class TrainerSignUpForm(BaseModel):
    first_name: str
    last_name: str
    gender: str
    email: EmailStr
    username: str
    password: str
    confirm_password: str
    date_of_birth: date
    specialties: Optional[str] = None 
    experience: Optional[str] = None  
    contact_number: Optional[str] = None  
    photo: Optional[str] = None 

    @classmethod
    def as_form(
        cls,
        first_name: str = Form(...),
        last_name: str = Form(...),
        gender: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        username: str = Form(...),
        date_of_birth: date = Form(...),
        specialties: Optional[str] = Form(None),  
        experience: Optional[str] = Form(None),  
        contact_number: Optional[str] = Form(None),  
        photo: Optional[str] = Form(None) 
    ) -> 'TrainerSignUpForm':
        form = cls(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            email=email,
            password=password,
            confirm_password=confirm_password,
            username=username,
            date_of_birth=date_of_birth,
            specialties=specialties,
            experience=experience,
            contact_number=contact_number,
            photo=photo
        )

        # Add validation to ensure passwords match
        if form.password != form.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        # Validate password constraints
        if not re.match(r'^(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', form.password):
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long, contain at least one uppercase letter, and one special character.")

        return form

class TrainerLoginForm(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @classmethod
    def as_form(
        cls,
        username: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        password: str = Form(...)
    ) -> 'TrainerLoginForm':
        return cls(username=username, email=email, password=password)
