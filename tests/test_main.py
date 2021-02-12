import os
import pytest
from main import app, db
from models import User


@pytest.fixture
def client():
    app.config['TESTING']=True
    os.environ["DATEBASE_URL"] = "sqlite:///:memory:"

    client = app.test_client()

    db.create_all()

    yield client

def cleanup():
    db.drop_all()

def test_index_not_logged_in(client):
    response = client.get('/')
    assert b'Odgadnij' in response.data
    assert response.status_code == 200

def test_index_logged_in(client):
    client.post("/login", data={"user-name":"Uzytkownik testowu", "user-email":"test@gmail.com", "user-password":"haslo123"}, follow_redirects=True)

    response = client.get("/")
    assert b'Wprowadz swoja liczbe' in response.data

def test_result_correct(client):
    client.post("/login", data={"user-name":"Test123", "user-email":"123@gmail.com", "user-password":"pas123"}, follow_redirects=True)

    user = db.query(User).first()

    user.secret_number = 17
    db.add(user)
    db.commit()

    response = client.post("/result", data={"quess": 17})
    assert b'Ci' in response.data

def test_result_try_bigger(client):
    client.post('/login', data={"user-name":"user", "user-email":"gosia@gmail.com", "user-password":"haslo1234"}, follow_redirects=True)

    user = db.query(User).first()

    user.secret_number = 20

    db.add(user)
    db.commit()

    response = client.post('/result', data={"quess":18})
    assert b'Twoja liczba jest zbyt duza' in response.data

def test_result_try_lower(client):
    client.post('/login', data={"user-name":"user", "user-email":"gosia@gmail.com", "user-password":"haslo1234"}, follow_redirects=True)

    user = db.query(User).first()

    user.secret_number = 2

    db.add(user)
    db.commit()

    response = client.post('/result', data={"quess":28})
    assert b'Twoja liczba jest zbyt mala' in response.data

def test_profile(client):
    client.post("/login", data={"user-name":"user", "user-email":"gosia@gmail.com", "user-password":"haslo1234"}, follow_redirects=True)

    response = client.get('/profile')
    assert b'Twoja nazwa to' in response.data

def test_profile_edit(client):
    client.post("/login", data={"user-name": "user", "user-email": "gosia@gmail.com", "user-password": "haslo1234"},
                follow_redirects=True)

    response = client.get('/profile/edit')
    assert b'Edycja profilu' in response.data

    response = client.post('/profile/edit', data={"profile-name":"User2", "profile-email":"gosia2@gmail.com"}, follow_redirects=True)

    assert b'User2' in response.data
    assert b'gosia2@gmail.com' in response.data

def test_profile_del(client):
    client.post("/login", data={"user-name": "user3", "user-email": "gosia3@gmail.com", "user-password": "haslo12345"},
                follow_redirects=True)

    response = client.get('/profile/delete')
    assert b'swoje konto?' in response.data

    response = client.post('/profile/delete', follow_redirects=True)
    assert b'Odgadnij' in response.data

def test_all_users(client):
    response = client.get('/users')
    assert b'Lista uzytkownikow'

    client.post("/login", data={"user-name": "user", "user-email": "gosia3@gmail.com", "user-password": "haslo12345"},
                follow_redirects=True)

    response = client.get('/users')
    assert b'Lista uzytkownikow' in response.data
    assert b'user' in response.data