# JWT Authentication

## Overview
JSON Web Token based authentication system for secure user access.

## Implementation

### Token Generation
- HS256 algorithm
- Secret key signing
- Configurable expiration
- Payload encryption

### Token Structure
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1234567890,
  "iat": 1234567800
}
```

### Token Validation
- Signature verification
- Expiration check
- Issuer validation
- Audience verification

## Authentication Flow

### Login Process
1. User submits credentials
2. Server validates password
3. Generate JWT token
4. Return token to client
5. Client stores token

### Request Authentication
1. Client sends token in header
2. Server extracts token
3. Validate token signature
4. Check expiration
5. Extract user info
6. Process request

## Security Features

### Token Security
- Strong secret key
- Short expiration (24h)
- Refresh token support
- Blacklist capability

### Password Security
- Bcrypt hashing
- Salt generation
- Configurable rounds
- Password policies

## Token Management

### Storage
- Client: localStorage/sessionStorage
- Server: No storage (stateless)
- Refresh tokens: Database

### Refresh Strategy
- Refresh before expiry
- Automatic renewal
- Seamless UX
- Security checks

## Headers

### Authorization Header
```
Authorization: Bearer <token>
```

### Custom Headers
- X-Refresh-Token
- X-Token-Expiry
- X-User-Id

## Error Handling

### Token Errors
- Invalid signature: 401
- Expired token: 401
- Malformed token: 400
- Missing token: 401

### Authentication Errors
- Invalid credentials: 401
- Account locked: 403
- User not found: 404

## Frontend Integration

### Token Storage
- Secure storage
- Auto-refresh
- Logout cleanup
- Cross-tab sync

### API Interceptors
- Attach token to requests
- Handle token refresh
- Retry failed requests
- Logout on 401

## Best Practices

### Security
- HTTPS only
- Secure storage
- Token rotation
- Activity monitoring

### Performance
- Token caching
- Minimal payload
- Efficient validation
- Connection pooling

## Configuration

### Environment Variables
- SECRET_KEY
- TOKEN_EXPIRY
- REFRESH_EXPIRY
- ALGORITHM

### Settings
- Token lifetime
- Refresh window
- Max sessions
- Security policies

## Monitoring

### Metrics
- Login attempts
- Token generation
- Validation failures
- Active sessions

### Logging
- Authentication events
- Token operations
- Security violations
- Error tracking

## Recent Updates (2025-08-18)

### ✅ Authentication Integration Fixes
- **Fixed AuthProvider Integration**: Frontend now properly wraps components with AuthProvider
- **Added Missing Endpoints**: `/me`, `/refresh`, `/logout` endpoints now available
- **Google OAuth Support**: Complete Google authentication flow implemented
- **Frontend-Backend Sync**: Auth state properly synchronized between client and server
- **Token Management**: Automatic refresh and proper token storage implemented

### API Endpoints Added
- `GET /api/v1/auth/me` - Get current user information
- `POST /api/v1/auth/refresh` - Refresh access tokens
- `POST /api/v1/auth/logout` - User logout

### Frontend Integration
- **AuthContext**: React Context API managing auth state
- **TokenManager**: Secure token storage and management
- **AuthRepository**: Clean separation of auth logic
- **ProtectedRoute**: Component-level route protection

## Future Enhancements
- Two-factor authentication
- Biometric support
- Advanced session management
- OAuth providers (GitHub, Microsoft)