"""
Tests for the High School Management System API
"""

from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities GET endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9
    
    def test_get_activities_has_correct_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Test the /activities/{activity_name}/signup POST endpoint"""
    
    def setup_method(self):
        """Reset activities before each test"""
        # Reset participants to initial state
        activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
        activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    
    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant_fails(self):
        """Test that signing up a duplicate participant fails"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self):
        """Test that signing up for a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_participants(self):
        """Test signing up multiple participants"""
        initial_count = len(activities["Programming Class"]["participants"])
        
        # Sign up first participant
        response1 = client.post(
            "/activities/Programming Class/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up second participant
        response2 = client.post(
            "/activities/Programming Class/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        assert len(activities["Programming Class"]["participants"]) == initial_count + 2


class TestUnregisterEndpoint:
    """Test the /activities/{activity_name}/unregister DELETE endpoint"""
    
    def setup_method(self):
        """Reset activities before each test"""
        # Reset participants to initial state
        activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
        activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
        activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
    
    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        initial_count = len(activities["Chess Club"]["participants"])
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1
    
    def test_unregister_nonexistent_participant_fails(self):
        """Test that unregistering a nonexistent participant fails"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_from_nonexistent_activity_fails(self):
        """Test that unregistering from a nonexistent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_multiple_participants(self):
        """Test unregistering multiple participants"""
        initial_count = len(activities["Gym Class"]["participants"])
        
        # Unregister first participant
        response1 = client.delete(
            "/activities/Gym Class/unregister?email=john@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Unregister second participant
        response2 = client.delete(
            "/activities/Gym Class/unregister?email=olivia@mergington.edu"
        )
        assert response2.status_code == 200
        
        assert len(activities["Gym Class"]["participants"]) == initial_count - 2
        assert len(activities["Gym Class"]["participants"]) == 0
    
    def test_unregister_then_signup_same_participant(self):
        """Test that a participant can sign up again after unregistering"""
        # Unregister
        response1 = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response1.status_code == 200
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        
        # Sign up again
        response2 = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response2.status_code == 200
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that the root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
