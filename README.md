# RECRUITING2.0

Next generation recruitment platform focusing on holistic candidate-job matching.

## Features

- Multi-dimensional assessment system
  - Wellbeing preferences
  - Skills evaluation
  - Values alignment
- Sophisticated matching algorithm
- Instant job recommendations
- Company culture insights

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic (migrations)
- Python 3.9+

## Setup

1. Clone the repository:

```bash
git clone [repository-url]
cd recruiting2
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configurations
```

5. Start PostgreSQL database:

```bash
docker-compose up -d
```

6. Run database migrations:

```bash
alembic upgrade head
```

7. (Optional) Seed initial data:

```bash
python -m app.db.seed
```

8. Start the application:

```bash
uvicorn app.main:app --reload
```

## Development

### Running Tests

```bash
pytest
```

### Creating Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### API Documentation

Once the application is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
recruiting2/
├── alembic/                # Database migrations
├── app/
│   ├── api/               # API routes
│   ├── core/              # Business logic
│   ├── db/                # Database models and config
│   ├── middleware/        # Middleware components
│   └── schemas/           # Pydantic models
├── tests/                 # Test files
├── logs/                  # Application logs
├── .env                   # Environment variables
└── docker-compose.yml     # Docker configuration
```

## API Endpoints

### Assessment

- GET `/api/v1/assessments/{type}/questions` - Get assessment questions
- POST `/api/v1/assessments/{type}/submit` - Submit assessment answers

### Profile

- GET `/api/v1/users/{email}/profile` - Get user profile
- GET `/api/v1/users/{email}/recommendations` - Get job recommendations

### Status

- GET `/api/v1/users/{email}/assessment-status` - Check assessment completion

## Contributing

1. Create a new branch
2. Make your changes
3. Submit a pull request
