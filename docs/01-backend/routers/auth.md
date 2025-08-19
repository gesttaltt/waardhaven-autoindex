# Authentication Router

## Overview
Handles user authentication, registration, and token management.

## Location
`apps/api/app/routers/auth.py`

## Endpoints

### POST /api/v1/auth/register
- User registration
- Password validation with security requirements
- Password hashing with bcrypt
- Returns JWT access token

### POST /api/v1/auth/login
- User authentication
- Password verification
- JWT token generation
- Returns access token

### POST /api/v1/auth/google
- Google OAuth authentication
- Creates new user or links existing account
- Marks user as Google user
- Returns JWT access token

### OPTIONS endpoints
- Handles CORS preflight requests for all auth endpoints
- Returns 200 OK for browser compatibility

## Authentication Flow

1. **Registration**
   - Validate password strength requirements
   - Check for existing user by email
   - Hash password with bcrypt
   - Create user record
   - Generate JWT token

2. **Login**
   - Verify email and password
   - Check password hash
   - Generate JWT token
   - Return token to client

3. **Google OAuth**
   - Receive verified email from frontend
   - Check if user exists
   - Create new user or link existing
   - Mark as Google user (is_google_user flag)
   - Generate JWT token

4. **Protected Routes**
   - Extract token from header
   - Verify JWT signature
   - Decode user information
   - Grant access to resource

## Security Features

### Password Security
- Bcrypt hashing
- Salt generation
- Configurable rounds
- No plain text storage

### JWT Tokens
- HS256 algorithm
- Configurable expiration
- Secret key signing
- Payload encryption

## Token Structure
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1234567890
}
```

## Dependencies
- JWT library
- Bcrypt for passwords
- Pydantic for validation
- SQLAlchemy for database

## Error Handling
- Invalid credentials: 401
- User exists: 400
- Invalid token: 401
- Expired token: 401

## Related Modules
- utils/security.py: Password hashing
- utils/token_dep.py: Token dependencies
- models.py: User model
- schemas.py: Auth schemas