# Authentication & Testing Implementation Plan

## Phase 1: User Authentication System

### Backend Changes:
1. **Update User Model** (app/models.py)
   - Add password_hash field
   - Add created_at, updated_at timestamps
   - Add email verification fields

2. **Authentication Endpoints** (app/api/auth.py)
   - POST /auth/register - Create new user account
   - POST /auth/login - Authenticate and return JWT token
   - POST /auth/refresh - Refresh expired token
   - POST /auth/logout - Invalidate token
   - GET /auth/me - Get current user info

3. **JWT Implementation**
   - Use python-jose for JWT handling
   - Access tokens (15 min expiry)
   - Refresh tokens (7 days expiry)
   - Store refresh tokens in database

4. **Authentication Middleware**
   - Create dependency for protecting routes
   - Add user context to requests
   - Handle token validation

### Frontend Changes:
1. **Auth Context & Provider**
   - Global auth state management
   - Token storage (localStorage/sessionStorage)
   - Auto-refresh logic

2. **Auth Components**
   - SignIn page with email/password
   - SignUp page with validation
   - Protected route wrapper
   - User menu with logout

3. **API Client Updates**
   - Add auth headers to all requests
   - Handle 401 responses
   - Token refresh interceptor

## Phase 2: Comprehensive Test Suite

### Backend Tests (pytest):
1. **Unit Tests**
   - Model tests (user, league, draft, player)
   - Service tests (pool division, sleeper API)
   - Schema validation tests

2. **API Tests**
   - Authentication endpoints
   - League management
   - Draft operations
   - Player endpoints

3. **Integration Tests**
   - Complete draft flow
   - WebSocket connections
   - Database transactions

### Frontend Tests (Jest + RTL):
1. **Component Tests**
   - Auth forms (login/signup)
   - Draft room interactions
   - League dashboard
   - Player selection

2. **Hook Tests**
   - useAuth hook
   - useWebSocket hook
   - API hooks

3. **Integration Tests**
   - Full auth flow
   - Draft simulation
   - Navigation flows

### Test Infrastructure:
1. **Test Database**
   - Separate SQLite for tests
   - Fixtures for common data
   - Reset between tests

2. **Mocking**
   - Mock Sleeper API responses
   - Mock WebSocket for frontend
   - Mock auth for protected routes

3. **CI/CD Integration**
   - Run tests on PR
   - Coverage requirements (80%+)
   - Test reports in GitHub

## Phase 3: Deployment Preparation

### Environment Setup:
1. **Environment Variables**
   - JWT_SECRET_KEY
   - DATABASE_URL
   - FRONTEND_URL
   - API_KEYS

2. **Docker Configuration**
   - Dockerfile for backend
   - Dockerfile for frontend
   - docker-compose for local dev

3. **Deployment Options**
   - Heroku (quick setup)
   - AWS (EC2 + RDS)
   - Vercel (frontend) + Railway (backend)

### Demo Requirements:
1. **Sample Data**
   - Pre-populated leagues
   - Demo accounts
   - Completed drafts for showcase

2. **Features to Demo**
   - User registration/login
   - League creation
   - Live drafting
   - Real-time updates
   - Player pool balance

## Implementation Timeline:
- **Wednesday PM**: Auth backend + basic frontend
- **Thursday AM**: Complete auth + start tests
- **Thursday PM**: Finish test suite + deployment
- **Friday AM**: Final testing + demo prep
