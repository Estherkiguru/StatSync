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
    password: str
    confirm_password: str
    username: str
    date_of_birth: date

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
        date_of_birth: date = Form(...)
    ) -> 'TrainerSignUpForm':
        form = cls(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            email=email,
            password=password,
            confirm_password=confirm_password,
            username=username,
            date_of_birth=date_of_birth
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
