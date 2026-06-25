import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activity participants to a known state before each test."""
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in original.items():
        activities[name]["participants"] = participants


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data


def test_get_activities_includes_expected_fields():
    response = client.get("/activities")
    activity = response.json()["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    assert response.status_code == 200
    assert "new@mergington.edu" in response.json()["message"]
    assert "new@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_unknown_activity():
    response = client.post("/activities/Unknown Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_participant():
    client.post("/activities/Chess Club/signup?email=dup@mergington.edu")
    response = client.post("/activities/Chess Club/signup?email=dup@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# --- DELETE /activities/{activity_name}/signup ---

def test_unregister_success():
    client.post("/activities/Chess Club/signup?email=remove@mergington.edu")
    response = client.delete("/activities/Chess Club/signup?email=remove@mergington.edu")
    assert response.status_code == 200
    assert "remove@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_unknown_activity():
    response = client.delete("/activities/Unknown Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_not_signed_up():
    response = client.delete("/activities/Chess Club/signup?email=notregistered@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"
