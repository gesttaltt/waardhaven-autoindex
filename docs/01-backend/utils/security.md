# Security Utilities

## Overview
Security helper functions for authentication and password management.

## Location
`apps/api/app/utils/security.py`

## Core Functions

### Password Hashing
- `hash_password(password)` - Creates bcrypt hash
- `verify_password(plain, hashed)` - Validates password
- Salt generation automatic
- Configurable work factor

### JWT Operations
- `create_access_token(data)` - Generate JWT
- `decode_token(token)` - Validate and decode
- Expiration handling
- Secret key management

## Security Configuration
- Bcrypt rounds: 12
- JWT algorithm: HS256
- Token expiry: 24 hours
- Secret key from environment

## Best Practices
- Never store plain passwords
- Use strong secret keys
- Regular key rotation
- Secure token transmission
