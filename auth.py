from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext

from db import get_db
from models import Athlete, Trainer
from config import settings

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for JWT token generation
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Utility function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Utility function to hash password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Utility function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})

    # Generate the encoded JWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# Utility function to authenticate user (athlete or trainer)
def authenticate_user(db: Session, username: str, password: str, role: str):
    if role == "athlete":
        user = db.query(Athlete).filter(Athlete.username == username).first()
    elif role == "trainer":
        user = db.query(Trainer).filter(Trainer.username == username).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    if not user or not verify_password(password, user.password):
        return False
    return user


# Dependency to get current user based on JWT token
async def get_current_user(request: Request, role_type: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get the token from the cookies
    token_key = "athlete_access_token" if role_type == "athlete" else "trainer_access_token"
    token = request.cookies.get(token_key)

    if not token:
        print("No access token found in cookies.")
        raise credentials_exception
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Extract user data
        username: str = payload.get("sub")
        role: str = payload.get("role")


        # Debugging: Print out the extracted data
        print(f"Decoded JWT - Username: {username}, Role: {role}")

        if username is None or role is None or role != role_type:
            raise credentials_exception
        return username, role
  
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise credentials_exception

# Dependency to get current authenticated athlete
async def get_current_athlete(request: Request, db: Session = Depends(get_db)):
    # Get the username and role from the athlete JWT token
    username, role = await get_current_user(request, "athlete", db)

    
    # Ensure the user is an athlete
    if role != "athlete":
        raise HTTPException(status_code=403, detail="Not authorized as athlete")

    # Fetch the athlete from the database using the username
    athlete = db.query(Athlete).filter(Athlete.username == username).first()
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    return athlete


# Dependency to get current authenticated trainer
async def get_current_trainer(request: Request, db: Session = Depends(get_db)):
    # Get username and role from JWT token
    username, role = await get_current_user(request, "trainer", db)

    # Ensure the user is a trainer
    if role != "trainer":
        raise HTTPException(status_code=403, detail="Not authorized as trainer")

    # Fetch the trainer's data from the database
    trainer = db.query(Trainer).filter(Trainer.username == username).first()
    
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    return trainer

