from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
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
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire =  datetime.now(timezone.utc)+ expires_delta
    else:
        expire =  datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if role == "athlete":
        user = db.query(Athlete).filter(Athlete.username == username).first()
    elif role == "trainer":
        user = db.query(Trainer).filter(Trainer.username == username).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user


# Dependency to get current authenticated athlete
async def get_current_athlete(current_user: Athlete = Depends(get_current_user)):
    if not isinstance(current_user, Athlete):
        raise HTTPException(status_code=403, detail="Not authorized as athlete")
    return current_user


# Dependency to get current authenticated trainer
async def get_current_trainer(current_user: Trainer = Depends(get_current_user)):
    if not isinstance(current_user, Trainer):
        raise HTTPException(status_code=403, detail="Not authorized as trainer")
    return current_user

