# Architecture & Design Overview

Note: Please refer to `README.md` for setup instructions, API docs, and project structure.

## Technology Stack (MVP)

| Layer      | Technology                  |
|------------|-----------------------------|
| API        | FastAPI (Python 3.11)       |
| Database   | PostgreSQL                  |
| Container  | Docker                      |

## Decision

### FastAPI
I chose FastAPI for this project because of its modern features, excellent performance, and fast development experience.

### PostgreSQL
I prefer PostgreSQL because it is a powerful, open-source relational database that is widely used in production environments.

### API Design
I have made two different endpoints, `register` and `login`. 
The reason for this is, to validate `hash function` for password (which i will cover in next paragraph) and future considerations.
So, our MVP is the `register` endpoint. 

For the `login` endpoint, i have implemented a simple JWT-based authentication mechanism, that can be used to authenticate users and protect other API endpoints.

## Storing Passwords
Here, i have chose `sha256` to store hashed passwords, because it is way more secure than `encrypting passwords`.
I havn't considered `encryption of passwords` because, it can be easily decrypted if the key is compromised. 
On the other hand, `hashing` is a one-way function, which means that it cannot be reversed to original password.

However, if we explicitly want to use the password for login into external system, than i would suggest to use different techniques,
such as: 
   - SSO (Single Sign-On) method, for that we will `expose API endpoint to login to external system using the JWT token`.
   - Or, we can use `OAuth` for secure authentication, which will allow users to authenticate using their existing credentials from other services (e.g., Google, Facebook) without sharing their passwords with our application.
   - Even better, we can use `passkeys` for passwordless authentication, which is more secure and user-friendly.

## Security Considerations
- Passwords are hashed using `PBKDF2-HMAC-SHA256` with a random salt and 260,000 iterations before storing in the database.
- JWT tokens are used for authentication, which can be securely signed and verified.

## Limitations
- Its limited to `register` and `login` endpoints, and does not include features like password reset, email verification, or user roles/permissions.
- The JWT implementation is basic and does not include features like token refresh or blacklisting.
- It's only works with `PostgreSQL` database, and does not support other databases.
- The application does not currently implement any caching or performance optimizations.

## Assumptions
- Assumed that the app will be deployed in a secure environment over HTTPS.


## Future Considerations
- `OAuth`  for secure authentication
- Even better, `passkeys` for passwordless authentication, which is more secure and user-friendly
- Caching with `Redis`
- Email notifications with Queue system like `RabbitMQ` or `Celery`


## AI Useage
I have used AI to assist with the following tasks:
- Generating boilerplate code for FastAPI application
- Generating Dockerfile and docker-compose.yml
- Writing tests for the API endpoints
- Logic for Logger class
- Generating documentation for `Secondary Libraries` and `Flow Diagram` sections in this file

## Flow Diagram
```
Client
  └─► Router (routers/)
        └─► Service (services/)
              └─► ORM Model (models/)
                    └─► PostgreSQL
```


## Secondary Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `sqlalchemy` | 2.0.36 | Async ORM for database models and queries |
| `asyncpg` | 0.30.0 | High-performance async PostgreSQL driver |
| `pydantic-settings` | 2.7.0 | Environment-based configuration management |
| `PyJWT` | 2.10.1 | JWT token creation and validation for auth |
| `uvicorn[standard]` | 0.34.0 | ASGI server to run the FastAPI app |
| `pytest` | 8.3.4 | Test framework |
| `pytest-asyncio` | 0.25.0 | Async test support for pytest |
| `httpx` | 0.28.1 | Async HTTP client used in tests |
| `aiosqlite` | 0.20.0 | In-memory SQLite backend for test isolation |
| `python-dotenv` | 1.0.1 | Loads `.env` files for local development |
