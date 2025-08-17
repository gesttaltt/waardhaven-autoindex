# Token Dependencies

## Overview
FastAPI dependency functions for JWT token validation and user authentication.

## Location
`apps/api/app/utils/token_dep.py`

## Purpose
Provides reusable dependencies for protecting API endpoints with authentication.

## Core Dependencies

### get_current_user
- Extracts JWT from header
- Validates token signature
- Decodes user information
- Returns user object
- Raises 401 if invalid

### require_admin
- Checks user role
- Validates admin privileges
- Denies non-admin access
- Used for admin endpoints

### optional_user
- Allows anonymous access
- Returns user if authenticated
- Returns None if not
- Used for public endpoints

## Usage in Routers

```python
from app.utils.token_dep import get_current_user

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    return {"user": current_user.email}
```

## Token Validation

### Validation Steps
1. Extract Authorization header
2. Check Bearer scheme
3. Verify JWT signature
4. Check expiration
5. Extract user claims
6. Load user from database

### Error Handling
- Missing token: 401
- Invalid token: 401
- Expired token: 401
- User not found: 404

## Security Features
- Signature verification
- Expiration checking
- User validation
- Role-based access
- Audit logging

## Dependencies
- PyJWT library
- FastAPI Depends
- Database session
- User model