"""
handles API endpoints related to user authentication
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from db import get_db
from forms import LoginForm, SignUpForm
from fastapi.responses import JSONResponse
from models import Athlete, Trainer
from bcrypt import hashpw, gensalt
from fastapi.templating import Jinja2Templates
from datetime import timedelta, date
from trainers_forms import TrainerSignUpForm, TrainerLoginForm
from auth import authenticate_user, create_access_token, get_current_user, get_current_athlete, get_current_trainer
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Template setup for rendering HTML pages
templates = Jinja2Templates(directory="templates")

# Route for the home page
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for the Athlete login page
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login endpoint for an athlete
@router.post("/login")
async def login(request: Request, form_data: LoginForm = Depends(LoginForm.as_form), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password, role="athlete")
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "form": form_data, "error": "Invalid credentials"})

    access_token_expires = timedelta(minutes=30) 
    access_token = create_access_token(data={"sub": user.username, "role": "athlete"}, expires_delta=access_token_expires)
    
    # Redirect to athlete dashboard after successful login
    return JSONResponse(
        content={"access_token": access_token, "redirect_url": f"/athlete/{user.id}"},
        status_code=200
    )

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

# Route for the Trainer login page
@router.get("/trainer/login", response_class=HTMLResponse)
async def trainer_login_page(request: Request):
    return templates.TemplateResponse("trainerlogin.html", {"request": request})

# Login endpoint for a trainer
@router.post("/trainer/login")
async def trainer_login(request: Request, form_data: TrainerLoginForm = Depends(TrainerLoginForm.as_form), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password, role="trainer")

    if not user:
        return templates.TemplateResponse("trainerlogin.html", {"request": request, "form": form_data, "error": "Invalid credentials"})

    access_token_expires = timedelta(minutes=30) 
    access_token = create_access_token(data={"sub": user.username, "role": "trainer"}, expires_delta=access_token_expires)
    
    # Redirect to the list of athletes after successful login
    return JSONResponse(
        content={"access_token": access_token, "redirect_url": "/athletes"},
        status_code=200
    )

# Route for the Trainer signup page
@router.get("/trainer/signup", response_class=HTMLResponse)
async def trainer_signup_page(request: Request):
    # Create an empty form instance with default values
    signup_form = TrainerSignUpForm(
        first_name='',
        last_name='',
        gender='',
        date_of_birth=date.today(),
        username='',
        email='example@example.com',
        password='',
        confirm_password=''
    )
    return templates.TemplateResponse("trainersignup.html", {"request": request, "signup_form": signup_form})
  
# Signup endpoint for a new trainer
@router.post('/trainer/signup')
async def trainer_signup(request: Request, form_data: TrainerSignUpForm = Depends(TrainerSignUpForm.as_form), db: Session = Depends(get_db)):
    # Check if username or email already exists
    db_trainer = db.query(Trainer).filter(
        (Trainer.username == form_data.username) | (Trainer.email == form_data.email)
    ).first()

    if db_trainer:
        return templates.TemplateResponse("trainersignup.html", {
            "request": request,
            "signup_form": form_data,
            "error": "Username or email already registered"
        })
    
    # Check if password matches
    if form_data.password != form_data.confirm_password:
        return templates.TemplateResponse("trainersignup.html", {
            "request": request,
            "signup_form": form_data,
            "error": "Passwords do not match"
        })

    # Hash the password for security
    hashed_password = hashpw(form_data.password.encode(), gensalt())

    # Create new trainer instance
    new_trainer = Trainer(
        first_name=form_data.first_name,
        last_name=form_data.last_name,
        gender=form_data.gender,
        date_of_birth=form_data.date_of_birth,
        username=form_data.username,
        email=form_data.email,
        password=hashed_password.decode()
    )

    db.add(new_trainer)
    db.commit()
    db.refresh(new_trainer)

    # Redirect to login page after successful signup
    return RedirectResponse(url="/trainer/login", status_code=302)

# Endpoint for trainers to view a list of athletes data
@router.get("/athletes", response_class=JSONResponse)
async def list_athletes(
    db: Session = Depends(get_db),
    current_user: Trainer = Depends(get_current_trainer)
):
    # Fetch all athletes from the database
    athletes = db.query(Athlete).all()

    if not athletes:
        return JSONResponse(content={"error": "No athletes found"}, status_code=404)

    # Prepare the response data for all athletes
    athlete_list = []
    for athlete in athletes:
        athlete_data = {
            "first_name": athlete.first_name,
            "last_name": athlete.last_name,
            "body_weight": athlete.body_weight,
            # "height": athlete.height,
            "bmr": athlete.bmr,
            "age": athlete.age,
            "hydration_level": athlete.hydration_level,
            "muscle_mass": athlete.muscle_mass,
            "residence": athlete.residence,
            "gender": athlete.gender,
            "date_of_birth": athlete.date_of_birth.strftime("%Y-%m-%d")
        }
        athlete_list.append(athlete_data)

    return JSONResponse(content={"athletes": athlete_list}, status_code=200)

# Endpoint for athletes and trainers to view athlete data
@router.get("/athlete/{athlete_id}", response_class=JSONResponse)
async def get_athlete(
    athlete_id: int,
    db: Session = Depends(get_db), 
    current_user: Athlete = Depends(get_current_athlete) 
):
    athlete = db.query(Athlete).filter_by(id=athlete_id).first()

    if not athlete:
        return JSONResponse(content={"error": "Athlete not found"}, status_code=404)

    if current_user.id != athlete.id:
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)

    return {
        "first_name": athlete.first_name,
        "last_name": athlete.last_name,
        "body_weight": athlete.body_weight,
        #"height": athlete.height,
        "bmr": athlete.bmr,
        "age": athlete.age,
        "hydration_level": athlete.hydration_level,
        "muscle_mass": athlete.muscle_mass,
        "residence": athlete.residence,
        "gender": athlete.gender,
        "date_of_birth": athlete.date_of_birth
    }

# Define the Pydantic model for the request body
class AthleteUpdate(BaseModel):
    body_weight: Optional[float] = None
    bmr: Optional[float] = None
    hydration_level: Optional[float] = None
    muscle_mass: Optional[float] = None


# Endpoint for updating athlete's data
@router.put("/athlete/{athlete_id}", response_class=JSONResponse)
async def update_athlete(
    athlete_id: int,
    athlete_data: AthleteUpdate,  # Pydantic model for validation
    db: Session = Depends(get_db),
    current_trainer: Trainer = Depends(get_current_trainer)  # Authenticate the trainer
):
    athlete = db.query(Athlete).filter_by(id=athlete_id).first()

    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    # Update athlete's data with the provided information
    if athlete_data.body_weight is not None:
        athlete.body_weight = athlete_data.body_weight
    if athlete_data.bmr is not None:
        athlete.bmr = athlete_data.bmr
    if athlete_data.hydration_level is not None:
        athlete.hydration_level = athlete_data.hydration_level
    if athlete_data.muscle_mass is not None:
        athlete.muscle_mass = athlete_data.muscle_mass

# Save changes to the database
    db.commit()
    db.refresh(athlete)

    return {
        "message": "Athlete updated successfully",
        "athlete": {
            "first_name": athlete.first_name,
            "last_name": athlete.last_name,
            "body_weight": athlete.body_weight,
            "bmr": athlete.bmr,
            "age": athlete.age,
            "hydration_level": athlete.hydration_level,
            "muscle_mass": athlete.muscle_mass,
            "residence": athlete.residence,
            "gender": athlete.gender,
            "date_of_birth": athlete.date_of_birth
        }
    }
 