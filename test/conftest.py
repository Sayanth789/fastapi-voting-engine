from fastapi.testclient import TestClient 
import pytest 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app 

from app.config import settings 
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models 

# 💡 Dynamic Test Database connection string
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 💡 Fixed: changed autoFlush to autoflush
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

@pytest.fixture() 
def session():
    print("Setting up test database tables...")
    # 💡 Clean database and create all tables for a fresh state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db  # 💡 Yield the active session to the client override
    finally:
        db.close()

@pytest.fixture() 
def client(session):  # 💡 Fixed spelling from cleint -> client
    def override_get_db():
        try: 
            yield session 
        finally:
            pass  # Session closing is handled by the session fixture lifecycle

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # 💡 Clear overrides after the test finishes to avoid polluting other test files
    app.dependency_overrides.clear()

@pytest.fixture 
def test_user(client):
    user_data = {"email": "sayanthvv777@gmail.com", "password": "password123"}
    res = client.post('/users/', json=user_data) # 💡 Fixed trailing slash

    assert res.status_code == 201 
    new_user = res.json()                 
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture 
def test_user2(client):
    # 💡 Changed email so it doesn't violate a UNIQUE database constraint with test_user
    user_data = {"email": "anotheruser@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data) # 💡 Fixed trailing slash & .json() typo

    assert res.status_code == 201 
    new_user = res.json() 
    new_user['password'] = user_data['password'] # 💡 Fixed spelling of password
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    }, {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user['id']
    }, {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user2['id']
    }]

    # 💡 Map dictionaries cleanly to your SQLAlchemy model instances
    posts = [models.Post(**post) for post in posts_data]

    session.add_all(posts)
    session.commit()

    posts = session.query(models.Post).all()
    return posts
