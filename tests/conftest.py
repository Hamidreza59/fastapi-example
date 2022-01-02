from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
import pytest
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

testSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine) # remove all tables
    Base.metadata.create_all(bind=engine) # create all tables before all tests
    db = testSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    # run our code before we run our test
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # run our code after we run our test

@pytest.fixture
def test_user(client):
    user_data = {"email": "hamid2@gmail.com", 
                 "password": "1234"}
    res = client.post('/users/', json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def test_user_2(client):
    user_data = {"email": "hamid3@gmail.com", 
                 "password": "1234"}
    res = client.post('/users/', json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f'Bearer {token}'
    }
    return client

@pytest.fixture
def test_posts(test_user, session, test_user_2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user['id']
    }, {
        "title": "4rd title",
        "content": "4rd content",
        "owner_id": test_user_2['id']
    },]

    def create_post_model(post):
        return models.Post(**post)

    added_posts = map(create_post_model, posts_data)
    session.add_all(list(added_posts))
    session.commit()
    
    posts = session.query(models.Post).all()
    return posts