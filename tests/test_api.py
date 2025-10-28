"""
Test cases for the FastAPI endpoints.
"""
import pytest
from fastapi import status
from src.app import activities


class TestGetActivities:
    """Test cases for the GET /activities endpoint."""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of all activities."""
        response = client.get("/activities")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that we get all expected activities
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Check structure of a specific activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_data_structure(self, client, reset_activities):
        """Test that activities have the correct data structure."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test cases for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify student was added to the activity
        assert email in activities[activity_name]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity."""
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration(self, client, reset_activities):
        """Test that students cannot register twice for the same activity."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Student is already signed up"
    
    def test_signup_missing_email(self, client, reset_activities):
        """Test signup without providing email parameter."""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_signup_empty_email(self, client, reset_activities):
        """Test signup with empty email parameter."""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email=")
        
        # Empty email is accepted by FastAPI but creates an empty string participant
        assert response.status_code == status.HTTP_200_OK
        # Verify empty string was added (this reveals current behavior)
        assert "" in activities[activity_name]["participants"]
    
    def test_signup_url_encoded_activity_name(self, client, reset_activities):
        """Test signup with URL-encoded activity name."""
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        email = "newstudent@mergington.edu"
        
        response = client.post(f"/activities/{encoded_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_200_OK
        assert email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Test cases for the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Verify student is initially registered
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify student was removed from the activity
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregistration from non-existent activity."""
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregistration of student who is not registered."""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_missing_email(self, client, reset_activities):
        """Test unregistration without providing email parameter."""
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_unregister_empty_email(self, client, reset_activities):
        """Test unregistration with empty email parameter."""
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email=")
        
        # Empty email returns 400 because empty string is not in participants
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_url_encoded_activity_name(self, client, reset_activities):
        """Test unregistration with URL-encoded activity name."""
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        email = "emma@mergington.edu"  # Already registered
        
        response = client.delete(f"/activities/{encoded_name}/unregister?email={email}")
        
        assert response.status_code == status.HTTP_200_OK
        assert email not in activities[activity_name]["participants"]


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestCompleteWorkflow:
    """Test cases for complete signup/unregister workflows."""
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete workflow of signing up and then unregistering."""
        activity_name = "Art Workshop"
        email = "workflow@mergington.edu"
        
        # Initial state - student not registered
        assert email not in activities[activity_name]["participants"]
        
        # Step 1: Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        assert email in activities[activity_name]["participants"]
        
        # Step 2: Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        assert email not in activities[activity_name]["participants"]
        
        # Step 3: Try to unregister again (should fail)
        unregister_again_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_again_response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_multiple_students_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity."""
        activity_name = "Science Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
            assert email in activities[activity_name]["participants"]
        
        # Verify all students are registered
        for email in emails:
            assert email in activities[activity_name]["participants"]
    
    def test_same_student_multiple_activities(self, client, reset_activities):
        """Test one student signing up for multiple activities."""
        email = "multisport@mergington.edu"
        activity_names = ["Soccer Team", "Basketball Club", "Math Olympiad"]
        
        for activity_name in activity_names:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
            assert email in activities[activity_name]["participants"]
        
        # Verify student is registered for all activities
        for activity_name in activity_names:
            assert email in activities[activity_name]["participants"]


class TestEdgeCases:
    """Test cases for edge cases and special scenarios."""
    
    def test_special_characters_in_email(self, client, reset_activities):
        """Test signup with special characters in email."""
        activity_name = "Drama Club"
        emails_and_expected = [
            ("test+tag@mergington.edu", "test tag@mergington.edu"),  # + becomes space in URL
            ("test.dot@mergington.edu", "test.dot@mergington.edu"),  # . stays the same
            ("test_underscore@mergington.edu", "test_underscore@mergington.edu")  # _ stays the same
        ]
        
        for email, expected_in_participants in emails_and_expected:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
            assert expected_in_participants in activities[activity_name]["participants"]
    
    def test_case_sensitive_activity_names(self, client, reset_activities):
        """Test that activity names are case sensitive."""
        correct_name = "Chess Club"
        incorrect_name = "chess club"
        email = "case@mergington.edu"
        
        # Correct case should work
        response = client.post(f"/activities/{correct_name}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Incorrect case should fail
        response = client.post(f"/activities/{incorrect_name}/signup?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND