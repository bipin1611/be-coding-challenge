import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import Base
from src.main import app
from src.database import get_db

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# /register
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/register", json={
        "username": "alice",
        "password": "secret123",
        "system": "github",
    })
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["system"] == "github"
    assert "id" in body
    assert "created_at" in body
    assert body["name"] is None
    assert body["email"] is None


@pytest.mark.asyncio
async def test_register_with_optional_fields(client):
    response = await client.post("/register", json={
        "username": "bob",
        "password": "pass",
        "system": "aws",
        "name": "Bob Smith",
        "email": "bob@example.com",
    })
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Bob Smith"
    assert body["email"] == "bob@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    payload = {"username": "alice", "password": "pass1", "system": "github"}
    await client.post("/register", json=payload)
    response = await client.post("/register", json=payload)
    assert response.status_code == 409
    assert "username" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/register", json={
        "username": "user1",
        "password": "pass",
        "system": "sys",
        "email": "shared@example.com",
    })
    response = await client.post("/register", json={
        "username": "user2",
        "password": "pass",
        "system": "sys",
        "email": "shared@example.com",
    })
    assert response.status_code == 409
    assert "email" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email_format(client):
    response = await client.post("/register", json={
        "username": "baduser",
        "password": "pass",
        "system": "sys",
        "email": "not-an-email",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_username(client):
    response = await client.post("/register", json={
        "password": "pass",
        "system": "sys",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_password(client):
    response = await client.post("/register", json={
        "username": "alice",
        "system": "sys",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_system(client):
    response = await client.post("/register", json={
        "username": "alice",
        "password": "pass",
    })
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# /login
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/register", json={
        "username": "carol",
        "password": "mypassword",
        "system": "github",
    })
    response = await client.post("/login", json={
        "username": "carol",
        "password": "mypassword",
    })
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/register", json={
        "username": "dave",
        "password": "correct",
        "system": "aws",
    })
    response = await client.post("/login", json={
        "username": "dave",
        "password": "wrong",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = await client.post("/login", json={
        "username": "ghost",
        "password": "pass",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_missing_username(client):
    response = await client.post("/login", json={"password": "pass"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_password(client):
    response = await client.post("/login", json={"username": "alice"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_token_contains_expected_claims(client):
    import jwt as pyjwt
    from src.config import settings

    await client.post("/register", json={
        "username": "eve",
        "password": "secret",
        "system": "internal",
    })
    response = await client.post("/login", json={
        "username": "eve",
        "password": "secret",
    })
    token = response.json()["access_token"]
    payload = pyjwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert payload["username"] == "eve"
    assert payload["system"] == "internal"
    assert "sub" in payload
    assert "exp" in payload
