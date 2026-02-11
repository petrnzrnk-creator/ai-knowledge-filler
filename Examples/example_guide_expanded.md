---
title: "API Authentication Implementation Guide"
type: guide
domain: api-design
level: intermediate
status: active
version: v1.0
tags: [api, authentication, security, oauth, jwt]
related:
  - "[[API Security Best Practices]]"
  - "[[OAuth 2.0 Flow]]"
created: 2026-02-06
updated: 2026-02-10
---

## Purpose

Comprehensive step-by-step guide for implementing secure API authentication using JWT and OAuth 2.0, from initial design through production deployment.

## Prerequisites

- Basic understanding of HTTP and REST APIs
- Familiarity with authentication vs authorization concepts
- Development environment with HTTPS support
- Database for storing user credentials and tokens

## Authentication Strategy Selection

### Option A: JWT (JSON Web Tokens)

**Best for:**
- Stateless APIs and microservices
- Mobile applications
- Single-page applications (SPAs)
- Systems with high read-to-write ratios

**Trade-offs:**
- ✅ No server-side session storage
- ✅ Scalable across multiple servers
- ✅ Self-contained with claims
- ❌ Cannot revoke until expiration
- ❌ Larger token size in headers

### Option B: OAuth 2.0

**Best for:**
- Third-party integrations
- Social login (Google, GitHub, Facebook)
- Delegated authorization
- Enterprise SSO systems

**Trade-offs:**
- ✅ Industry standard protocol
- ✅ Scoped permissions
- ✅ Token revocation support
- ❌ More complex implementation
- ❌ Requires provider setup

### Decision Matrix

| Requirement | JWT | OAuth 2.0 |
|-------------|-----|-----------|
| **Stateless** | ✅ Yes | ⚠️ Depends |
| **Third-party login** | ❌ No | ✅ Yes |
| **Token revocation** | ❌ No | ✅ Yes |
| **Implementation complexity** | ✅ Low | ❌ High |
| **Scalability** | ✅ High | ✅ High |

## Implementation: JWT Authentication

### Step 1: Setup and Dependencies

**Node.js/Express:**
```javascript
npm install express jsonwebtoken bcryptjs dotenv
```

**Python/Flask:**
```bash
pip install Flask PyJWT bcrypt python-dotenv
```

**Environment Configuration:**
```env
JWT_SECRET=your-super-secret-key-change-in-production
JWT_EXPIRATION=3600  # 1 hour in seconds
REFRESH_TOKEN_EXPIRATION=604800  # 7 days
```

### Step 2: User Registration

**Node.js Implementation:**
```javascript
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

// User registration endpoint
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;

    // Validation
    if (!email || !password || !name) {
      return res.status(400).json({ 
        error: 'Email, password, and name are required' 
      });
    }

    // Check if user exists
    const existingUser = await db.query(
      'SELECT id FROM users WHERE email = ?', 
      [email]
    );
    
    if (existingUser.length > 0) {
      return res.status(409).json({ 
        error: 'User already exists' 
      });
    }

    // Hash password
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // Create user
    const result = await db.query(
      'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
      [email, hashedPassword, name]
    );

    // Generate tokens
    const userId = result.insertId;
    const accessToken = generateAccessToken(userId, email);
    const refreshToken = generateRefreshToken(userId);

    // Store refresh token
    await db.query(
      'INSERT INTO refresh_tokens (user_id, token) VALUES (?, ?)',
      [userId, refreshToken]
    );

    res.status(201).json({
      message: 'User registered successfully',
      accessToken,
      refreshToken,
      user: { id: userId, email, name }
    });

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

**Python/Flask Implementation:**
```python
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validation
    if not all(k in data for k in ['email', 'password', 'name']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check existing user
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 409
    
    # Hash password
    hashed_password = generate_password_hash(
        data['password'], 
        method='pbkdf2:sha256'
    )
    
    # Create user
    new_user = User(
        email=data['email'],
        password=hashed_password,
        name=data['name']
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Generate tokens
    access_token = generate_access_token(new_user.id, new_user.email)
    refresh_token = generate_refresh_token(new_user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': new_user.id,
            'email': new_user.email,
            'name': new_user.name
        }
    }), 201
```

### Step 3: Login Endpoint

**Node.js Implementation:**
```javascript
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validation
    if (!email || !password) {
      return res.status(400).json({ 
        error: 'Email and password are required' 
      });
    }

    // Find user
    const users = await db.query(
      'SELECT id, email, password, name FROM users WHERE email = ?',
      [email]
    );

    if (users.length === 0) {
      return res.status(401).json({ 
        error: 'Invalid credentials' 
      });
    }

    const user = users[0];

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    
    if (!isValidPassword) {
      return res.status(401).json({ 
        error: 'Invalid credentials' 
      });
    }

    // Generate tokens
    const accessToken = generateAccessToken(user.id, user.email);
    const refreshToken = generateRefreshToken(user.id);

    // Store refresh token (replace old ones)
    await db.query(
      'DELETE FROM refresh_tokens WHERE user_id = ?',
      [user.id]
    );
    await db.query(
      'INSERT INTO refresh_tokens (user_id, token) VALUES (?, ?)',
      [user.id, refreshToken]
    );

    // Update last login
    await db.query(
      'UPDATE users SET last_login = NOW() WHERE id = ?',
      [user.id]
    );

    res.json({
      message: 'Login successful',
      accessToken,
      refreshToken,
      user: { 
        id: user.id, 
        email: user.email, 
        name: user.name 
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

### Step 4: Token Generation Functions

**Node.js Implementation:**
```javascript
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

function generateAccessToken(userId, email) {
  const payload = {
    userId,
    email,
    type: 'access'
  };

  return jwt.sign(
    payload,
    process.env.JWT_SECRET,
    { 
      expiresIn: process.env.JWT_EXPIRATION || '1h',
      issuer: 'your-api-name',
      audience: 'your-app'
    }
  );
}

function generateRefreshToken(userId) {
  const payload = {
    userId,
    type: 'refresh'
  };

  return jwt.sign(
    payload,
    process.env.JWT_SECRET,
    { 
      expiresIn: process.env.REFRESH_TOKEN_EXPIRATION || '7d',
      issuer: 'your-api-name',
      audience: 'your-app'
    }
  );
}
```

### Step 5: Authentication Middleware

**Node.js Implementation:**
```javascript
function authenticateToken(req, res, next) {
  // Get token from header
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ 
      error: 'Access token required' 
    });
  }

  try {
    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET, {
      issuer: 'your-api-name',
      audience: 'your-app'
    });

    // Check token type
    if (decoded.type !== 'access') {
      return res.status(401).json({ 
        error: 'Invalid token type' 
      });
    }

    // Attach user info to request
    req.user = {
      userId: decoded.userId,
      email: decoded.email
    };

    next();

  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ 
        error: 'Token expired',
        code: 'TOKEN_EXPIRED'
      });
    }
    
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ 
        error: 'Invalid token' 
      });
    }

    return res.status(500).json({ 
      error: 'Token verification failed' 
    });
  }
}

// Usage: Protect routes
app.get('/api/protected', authenticateToken, (req, res) => {
  res.json({
    message: 'Access granted',
    user: req.user
  });
});
```

### Step 6: Token Refresh Endpoint

**Node.js Implementation:**
```javascript
app.post('/api/auth/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({ 
        error: 'Refresh token required' 
      });
    }

    // Verify refresh token
    const decoded = jwt.verify(refreshToken, process.env.JWT_SECRET);

    if (decoded.type !== 'refresh') {
      return res.status(401).json({ 
        error: 'Invalid token type' 
      });
    }

    // Check if refresh token exists in database
    const tokens = await db.query(
      'SELECT user_id FROM refresh_tokens WHERE token = ?',
      [refreshToken]
    );

    if (tokens.length === 0) {
      return res.status(401).json({ 
        error: 'Invalid refresh token' 
      });
    }

    // Get user info
    const users = await db.query(
      'SELECT id, email FROM users WHERE id = ?',
      [decoded.userId]
    );

    if (users.length === 0) {
      return res.status(401).json({ 
        error: 'User not found' 
      });
    }

    const user = users[0];

    // Generate new access token
    const newAccessToken = generateAccessToken(user.id, user.email);

    res.json({
      message: 'Token refreshed',
      accessToken: newAccessToken
    });

  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ 
        error: 'Refresh token expired',
        code: 'REFRESH_TOKEN_EXPIRED'
      });
    }
    
    return res.status(401).json({ 
      error: 'Invalid refresh token' 
    });
  }
});
```

### Step 7: Logout Endpoint

**Node.js Implementation:**
```javascript
app.post('/api/auth/logout', authenticateToken, async (req, res) => {
  try {
    const { refreshToken } = req.body;
    const userId = req.user.userId;

    if (refreshToken) {
      // Delete specific refresh token
      await db.query(
        'DELETE FROM refresh_tokens WHERE token = ? AND user_id = ?',
        [refreshToken, userId]
      );
    } else {
      // Delete all refresh tokens for user
      await db.query(
        'DELETE FROM refresh_tokens WHERE user_id = ?',
        [userId]
      );
    }

    res.json({ message: 'Logged out successfully' });

  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({ error: 'Logout failed' });
  }
});
```

## Implementation: OAuth 2.0

### Step 1: Choose OAuth Provider

**Popular providers:**
- **Google** — https://developers.google.com/identity/protocols/oauth2
- **GitHub** — https://docs.github.com/en/developers/apps/building-oauth-apps
- **Auth0** — https://auth0.com/docs/get-started
- **Okta** — https://developer.okta.com/docs/guides/

### Step 2: Register Application

**Google OAuth Example:**

1. Go to Google Cloud Console
2. Create new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Configure redirect URIs: `https://yourdomain.com/auth/callback`
6. Note Client ID and Client Secret

### Step 3: OAuth Flow Implementation

**Node.js with Passport.js:**
```javascript
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: "https://yourdomain.com/auth/google/callback"
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      // Check if user exists
      let user = await db.query(
        'SELECT * FROM users WHERE google_id = ?',
        [profile.id]
      );

      if (user.length === 0) {
        // Create new user
        const result = await db.query(
          'INSERT INTO users (google_id, email, name, avatar) VALUES (?, ?, ?, ?)',
          [profile.id, profile.emails[0].value, profile.displayName, profile.photos[0].value]
        );
        user = { id: result.insertId, email: profile.emails[0].value };
      } else {
        user = user[0];
      }

      return done(null, user);

    } catch (error) {
      return done(error, null);
    }
  }
));

// Routes
app.get('/auth/google',
  passport.authenticate('google', { scope: ['profile', 'email'] })
);

app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    // Generate JWT for the authenticated user
    const token = generateAccessToken(req.user.id, req.user.email);
    res.redirect(`/auth/success?token=${token}`);
  }
);
```

## Security Best Practices

### 1. HTTPS Only

**Never use HTTP for authentication:**
```javascript
// Express: Force HTTPS
app.use((req, res, next) => {
  if (req.headers['x-forwarded-proto'] !== 'https' && process.env.NODE_ENV === 'production') {
    return res.redirect('https://' + req.headers.host + req.url);
  }
  next();
});
```

### 2. Strong Password Requirements

**Implement password validation:**
```javascript
function validatePassword(password) {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  return password.length >= minLength && 
         hasUpperCase && 
         hasLowerCase && 
         hasNumbers && 
         hasSpecialChar;
}
```

### 3. Rate Limiting

**Prevent brute force attacks:**
```javascript
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 requests per window
  message: 'Too many login attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/api/auth/login', loginLimiter, loginHandler);
```

### 4. Secure Token Storage

**Client-side best practices:**

**❌ Don't:**
```javascript
// localStorage is vulnerable to XSS
localStorage.setItem('token', accessToken);
```

**✅ Do:**
```javascript
// Use httpOnly cookies
res.cookie('accessToken', token, {
  httpOnly: true,
  secure: true, // HTTPS only
  sameSite: 'strict',
  maxAge: 3600000 // 1 hour
});
```

### 5. CORS Configuration

**Restrict origins:**
```javascript
const cors = require('cors');

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS.split(','),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

## Troubleshooting

### Issue 1: "Token Expired" on Valid Token

**Cause:** Server time out of sync

**Solution:**
```bash
# Synchronize server time
sudo ntpdate -s time.nist.gov

# Or use NTP service
sudo systemctl enable ntp
sudo systemctl start ntp
```

### Issue 2: CORS Errors in Browser

**Symptoms:**
```
Access to fetch at 'https://api.example.com/auth/login' from origin 'https://app.example.com' 
has been blocked by CORS policy
```

**Solution:**
```javascript
// Add proper CORS headers
app.use(cors({
  origin: 'https://app.example.com',
  credentials: true
}));

// Ensure preflight requests handled
app.options('*', cors());
```

### Issue 3: Password Hash Verification Fails

**Cause:** Bcrypt rounds mismatch or encoding issues

**Debug:**
```javascript
console.log('Stored hash:', user.password);
console.log('Provided password:', password);
console.log('Hash length:', user.password.length); // Should be 60 for bcrypt

// Test with known value
const testHash = await bcrypt.hash('test123', 10);
const testResult = await bcrypt.compare('test123', testHash);
console.log('Test result:', testResult); // Should be true
```

### Issue 4: JWT Verification Fails

**Common causes:**
- Wrong secret key
- Token modified in transit
- Clock skew

**Debug:**
```javascript
try {
  const decoded = jwt.verify(token, process.env.JWT_SECRET, {
    clockTolerance: 60 // Allow 60 seconds of clock skew
  });
  console.log('Decoded:', decoded);
} catch (error) {
  console.error('Verification error:', error.name, error.message);
  
  // Decode without verification to see contents
  const decoded = jwt.decode(token);
  console.log('Token contents:', decoded);
}
```

### Issue 5: Refresh Token Not Found in Database

**Cause:** Token rotation or cleanup job removed it

**Solution:**
```javascript
// Implement token cleanup with grace period
await db.query(`
  DELETE FROM refresh_tokens 
  WHERE created_at < DATE_SUB(NOW(), INTERVAL 8 DAY)
`);

// Keep tokens for 7 days + 1 day grace period
```

## Common Pitfalls

### 1. Storing Passwords in Plain Text

**❌ Never do this:**
```javascript
await db.query('INSERT INTO users (password) VALUES (?)', [password]);
```

**✅ Always hash:**
```javascript
const hashedPassword = await bcrypt.hash(password, 10);
await db.query('INSERT INTO users (password) VALUES (?)', [hashedPassword]);
```

### 2. Using Weak JWT Secrets

**❌ Weak secret:**
```javascript
const secret = 'mysecret';
```

**✅ Strong secret:**
```javascript
// Generate with:
require('crypto').randomBytes(64).toString('hex');
// Store in environment variable
```

### 3. Not Validating Input

**❌ Trusting user input:**
```javascript
app.post('/login', (req, res) => {
  const user = db.query('SELECT * FROM users WHERE email = ' + req.body.email);
});
```

**✅ Validate and sanitize:**
```javascript
const { body, validationResult } = require('express-validator');

app.post('/login', [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 })
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  // Proceed with authentication
});
```

### 4. Token Never Expires

**❌ No expiration:**
```javascript
const token = jwt.sign(payload, secret);
```

**✅ Set expiration:**
```javascript
const token = jwt.sign(payload, secret, { expiresIn: '1h' });
```

### 5. Not Implementing Token Refresh

**❌ Long-lived access tokens:**
```javascript
const token = jwt.sign(payload, secret, { expiresIn: '30d' });
```

**✅ Short access token + refresh token:**
```javascript
const accessToken = jwt.sign(payload, secret, { expiresIn: '15m' });
const refreshToken = jwt.sign(payload, secret, { expiresIn: '7d' });
```

## Testing

### Unit Tests

**Testing password hashing:**
```javascript
describe('Password Security', () => {
  it('should hash passwords before storing', async () => {
    const password = 'Test123!@#';
    const hashed = await bcrypt.hash(password, 10);
    
    expect(hashed).not.toBe(password);
    expect(hashed.length).toBe(60); // Bcrypt output length
  });

  it('should verify correct passwords', async () => {
    const password = 'Test123!@#';
    const hashed = await bcrypt.hash(password, 10);
    const isValid = await bcrypt.compare(password, hashed);
    
    expect(isValid).toBe(true);
  });
});
```

**Testing JWT generation:**
```javascript
describe('JWT Token Generation', () => {
  it('should generate valid access token', () => {
    const token = generateAccessToken(1, 'test@example.com');
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    expect(decoded.userId).toBe(1);
    expect(decoded.email).toBe('test@example.com');
    expect(decoded.type).toBe('access');
  });

  it('should reject expired tokens', (done) => {
    const token = jwt.sign(
      { userId: 1 },
      process.env.JWT_SECRET,
      { expiresIn: '1ms' }
    );

    setTimeout(() => {
      expect(() => {
        jwt.verify(token, process.env.JWT_SECRET);
      }).toThrow('jwt expired');
      done();
    }, 100);
  });
});
```

### Integration Tests

**Testing login flow:**
```javascript
describe('POST /api/auth/login', () => {
  it('should return token on valid credentials', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'Test123!@#'
      });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('accessToken');
    expect(response.body).toHaveProperty('refreshToken');
  });

  it('should reject invalid credentials', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'wrongpassword'
      });

    expect(response.status).toBe(401);
    expect(response.body.error).toBe('Invalid credentials');
  });
});
```

## Production Checklist

### Pre-Deployment

- [ ] HTTPS enforced on all endpoints
- [ ] Strong JWT secret generated and stored in environment
- [ ] Password hashing with bcrypt (min 10 rounds)
- [ ] Token expiration configured (access: 15-60 min, refresh: 7 days)
- [ ] Rate limiting enabled on auth endpoints
- [ ] CORS configured with specific origins
- [ ] Input validation on all auth endpoints
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (input sanitization)
- [ ] Refresh token rotation implemented
- [ ] Token stored in httpOnly cookies (not localStorage)
- [ ] Logout invalidates refresh tokens
- [ ] Database indexes on user_id, email, token fields
- [ ] Logging for failed authentication attempts
- [ ] Monitoring alerts configured
- [ ] Security headers configured (HSTS, CSP, etc.)
- [ ] Error messages don't leak sensitive info

### Monitoring

- [ ] Track authentication success/failure rates
- [ ] Monitor token refresh patterns
- [ ] Alert on spike in failed login attempts
- [ ] Log suspicious authentication activity
- [ ] Track token expiration and refresh usage

## Conclusion

Implementing secure API authentication requires careful attention to:

1. **Token Management** — Short-lived access tokens with refresh capability
2. **Password Security** — Strong hashing, validation, and storage
3. **HTTPS Enforcement** — Never transmit credentials over HTTP
4. **Rate Limiting** — Prevent brute force attacks
5. **Input Validation** — Sanitize all user input
6. **Error Handling** — Generic messages, detailed logging

Start with JWT for most use cases. Add OAuth 2.0 when third-party integrations are required.

Security is not a feature — it's a requirement. Test thoroughly, monitor actively, and update regularly.
