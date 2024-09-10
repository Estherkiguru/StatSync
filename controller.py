"""
handles API endpoints related to user authentication
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from db import get_db
from forms import LoginForm, SignUpForm
from models import Athlete
from bcrypt import hashpw, gensalt, checkpw
from fastapi.templating import Jinja2Templates
from datetime import date


router = APIRouter()

# Template setup for rendering HTML pages
templates = Jinja2Templates(directory="templates")

# Route for the home page
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for the login page
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login endpoint for an athlete
@router.post("/login")
async def login(request: Request, form_data: LoginForm = Depends(LoginForm.as_form), db: Session = Depends(get_db)):
    if form_data.username:
        query = db.query(Athlete).filter(Athlete.username == form_data.username)
    elif form_data.email:
        query = db.query(Athlete).filter(Athlete.email == form_data.email)
    else:
        raise HTTPException(status_code=400, detail="Username or email required")

    user = query.first()

    if user and checkpw(form_data.password.encode(), user.password.encode()):
        return RedirectResponse(url="/", status_code=302)  # Redirect to home page or a dashboard
    else:
        return templates.TemplateResponse("login.html", {"request": request, "form": form_data, "error": "Invalid credentials"})
# Route for the signup page
@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    # Create an empty form instance with default values
    signup_form = SignUpForm(
        first_name='',
        last_name='',
        gender='',
        age=0,
        date_of_birth=date.today(),
        residence='',
        username='',
        email='example@example.com',
        password='',
        confirm_password=''
    )
    return templates.TemplateResponse("signup.html", {"request": request, "signup_form": signup_form})
   
# Signup endpoint for a new athlete
@router.post('/signup')
async def signup(request: Request, form_data: SignUpForm = Depends(SignUpForm.as_form), db: Session = Depends(get_db)):
    # Check if username or email already exists
    db_athlete = db.query(Athlete).filter(
        (Athlete.username == form_data.username) | (Athlete.email == form_data.email)
    ).first()

    if db_athlete:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "signup_form": form_data,
            "error": "Username or email already registered"
        })
    
    # Check if password matches
    if form_data.password != form_data.confirm_password:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "signup_form": form_data,
            "error": "Passwords do not match"
        })

    # Hash the password for security
    hashed_password = hashpw(form_data.password.encode(), gensalt())

    # Create new athlete instance
    new_athlete = Athlete(
        first_name=form_data.first_name,
        last_name=form_data.last_name,
        gender=form_data.gender,
        age=form_data.age,
        date_of_birth=form_data.date_of_birth,
        residence=form_data.residence,
        username=form_data.username,
        email=form_data.email,
        password=hashed_password.decode()
    )

    db.add(new_athlete)
    db.commit()
    db.refresh(new_athlete)

    # Redirect to login page after successful signup
    return RedirectResponse(url="/login", status_code=302)