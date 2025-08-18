# Security Best Practices

## Overview

Security is implemented at multiple layers to protect user data, prevent attacks, and ensure system integrity.

## Security Architecture

```
┌─────────────────────────────────────────┐
│         Network Security                 │
│     (HTTPS, CORS, Rate Limiting)        │
├─────────────────────────────────────────┤
│       Authentication & Authorization      │
│      (JWT, OAuth, Role-Based Access)     │
├─────────────────────────────────────────┤
│          Input Validation                │
│    (Sanitization, Type Checking)         │
├─────────────────────────────────────────┤
│           Data Protection                │
│     (Encryption, Secure Storage)         │
└─────────────────────────────────────────┘
```

## Authentication Security

### JWT Token Security

```typescript
// Token generation with security best practices
export class TokenManager {
  private readonly TOKEN_EXPIRY = 3600; // 1 hour
  private readonly REFRESH_TOKEN_EXPIRY = 604800; // 7 days
  
  generateTokens(userId: string): AuthTokens {
    const payload = {
      sub: userId,
      iat: Date.now(),
      exp: Date.now() + (this.TOKEN_EXPIRY * 1000),
      jti: crypto.randomUUID(), // Unique token ID for revocation
    };
    
    const accessToken = jwt.sign(payload, process.env.JWT_SECRET!, {
      algorithm: 'HS256',
      issuer: 'waardhaven.com',
      audience: 'waardhaven-api',
    });
    
    const refreshToken = jwt.sign(
      { ...payload, exp: Date.now() + (this.REFRESH_TOKEN_EXPIRY * 1000) },
      process.env.JWT_REFRESH_SECRET!,
      { algorithm: 'HS256' }
    );
    
    return { accessToken, refreshToken };
  }
  
  verifyToken(token: string): JWTPayload {
    try {
      return jwt.verify(token, process.env.JWT_SECRET!, {
        algorithms: ['HS256'],
        issuer: 'waardhaven.com',
        audience: 'waardhaven-api',
      });
    } catch (error) {
      throw new AuthenticationError('Invalid token');
    }
  }
}
```

### Secure Password Handling

```typescript
// Password hashing and validation
import bcrypt from 'bcrypt';

export class PasswordService {
  private readonly SALT_ROUNDS = 12;
  private readonly MIN_LENGTH = 8;
  private readonly REQUIREMENTS = {
    uppercase: /[A-Z]/,
    lowercase: /[a-z]/,
    number: /[0-9]/,
    special: /[!@#$%^&*]/,
  };
  
  async hashPassword(password: string): Promise<string> {
    this.validatePasswordStrength(password);
    return bcrypt.hash(password, this.SALT_ROUNDS);
  }
  
  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }
  
  validatePasswordStrength(password: string): void {
    const errors: string[] = [];
    
    if (password.length < this.MIN_LENGTH) {
      errors.push(`Password must be at least ${this.MIN_LENGTH} characters`);
    }
    
    if (!this.REQUIREMENTS.uppercase.test(password)) {
      errors.push('Password must contain an uppercase letter');
    }
    
    if (!this.REQUIREMENTS.lowercase.test(password)) {
      errors.push('Password must contain a lowercase letter');
    }
    
    if (!this.REQUIREMENTS.number.test(password)) {
      errors.push('Password must contain a number');
    }
    
    if (!this.REQUIREMENTS.special.test(password)) {
      errors.push('Password must contain a special character');
    }
    
    if (errors.length > 0) {
      throw new ValidationError('Password does not meet requirements', errors);
    }
  }
}
```

### Session Management

```typescript
// Secure session handling
export class SessionManager {
  private sessions = new Map<string, Session>();
  
  createSession(userId: string, userAgent: string, ip: string): string {
    const sessionId = crypto.randomUUID();
    const session: Session = {
      id: sessionId,
      userId,
      userAgent,
      ip,
      createdAt: Date.now(),
      lastActivity: Date.now(),
      expiresAt: Date.now() + (3600 * 1000), // 1 hour
    };
    
    this.sessions.set(sessionId, session);
    this.scheduleCleanup(sessionId);
    
    return sessionId;
  }
  
  validateSession(sessionId: string, userAgent: string, ip: string): boolean {
    const session = this.sessions.get(sessionId);
    
    if (!session) return false;
    if (session.expiresAt < Date.now()) {
      this.sessions.delete(sessionId);
      return false;
    }
    
    // Check for session hijacking
    if (session.userAgent !== userAgent || session.ip !== ip) {
      this.logSecurityEvent('POSSIBLE_SESSION_HIJACK', { sessionId, userAgent, ip });
      this.sessions.delete(sessionId);
      return false;
    }
    
    // Update last activity
    session.lastActivity = Date.now();
    return true;
  }
}
```

## Input Validation & Sanitization

### Request Validation

```typescript
// Input validation middleware
import { z } from 'zod';
import DOMPurify from 'isomorphic-dompurify';

export const validateRequest = (schema: z.ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const validated = await schema.parseAsync(req.body);
      
      // Sanitize string inputs
      req.body = sanitizeObject(validated);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors,
        });
      }
      next(error);
    }
  };
};

function sanitizeObject(obj: any): any {
  if (typeof obj === 'string') {
    return DOMPurify.sanitize(obj, { ALLOWED_TAGS: [] });
  }
  
  if (Array.isArray(obj)) {
    return obj.map(sanitizeObject);
  }
  
  if (obj && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      acc[key] = sanitizeObject(obj[key]);
      return acc;
    }, {} as any);
  }
  
  return obj;
}

// Usage example
const loginSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(128),
});

router.post('/login', validateRequest(loginSchema), loginHandler);
```

### SQL Injection Prevention

```typescript
// Safe database queries using parameterized statements
export class DatabaseService {
  async getUserByEmail(email: string): Promise<User | null> {
    // Safe: Uses parameterized query
    const query = 'SELECT * FROM users WHERE email = $1';
    const result = await this.db.query(query, [email]);
    return result.rows[0] || null;
  }
  
  async searchAssets(searchTerm: string): Promise<Asset[]> {
    // Safe: Validates and escapes search term
    const sanitizedTerm = searchTerm.replace(/[%_]/g, '\\$&');
    const query = 'SELECT * FROM assets WHERE name ILIKE $1';
    const result = await this.db.query(query, [`%${sanitizedTerm}%`]);
    return result.rows;
  }
  
  // Never do this!
  async unsafeQuery(userInput: string) {
    // UNSAFE: Direct string concatenation
    // const query = `SELECT * FROM users WHERE email = '${userInput}'`;
    // return this.db.query(query);
  }
}
```

## XSS Prevention

### Content Security Policy

```typescript
// middleware/security.ts
export function securityHeaders(req: Request, res: Response, next: NextFunction) {
  // Content Security Policy
  res.setHeader(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' https://accounts.google.com",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self'",
      "connect-src 'self' https://api.waardhaven.com",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; ')
  );
  
  // Other security headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  
  next();
}
```

### Safe Rendering

```typescript
// Safe HTML rendering in React
const SafeHtmlComponent: React.FC<{ html: string }> = ({ html }) => {
  const sanitizedHtml = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });
  
  return (
    <div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />
  );
};

// Never render user input directly
const UnsafeComponent: React.FC<{ userInput: string }> = ({ userInput }) => {
  // DON'T DO THIS
  // return <div dangerouslySetInnerHTML={{ __html: userInput }} />;
  
  // DO THIS
  return <div>{userInput}</div>;
};
```

## CSRF Protection

### CSRF Token Implementation

```typescript
// CSRF token generation and validation
import crypto from 'crypto';

export class CSRFProtection {
  private tokens = new Map<string, string>();
  
  generateToken(sessionId: string): string {
    const token = crypto.randomBytes(32).toString('hex');
    this.tokens.set(sessionId, token);
    return token;
  }
  
  validateToken(sessionId: string, token: string): boolean {
    const storedToken = this.tokens.get(sessionId);
    if (!storedToken || storedToken !== token) {
      return false;
    }
    
    // Single use tokens
    this.tokens.delete(sessionId);
    return true;
  }
}

// Middleware
export const csrfProtection = (req: Request, res: Response, next: NextFunction) => {
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
    const token = req.headers['x-csrf-token'] || req.body._csrf;
    
    if (!csrfService.validateToken(req.sessionId, token)) {
      return res.status(403).json({ error: 'Invalid CSRF token' });
    }
  }
  
  next();
};
```

## Rate Limiting

### API Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';

// General rate limiter
export const apiLimiter = rateLimit({
  store: new RedisStore({
    client: redisClient,
    prefix: 'rl:api:',
  }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: 'Too many requests, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

// Strict limiter for auth endpoints
export const authLimiter = rateLimit({
  store: new RedisStore({
    client: redisClient,
    prefix: 'rl:auth:',
  }),
  windowMs: 15 * 60 * 1000,
  max: 5, // 5 attempts per window
  skipSuccessfulRequests: true, // Don't count successful logins
});

// Dynamic rate limiting based on user tier
export const dynamicLimiter = (req: Request, res: Response, next: NextFunction) => {
  const userTier = req.user?.tier || 'free';
  const limits = {
    free: 100,
    pro: 1000,
    enterprise: 10000,
  };
  
  const limiter = rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: limits[userTier],
    keyGenerator: (req) => req.user?.id || req.ip,
  });
  
  limiter(req, res, next);
};
```

## Data Encryption

### Encryption at Rest

```typescript
import crypto from 'crypto';

export class EncryptionService {
  private algorithm = 'aes-256-gcm';
  private key: Buffer;
  
  constructor() {
    this.key = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex');
  }
  
  encrypt(text: string): EncryptedData {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
    };
  }
  
  decrypt(data: EncryptedData): string {
    const decipher = crypto.createDecipheriv(
      this.algorithm,
      this.key,
      Buffer.from(data.iv, 'hex')
    );
    
    decipher.setAuthTag(Buffer.from(data.authTag, 'hex'));
    
    let decrypted = decipher.update(data.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
}
```

## API Security

### API Key Management

```typescript
export class APIKeyService {
  async generateAPIKey(userId: string): Promise<string> {
    const key = crypto.randomBytes(32).toString('hex');
    const hashedKey = await this.hashAPIKey(key);
    
    await this.db.query(
      'INSERT INTO api_keys (user_id, key_hash, created_at) VALUES ($1, $2, $3)',
      [userId, hashedKey, new Date()]
    );
    
    // Return unhashed key only once
    return key;
  }
  
  async validateAPIKey(key: string): Promise<boolean> {
    const hashedKey = await this.hashAPIKey(key);
    
    const result = await this.db.query(
      'SELECT * FROM api_keys WHERE key_hash = $1 AND revoked = false',
      [hashedKey]
    );
    
    if (result.rows.length === 0) {
      return false;
    }
    
    // Update last used
    await this.db.query(
      'UPDATE api_keys SET last_used = $1 WHERE key_hash = $2',
      [new Date(), hashedKey]
    );
    
    return true;
  }
  
  private async hashAPIKey(key: string): Promise<string> {
    return crypto.createHash('sha256').update(key).digest('hex');
  }
}
```

## Security Monitoring

### Audit Logging

```typescript
export class AuditLogger {
  async log(event: SecurityEvent): Promise<void> {
    const logEntry = {
      timestamp: new Date(),
      eventType: event.type,
      userId: event.userId,
      ip: event.ip,
      userAgent: event.userAgent,
      details: event.details,
      severity: event.severity,
    };
    
    // Store in database
    await this.db.query(
      'INSERT INTO audit_logs (data) VALUES ($1)',
      [JSON.stringify(logEntry)]
    );
    
    // Alert on high severity events
    if (event.severity === 'HIGH') {
      await this.alertSecurityTeam(logEntry);
    }
  }
  
  async detectAnomalies(userId: string): Promise<void> {
    const recentLogs = await this.getRecentLogs(userId);
    
    // Check for suspicious patterns
    const failedLogins = recentLogs.filter(log => 
      log.eventType === 'LOGIN_FAILED'
    ).length;
    
    if (failedLogins > 5) {
      await this.log({
        type: 'BRUTE_FORCE_DETECTED',
        userId,
        severity: 'HIGH',
        details: { failedAttempts: failedLogins },
      });
      
      // Temporarily lock account
      await this.lockAccount(userId);
    }
  }
}
```

## Security Checklist

### Frontend Security
- [ ] HTTPS enforced
- [ ] CSP headers configured
- [ ] XSS protection enabled
- [ ] Input sanitization
- [ ] Secure cookie settings
- [ ] No sensitive data in localStorage
- [ ] API keys not exposed
- [ ] Dependencies updated

### Backend Security
- [ ] Authentication required
- [ ] Authorization checks
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] Rate limiting enabled
- [ ] CORS configured
- [ ] Security headers set
- [ ] Error messages sanitized

### Infrastructure Security
- [ ] SSL/TLS certificates
- [ ] Firewall rules
- [ ] Database encryption
- [ ] Backup encryption
- [ ] Access logs enabled
- [ ] Monitoring alerts
- [ ] Incident response plan
- [ ] Regular security audits

## Security Tools

### Dependency Scanning
```bash
# Check for vulnerabilities
npm audit
npm audit fix

# Python dependencies
pip-audit
safety check
```

### Security Testing
```bash
# OWASP ZAP scan
zap-cli quick-scan --self-contained \
  --start-options '-config api.disablekey=true' \
  https://waardhaven.com

# SSL/TLS testing
testssl.sh waardhaven.com
```

## Incident Response

### Security Incident Procedure
1. **Detect** - Monitor alerts and logs
2. **Contain** - Isolate affected systems
3. **Investigate** - Determine scope and impact
4. **Remediate** - Fix vulnerabilities
5. **Recover** - Restore normal operations
6. **Review** - Post-incident analysis

## Best Practices

1. **Defense in Depth** - Multiple security layers
2. **Least Privilege** - Minimal access rights
3. **Fail Secure** - Default to secure state
4. **Security by Design** - Built-in, not added on
5. **Regular Updates** - Keep dependencies current
6. **Security Training** - Educate development team
7. **Code Reviews** - Security-focused reviews
8. **Penetration Testing** - Regular security assessments

## Next Steps

- Review [Troubleshooting Guide](./13-troubleshooting-guide.md)
- Learn about [Performance Optimization](./11-performance-optimization.md)
- Understand [Testing Guide](./09-testing-guide.md)