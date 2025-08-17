# Authentication Router

## Overview
Handles user authentication, registration, and token management.

## Location
`apps/api/app/routers/auth.py`

## Endpoints

### POST /api/v1/auth/register
- User registration
- Password hashing with bcrypt
- Returns user info and JWT token

### POST /api/v1/auth/login
- User authentication
- Password verification
- JWT token generation
- Returns access token

### GET /api/v1/auth/me
- Get current user info
- Requires authentication
- Returns user profile

## Authentication Flow

1. **Registration**
   - Validate user input
   - Check for existing user
   - Hash password
   - Create user record
   - Generate JWT token

2. **Login**
   - Verify credentials
   - Check password hash
   - Generate JWT token
   - Return token to client

3. **Protected Routes**
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