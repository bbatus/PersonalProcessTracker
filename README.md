# Personal Process Tracker

A multi-user productivity tracking system for managing tasks, goals, habits, and personal development.

## 🚀 Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/bbatus/personal-process-tracker.git
cd personal-process-tracker

# Start services
docker compose up -d

# Run migrations
docker compose exec backend alembic upgrade head

# Seed categories
docker compose exec backend python seed_categories.py

# Create test user
docker compose exec backend python create_test_user.py

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8001/docs
```

### Google Cloud VM Deployment (One Command!)
```bash
curl -fsSL https://raw.githubusercontent.com/bbatus/personal-process-tracker/main/vm_quick_setup.sh | bash
```

See [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) for detailed deployment instructions.

## 📚 Documentation

- **[GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)** - Complete guide for deploying to Google Cloud VM
- **[DOCKER_HUB_DEPLOYMENT.md](DOCKER_HUB_DEPLOYMENT.md)** - Alternative deployment using Docker Hub
- **[QUICK_START.md](QUICK_START.md)** - Fast setup instructions
- **[PRD](prd.md)** - Product Requirements Document

## Features

- 🔐 **Multi-user Authentication** - Email verification, password reset, account lockout
- ✅ **Task Management** - Create, track, and organize daily tasks
- 🎯 **Goal Tracking** - Set and monitor progress toward objectives
- 🔥 **Habit Tracking** - Build consistent routines with streak tracking
- 📊 **Analytics** - Visualize productivity with charts and heatmaps
- 📝 **Monthly Retrospectives** - Reflect on progress and plan improvements

## Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 15+
- SQLAlchemy + Alembic
- Redis (sessions & rate limiting)
- JWT authentication

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts

**Infrastructure:**
- Docker Compose
- HTTPS/TLS
- Automated backups

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd personal-process-tracker
```

2. Copy environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Update environment variables in `backend/.env`:
   - Set `JWT_SECRET` to a secure random string
   - Configure email settings (Gmail App Password recommended)
   - **Configure Google OAuth:**
     1. Go to [Google Cloud Console](https://console.cloud.google.com/)
     2. Create a new project or select existing one
     3. Enable Google+ API
     4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
     5. Set application type to "Web application"
     6. Add authorized redirect URI: `http://localhost:8001/api/auth/google/callback`
     7. Copy Client ID and Client Secret to `.env` file

4. Start all services:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

6. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

### Default Test User

A test user is already created for quick testing:
- Username: `testuser`
- Password: `Test123!`

## Application Pages

### Dashboard (/)
- Overview of recent tasks, goals, and habits
- Quick statistics cards
- Navigation to all features

### Tasks (/tasks)
- Create and manage daily tasks
- Filter by date and status
- Mark tasks as done, skip, or postpone
- Categorize tasks
- Set estimated duration

### Goals (/goals)
- Set goals with target counts
- Track progress with visual progress bars
- Get deadline warnings
- Increment goal count

### Habits (/habits)
- Create daily, weekly, or monthly habits
- Log completions
- Track current and longest streaks
- Get at-risk warnings

### Analytics (/analytics)
- Weekly trend charts
- Completion rate visualization
- Category breakdown pie chart
- Most completed/skipped tasks insights

### Retrospective (/retrospective)
- Write monthly retrospectives
- Log daily mood (1-10 scale)
- View automatic monthly statistics
- Browse past retrospectives

## Development

### Backend Development

```bash
# Enter backend container
docker-compose exec backend bash

# Run tests
pytest

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend Development

```bash
# Enter frontend container
docker-compose exec frontend sh

# Run tests
npm test

# Build for production
npm run build
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── alembic/          # Database migrations
│   ├── tests/            # Tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities
│   │   └── types/        # TypeScript types
│   └── package.json
└── docker-compose.yml
```

## Testing

The project uses both unit tests and property-based tests:

**Backend:**
```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app

# Run property tests only
docker-compose exec backend pytest tests/property/
```

**Frontend:**
```bash
# Run all tests
docker-compose exec frontend npm test

# Run in watch mode
docker-compose exec frontend npm run test:watch
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Security

- Passwords hashed with bcrypt (12 rounds)
- JWT tokens with 7-day expiration
- Account lockout after 5 failed attempts
- Rate limiting (100 requests/minute)
- CORS protection
- CSRF protection
- Input sanitization

## License

MIT

## Contributing

Contributions are welcome! Please read the contributing guidelines first.
