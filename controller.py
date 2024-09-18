"""
handles API endpoints related to user authentication
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from db import get_db
from forms import LoginForm, SignUpForm
from fastapi.responses import JSONResponse
from models import Athlete, Trainer
from bcrypt import hashpw, gensalt
from fastapi.templating import Jinja2Templates
from datetime import timedelta, date
from trainers_forms import TrainerSignUpForm, TrainerLoginForm
from auth import SECRET_KEY, ALGORITHM, authenticate_user, create_access_token, get_current_user, get_current_athlete, get_current_trainer
from pydantic import BaseModel
from typing import Optional
from jose import jwt, JWTError
from config import settings 


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
async def login(response: Response, request: Request, form_data: LoginForm = Depends(LoginForm.as_form), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password, role="athlete")
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "form": form_data, "error": "Invalid credentials"})

    access_token = create_access_token(data={"sub": user.username, "role": "athlete"})

    # Debugging: Print the generated token
    print(f"Generated JWT Token for athlete: {access_token}")

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="athlete_access_token",
        value=access_token,
        httponly=True,
        #max_age=2880 * 60,
        #expires=2880 * 60,
        samesite="Lax",
        secure=False 
    )
    return response
    #return RedirectResponse(url="/dashboard", status_code=302)


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
async def trainer_login(request: Request, response = Response, form_data: TrainerLoginForm = Depends(TrainerLoginForm.as_form), db: Session = Depends(get_db)):
    # Authenticate the trainer
    user = authenticate_user(db, form_data.username, form_data.password, role="trainer")

    if not user:
        return templates.TemplateResponse("trainerlogin.html", {"request": request, "form": form_data, "error": "Invalid credentials"})

    # Create the access token if authentication succeeds
    #access_token_expires = timedelta(minutes=30) 
    access_token = create_access_token(data={"sub": user.username, "role": "trainer"})
    
    # Create a redirect response and set the access token in the cookies
    response = RedirectResponse(url="/trainer/dashboard", status_code=302)
    response.set_cookie(
        key="trainer_access_token",
        value=access_token,
        httponly=True,
        #max_age=2880 * 60,
        #expires=2880 * 60,
        samesite="Lax",
        secure=False 
    )
    # Redirect to the trainers dashboard after successful login
    return response

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
        "id": athlete.id,
        "first_name": athlete.first_name,
        "last_name": athlete.last_name,
        "date_of_birth": athlete.date_of_birth,
        "email": athlete.email,
        "body_weight": athlete.body_weight,
        #"height": athlete.height,
        "bmr": athlete.bmr,
        "age": athlete.age,
        "hydration_level": athlete.hydration_level,
        "muscle_mass": athlete.muscle_mass,
        "residence": athlete.residence,
        "gender": athlete.gender,
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

# Endpoint for Athlete dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def athlete_dashboard(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("athlete_access_token")
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Unauthorized: No token found")
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role != "athlete":
            raise HTTPException(status_code=401, detail="Unauthorized")
    
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch the current athlete's data based on the username in the token
    athlete = db.query(Athlete).filter(Athlete.username == username).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    # Render the dashboard HTML template for athletes
    return templates.TemplateResponse("dashboard.html", {"request": request, "athlete": athlete})

@router.get("/download-stats", response_class=Response)
async def download_stats(request: Request, db: Session = Depends(get_db), current_athlete: Athlete = Depends(get_current_athlete)):
    # Create a PDF buffer in memory
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Write content on the PDF
    pdf.drawString(100, 750, f"First Name: {current_athlete.first_name}")
    pdf.drawString(100, 730, f"Last Name: {current_athlete.last_name}")
    pdf.drawString(100, 710, f"Date of Birth: {current_athlete.date_of_birth}")
    pdf.drawString(100, 690, f"Email: {current_athlete.email}")
    pdf.drawString(100, 670, f"Body Weight: {current_athlete.body_weight}")
    pdf.drawString(100, 650, f"BMR: {current_athlete.bmr}")
    pdf.drawString(100, 630, f"Age: {current_athlete.age}")
    pdf.drawString(100, 610, f"Hydration Level: {current_athlete.hydration_level}")
    pdf.drawString(100, 590, f"Muscle Mass: {current_athlete.muscle_mass}")
    pdf.drawString(100, 570, f"Residence: {current_athlete.residence}")
    pdf.drawString(100, 550, f"Gender: {current_athlete.gender}")

    # Finalize the PDF
    pdf.showPage()
    pdf.save()

    # Get the value of the BytesIO buffer and close the buffer
    pdf_data = buffer.getvalue()
    buffer.close()

    # Send the response as a PDF download
    headers = {
        'Content-Disposition': 'attachment; filename="athlete_stats.pdf"'
    }
    return Response(content=pdf_data, media_type="application/pdf", headers=headers)

# Trainer Dashboard Route endpoint 
@router.get("/trainer/dashboard", response_class=HTMLResponse)
async def trainer_dashboard(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("trainer_access_token")
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Unauthorized: No token found")
  
    try:
        # Decode the JWT token from the cookie
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the username and role from the token payload
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        # Ensure the role is "trainer"
        if username is None or role != "trainer":
            raise HTTPException(status_code=401, detail="Unauthorized")
    
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch the current trainer's data based on the username from the token
    trainer = db.query(Trainer).filter(Trainer.username == username).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    # Fetch the list of athletes for the trainer to view and manage
    athletes = db.query(Athlete).all()

    # Render the trainer dashboard template with the trainer's and athletes' data
    return templates.TemplateResponse("trainer_dashboard.html", {
        "request": request,
        "trainer": trainer,
        "athletes": athletes
    })

# Route for trainers to view and update specific athlete information
@router.get("/trainer/athlete/{athlete_id}", response_class=HTMLResponse)
async def view_athlete(
    athlete_id: int, 
    request: Request, 
    db: Session = Depends(get_db), 
    current_trainer: Trainer = Depends(get_current_trainer)
):
    # Fetch the athlete by ID
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()

    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    # Return the template for viewing/updating athlete information
    return templates.TemplateResponse("view_athlete.html", {
        "request": request,
        "athlete": athlete
    })


# Route for handling the update logic
@router.post("/trainer/athlete/{athlete_id}/update")
async def update_athlete(athlete_id: int, first_name: str = Form(...), last_name: str = Form(...), email: str = Form(...), body_weight: float = Form(...), db: Session = Depends(get_db), current_trainer: Trainer = Depends(get_current_trainer)):
    # Fetch the athlete by ID
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()

    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    # Update athlete's information
    athlete.first_name = first_name
    athlete.last_name = last_name
    athlete.email = email
    athlete.body_weight = body_weight

    # Commit changes to the database
    db.commit()

    # Redirect back to the trainer dashboard after update
    return RedirectResponse(url="/trainer/dashboard", status_code=302)
