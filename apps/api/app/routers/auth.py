from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime
from ..core.database import get_db
from ..models.user import User
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..utils.password_validator import PasswordValidator
from ..core.config import settings

router = APIRouter()

# Explicit OPTIONS handlers for CORS preflight requests
@router.options("/register")
async def options_register():
    """Handle preflight requests for registration endpoint"""
    return Response(status_code=200)

@router.options("/login")
async def options_login():
    """Handle preflight requests for login endpoint"""
    return Response(status_code=200)

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Validate password strength
    is_valid, errors = PasswordValidator.validate(req.password)
    if not is_valid:
        raise HTTPException(
            status_code=400, 
            detail={"message": "Password does not meet security requirements", "errors": errors}
        )
    
    # Check if email already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user with hashed password
    user = User(email=req.email, password_hash=get_password_hash(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)
