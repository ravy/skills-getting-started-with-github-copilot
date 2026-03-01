"""
Tests for the Mergington High School API

Tests cover all endpoints:
- GET / - redirect to static files
- GET /activities - retrieve all activities
- POST /activities/{activity_name}/signup - sign up for an activity
- DELETE /activities/{activity_name}/participants - unregister from an activity
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy()
        }
        for name, activity in activities.items()
    }
    
    yield
    
    # Restore original state after test
    for name, activity in activities.items():
        activity["participants"] = original_activities[name]["participants"].copy()


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 9 activities are returned
        assert len(data) == 9
        
        # Verify expected activity names exist
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Tennis Club", "Art Studio",
            "Music Ensemble", "Debate Team", "Science Club"
        ]
        for activity_name in expected_activities:
            assert activity_name in data
    
    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["description"], str)
            assert isinstance(activity["schedule"], str)
            assert isinstance(activity["max_participants"], int)
            assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_valid_activity(self, client, reset_activities):
        """Test signing up for a valid activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify student was actually added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_invalid_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signups are prevented"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for different activities"""
        email = "newstudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_unregister_valid_participant(self, client, reset_activities):
        """Test unregistering a student from an activity"""
        email = "michael@mergington.edu"
        
        # Verify student is enrolled
        assert email in activities["Chess Club"]["participants"]
        
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify student was removed
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_invalid_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/participants",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_non_participant(self, client, reset_activities):
        """Test unregistering a student who is not signed up"""
        email = "noone@mergington.edu"
        
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can re-signup after unregistering"""
        email = "michael@mergington.edu"
        
        # Unregister
        response1 = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert response1.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
        
        # Sign up again
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        assert email in activities["Chess Club"]["participants"]


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
