import pytest
from importlib import reload
from fastapi.testclient import TestClient

import src.app

client = TestClient(src.app.app)


@pytest.fixture(autouse=True)
def reset_activities():
    reload(src.app)


def test_root_redirect():
    # Arrange
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 200  # Assuming it serves the static file or follows redirect
    # Perhaps check content, but for now, just status


def test_get_activities():
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    # Verify added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    activity = "Programming Class"
    email = "dup@mergington.edu"
    client.post(f"/activities/{activity}/signup", params={"email": email})  # first signup
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_missing_activity():
    # Arrange
    activity = "Nonexistent Activity"
    email = "test@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_participant_success():
    # Arrange
    activity = "Gym Class"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity}/signup", params={"email": email})  # add first
    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    # Verify removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity]["participants"]


def test_remove_participant_missing_activity():
    # Arrange
    activity = "Nonexistent Activity"
    email = "test@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_participant_missing_participant():
    # Arrange
    activity = "Basketball Team"
    email = "notthere@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]