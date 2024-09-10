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
    residence: str
    username: str
    email: EmailStr
    password: str
    confirm_password: str

    @classmethod
    def as_form(
        cls,
        first_name: str = Form(...),
        last_name: str = Form(...),
        gender: str = Form(...),
        age: int = Form(...),
        date_of_birth: date = Form(...),
        residence: str = Form(...),
        username: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...)
    ) -> 'SignUpForm':
        form = cls(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            age=age,
            date_of_birth=date_of_birth,
            residence=residence,
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        )

        # Add validation to ensure passwords match
        if form.password != form.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        # Validate password constraints
        if not re.match(r'^(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', form.password):
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long, contain at least one uppercase letter, and one special character.")

        return form
