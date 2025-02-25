import pytest
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.core.schemas.user_schema import UserCreateSchema, LoginSchema
from app.core.models.user import User
from app.core.exceptions.custom_exceptions import DuplicateUsernameError, InvalidCredentialsError

@pytest.fixture
def db_session():
    # Setup code for creating a test database session
    # You can use an in-memory SQLite database for testing
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base

    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture
def auth_service(db_session: Session):
    return AuthService(db_session)

def test_register_user(auth_service: AuthService):
    user_data = UserCreateSchema(username="testuser", email="test@example.com", password="password")
    user = auth_service.register(user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_register_duplicate_user(auth_service: AuthService):
    user_data = UserCreateSchema(username="testuser", email="test@example.com", password="password")
    auth_service.register(user_data)
    with pytest.raises(DuplicateUsernameError):
        auth_service.register(user_data)

def test_login_user(auth_service: AuthService, db_session: Session):
    user_data = UserCreateSchema(username="testuser", email="test@example.com", password="password")
    auth_service.register(user_data)
    login_data = LoginSchema(username="testuser", password="password")
    token = auth_service.login(login_data)
    assert "access_token" in token

def test_login_invalid_user(auth_service: AuthService):
    login_data = LoginSchema(username="invaliduser", password="password")
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(login_data)