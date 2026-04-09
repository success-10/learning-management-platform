# EduFlow — Event-Driven Learning Management Platform

A Coursera-inspired LMS backend built with Django REST Framework, Celery, and Redis.
Designed with a clean Service/Selector architecture and event-driven communication between apps.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer (DRF)                         │
│  Views → Serializers → Permissions → Throttling → Pagination   │
├─────────────────────────────────────────────────────────────────┤
│                      Service / Selector Layer                   │
│  Services: Write operations (create, update, delete)            │
│  Selectors: Read operations (list, filter, aggregate)           │
├─────────────────────────────────────────────────────────────────┤
│                       Event Bus (Django Signals)                │
│  core/events.py → Central event catalog                         │
│  Apps fire events via transaction.on_commit()                   │
├─────────────────────────────────────────────────────────────────┤
│                    Async Workers (Celery + Redis)               │
│  Signal listeners dispatch Celery tasks                         │
│  Tasks: scoring, notifications, analytics, progress updates     │
├─────────────────────────────────────────────────────────────────┤
│                       Data Layer (Django ORM)                   │
│  MySQL/PostgreSQL + Redis Cache                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Apps

| App | Purpose |
|---|---|
| `core` | Shared models (TimeStampedModel), event definitions, mixins |
| `accounts` | Custom User model, JWT auth, role-based permissions |
| `courses` | Course → Module → Lesson hierarchy, CRUD with ownership |
| `enrollments` | Student enrollment/unenrollment with event emission |
| `assessments` | Quizzes, questions, submissions, async scoring |
| `progress` | Lesson completion tracking, course progress calculation |
| `notifications` | In-app + email notifications triggered by events |
| `analytics` | Event logging for admin dashboards |
| `audit_logs` | Compliance audit trail for all write operations |

### Event-Driven Flow

```
Student submits assessment
  → AssessmentService creates Submission
  → Fires: assessment_submitted (via transaction.on_commit)
  → Listener dispatches: calculate_score.delay()

Celery worker scores submission
  → Fires: score_calculated (with user_id, course_id, score, passed)
  → Three listeners react:
      1. progress → update_course_progress.delay()
      2. notifications → send_score_notification.delay()
      3. analytics → log_analytics_event.delay()
```

---

## Tech Stack

- **Backend**: Django 4.2+ / Django REST Framework
- **Auth**: JWT (SimpleJWT)
- **Async**: Celery 5.3+ with Redis broker
- **Cache**: Redis (separate DB from broker)
- **Database**: MySQL 8.0 (PostgreSQL recommended for production)
- **Docs**: drf-spectacular (OpenAPI 3.0 / Swagger)
- **Container**: Docker + Docker Compose

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development without Docker)

### Using Docker (Recommended)

```bash
# 1. Clone and enter the project
cd EduFlow

# 2. Create environment file
cp .env.example .env

# 3. Start all services
docker compose up --build

# 4. Run migrations (in another terminal)
docker compose exec web python manage.py migrate

# 5. Create a superuser
docker compose exec web python manage.py createsuperuser
```

Services will be available at:
- **API**: http://localhost:8000/api/v1/
- **Swagger Docs**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/

### Local Development (without Docker)

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your local DB and Redis URLs

# 4. Run migrations
python manage.py migrate

# 5. Start the dev server
python manage.py runserver

# 6. Start Celery worker (separate terminal)
celery -A config worker --loglevel=info

# 7. Start Celery Beat (separate terminal)
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/accounts/auth/login/` | Obtain JWT token |
| POST | `/api/v1/accounts/auth/refresh/` | Refresh JWT token |
| POST | `/api/v1/accounts/users/register/` | Register new user |
| GET | `/api/v1/accounts/users/me/` | Current user profile |

### Courses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/courses/` | List courses (filterable/searchable) |
| POST | `/api/v1/courses/` | Create course (instructor only) |
| GET | `/api/v1/courses/{uuid}/` | Course detail |
| PUT | `/api/v1/courses/{uuid}/` | Update course |
| DELETE | `/api/v1/courses/{uuid}/` | Delete course |
| POST | `/api/v1/courses/{uuid}/publish/` | Publish course |
| POST | `/api/v1/courses/{uuid}/unpublish/` | Unpublish course |
| POST | `/api/v1/courses/{uuid}/enroll/` | Enroll in course |

### Modules & Lessons (Nested)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/courses/{uuid}/modules/` | List modules |
| POST | `/api/v1/courses/{uuid}/modules/` | Create module |
| GET | `/api/v1/courses/{uuid}/modules/{uuid}/lessons/` | List lessons |
| POST | `/api/v1/courses/{uuid}/modules/{uuid}/lessons/` | Create lesson |

### Assessments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/assessments/assessments/` | List assessments |
| POST | `/api/v1/assessments/assessments/submit/` | Submit answers |
| GET | `/api/v1/assessments/submissions/` | My submissions |

### Enrollments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/my-enrollments/` | My enrollments |
| DELETE | `/api/v1/my-enrollments/{id}/unenroll/` | Unenroll |

### Progress
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/progress/` | My course progress |
| POST | `/api/v1/progress/complete_lesson/` | Mark lesson complete |
| GET | `/api/v1/progress/lesson_completions/` | My completed lessons |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/` | My notifications |
| PATCH | `/api/v1/notifications/{id}/read/` | Mark as read |
| POST | `/api/v1/notifications/read_all/` | Mark all as read |

### Analytics (Admin only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/events/` | Browse analytics events |

---

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific app tests
pytest apps/courses/tests/
pytest apps/enrollments/tests/

# Run with coverage
pytest --cov=apps --cov-report=html
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-key` |
| `DEBUG` | Debug mode (1/0) | `0` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `` |
| `DATABASE_URL` | Database connection string | — |
| `CELERY_BROKER_URL` | Redis broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis result backend | `redis://localhost:6379/0` |
| `REDIS_CACHE_URL` | Redis cache URL (use different DB) | `redis://localhost:6379/1` |

---

## Project Structure

```
EduFlow/
├── apps/
│   ├── core/              # Shared: events, models, mixins, health check
│   ├── accounts/          # User, JWT, permissions, RBAC
│   ├── courses/           # Course/Module/Lesson CRUD + search/filter
│   ├── enrollments/       # Enrollment management + events
│   ├── assessments/       # Assessments, scoring pipeline
│   ├── progress/          # Lesson completion + course progress
│   ├── notifications/     # In-app + email notifications
│   ├── analytics/         # Event logging + admin dashboard
│   └── audit_logs/        # Compliance audit trail
├── config/
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── local.py       # Development overrides
│   │   ├── test.py        # Test overrides
│   │   └── production.py  # Production security
│   ├── celery.py          # Celery app + error monitoring
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI entry point
├── conftest.py            # Shared test fixtures
├── pyproject.toml         # pytest configuration
├── requirements.txt       # Python dependencies
├── Dockerfile             # Multi-stage production build
├── docker-compose.yml     # Full stack orchestration
├── .env.example           # Environment variable template
└── .gitignore             # VCS exclusions
```
