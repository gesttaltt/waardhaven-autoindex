# Authentication Router

## Overview
Handles user authentication, registration, and token management.

## Location
`apps/api/app/routers/auth.py`

## Endpoints

### POST /api/v1/auth/register
- User registration with email and password
- Password strength validation
- Password hashing with bcrypt
- Returns JWT access token

### POST /api/v1/auth/login
- User authentication with email/password
- Password verification against hash
- JWT token generation
- Returns access token

### POST /api/v1/auth/google
- Google OAuth authentication
- Creates account if user doesn't exist
- Links existing accounts to Google
- Returns JWT access token

### GET /api/v1/auth/me
- Get current authenticated user information
- Requires valid JWT token
- Returns user profile (id, email, is_google_user, created_at)

### POST /api/v1/auth/refresh
- Refresh JWT access token for current user
- Requires valid existing token
- Returns new access token
- Extends session without re-login

### POST /api/v1/auth/logout
- User logout endpoint
- Token invalidation handled client-side
- Returns success message

## Authentication Flow

1. **Registration**
   - Validate user input (email format, password strength)
   - Check for existing user with same email
   - Hash password with bcrypt
   - Create user record in database
   - Generate JWT token with user ID
   - Return access token

2. **Login**
   - Verify email/password credentials
   - Check password hash with bcrypt
   - Generate JWT token with user ID
   - Return access token to client

3. **Google OAuth**
   - Verify Google token (handled client-side)
   - Check if user exists by email
   - Create new user if doesn't exist
   - Link existing user to Google if needed
   - Generate JWT token

4. **Protected Routes**
   - Extract Bearer token from Authorization header
   - Verify JWT signature using secret key
   - Decode user ID from token payload
   - Fetch user from database
   - Grant access to resource

5. **Token Refresh**
   - Validate current token
   - Generate new token with same user ID
   - Return refreshed access token

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