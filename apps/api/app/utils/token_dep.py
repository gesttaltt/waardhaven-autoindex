from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.config import settings
from ..models.user import User
import os

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_user_optional(token: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """Optional authentication - returns None if no token provided, useful for backward compatibility"""
    if not token:
        # Check if auth should be enforced
        if os.getenv("REQUIRE_AUTH", "false").lower() == "true":
            raise HTTPException(status_code=401, detail="Authentication required")
        return None
    
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(User).get(user_id)
        return user
    except (JWTError, AttributeError):
        return None
