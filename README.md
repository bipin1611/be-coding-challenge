# Backend Coding Challenge

Note: Architecture overview and design decisions are documented in `docs/architecture.md`.

Following points are in `docs/architecture.md`:
- Architecture & Design Overview
- Decisions that I have made
- Assumptions
- Password hashing vs encryption
- Security considerations
- Limitations
- Future considerations
- AI usage in this project
- Flow Diagram

## Requirements
- Python 3.11+
- Docker
- PostgreSQL 15+

## Installation and Setups
I have used `Docker` only, otherwise manual setup(which i havn't included), it will take longer time to setup everything.

### 1. Clone the repository
```bash 
git clone https://github.com/bipin1611/be-coding-challenge.git
cd be-coding-challenge
```

### 2. Environment setup
```bash
cp .env.example .env # Edit .env with your values
```
As we are using `Docker`, you don't need to change Database `credentials` in `.env` file.
Database and migration will be run automatically by `entrypoint.sh` script.


### 3. Start Docker Compose and run the application
```bash
docker-compose up --build
```

## API Docs
Once Docker containers are running, visit:
- Swagger UI: http://127.0.0.1:8000/docs

### API Endpoints
- `POST /register` - Create a new login credential (MVP)
    - Example Request body:
    ```bash
    curl -X 'POST' \
        'http://127.0.0.1:8000/register' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
            "name": "John Doe",
            "email": "joh.doe@example.com",
            "username": "john12345",
            "password": "password@123",
            "system": "chrome"
        }'
    ```

- `POST /login` - Authenticate and receive a JWT token
    - Example Request body:
    ```bash
    curl -X 'POST' \
        'http://127.0.0.1:8000/login' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
            "username": "john12345",
            "password": "password@123"
        }'
    ```

## Project Structure

```
repo/
├── src/
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # App configuration / settings
│   ├── database.py      # Database connection & session
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── routers/         # API route handlers
│   └── services/        # Business logic
├── tests/               # Pytest test suite
├── migrations/          # Database migrations
├── docs/
│   └── architecture.md  # Architecture overview
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Running Tests

### With Docker (recommended)

Tests use an in-memory SQLite database.

Build the image first:

```bash
docker-compose build api
```

Then run the full test suite:

```bash
docker-compose run --rm --no-deps api pytest tests/ -v
```

### Locally
Install dependencies and run pytest directly:

```bash
pip install -r requirements.txt
pytest tests/ -v
```
