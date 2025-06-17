import os
import sys
# Add the project root to PYTHONPATH so tests can import application modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app_full import app, db

@pytest.fixture
def client():
    # Configure testing & disable CSRF
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    # Push application context
    ctx = app.app_context()
    ctx.push()

    # Create tables and test client
    db.create_all()
    client = app.test_client()

    yield client

    # Teardown
    db.drop_all()
    ctx.pop()


@pytest.fixture
def test_student():
    from app_full import Student
    # Create and return a default test student
    stu = Student(
        name="Test Student",
        email="test@student.com",
        qr_id="T1",
        pin_hash="fake-hash",
        block="A"
    )
    db.session.add(stu)
    db.session.commit()
    return stu