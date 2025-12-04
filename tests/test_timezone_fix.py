"""
Tests for Timezone API Fix:
1. Allow admins to sync timezone
2. Return 401 instead of redirect for unauthenticated users
"""
import pytest
from datetime import datetime, timezone
from app import db
from app.models import Admin

@pytest.fixture
def admin_user(client):
    """Create an admin for testing."""
    admin = Admin(
        username="testadmin_tz",
        totp_secret="TESTSECRET123456"
    )
    db.session.add(admin)
    db.session.commit()
    return admin

def test_set_timezone_unauthenticated(client):
    """Test that /api/set-timezone returns 401 for unauthenticated users."""
    response = client.post(
        '/api/set-timezone',
        json={'timezone': 'America/New_York'}
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Unauthorized'

def test_set_timezone_admin(client, admin_user):
    """Test that /api/set-timezone works for admins."""

    # Login as admin
    with client.session_transaction() as sess:
        sess['is_admin'] = True
        sess['admin_id'] = admin_user.id
        sess['last_activity'] = datetime.now(timezone.utc).isoformat()

    # Test timezone sync
    response = client.post(
        '/api/set-timezone',
        json={'timezone': 'America/Chicago'}
    )

    # Should succeed with admin auth
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

    # Verify timezone was stored in session
    with client.session_transaction() as sess:
        assert sess.get('timezone') == 'America/Chicago'

def test_set_timezone_student(client, test_student):
    """Test that /api/set-timezone still works for students."""

    # Login as student
    with client.session_transaction() as sess:
        sess['student_id'] = test_student.id
        sess['login_time'] = datetime.now(timezone.utc).isoformat()

    # Test timezone sync
    response = client.post(
        '/api/set-timezone',
        json={'timezone': 'America/Los_Angeles'}
    )

    # Should succeed with student auth
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

    # Verify timezone was stored in session
    with client.session_transaction() as sess:
        assert sess.get('timezone') == 'America/Los_Angeles'
