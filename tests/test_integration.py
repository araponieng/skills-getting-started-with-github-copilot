"""
Integration tests for the complete application.
"""
import pytest
from fastapi import status
from src.app import activities


class TestApplicationIntegration:
    """Integration tests for the complete application workflow."""
    
    def test_activities_data_integrity(self, client, reset_activities):
        """Test that activities data maintains integrity across operations."""
        # Get initial activities count
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data)
        
        # Perform some operations
        client.post("/activities/Chess Club/signup?email=integration@mergington.edu")
        client.delete("/activities/Programming Class/unregister?email=emma@mergington.edu")
        
        # Check activities count hasn't changed
        response = client.get("/activities")
        final_data = response.json()
        assert len(final_data) == initial_count
        
        # Check specific changes were applied
        assert "integration@mergington.edu" in final_data["Chess Club"]["participants"]
        assert "emma@mergington.edu" not in final_data["Programming Class"]["participants"]
    
    def test_concurrent_operations_simulation(self, client, reset_activities):
        """Test simulation of concurrent operations on the same activity."""
        activity_name = "Basketball Club"
        emails = [f"concurrent{i}@mergington.edu" for i in range(5)]
        
        # Simulate multiple signups
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all signups were successful
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        for email in emails:
            assert email in activity_data["participants"]
    
    def test_activity_capacity_not_enforced(self, client, reset_activities):
        """Test that the current implementation doesn't enforce capacity limits."""
        # Note: The current implementation doesn't enforce max_participants
        # This test documents the current behavior
        activity_name = "Chess Club"  # max_participants: 12
        initial_participants = len(activities[activity_name]["participants"])
        
        # Add more participants than the max_participants limit
        emails_to_add = [f"overflow{i}@mergington.edu" for i in range(15)]
        
        for email in emails_to_add:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all were added (demonstrating no capacity enforcement)
        final_participants = len(activities[activity_name]["participants"])
        assert final_participants == initial_participants + len(emails_to_add)
    
    def test_persistent_state_across_requests(self, client, reset_activities):
        """Test that state persists across multiple API requests."""
        activity_name = "Drama Club"
        email = "persistent@mergington.edu"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Make a different API call
        client.get("/activities")
        
        # Check that the signup persisted
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity_name]["participants"]
        
        # Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Make another different API call
        client.get("/activities")
        
        # Check that the unregister persisted
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity_name]["participants"]


class TestDataValidation:
    """Test data validation and error handling."""
    
    def test_malformed_requests(self, client, reset_activities):
        """Test handling of malformed requests."""
        # Test with invalid HTTP methods
        response = client.put("/activities")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response = client.patch("/activities/Chess Club/signup")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_unicode_handling(self, client, reset_activities):
        """Test handling of unicode characters in activity names and emails."""
        # Test with unicode in email
        unicode_email = "tést@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={unicode_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Test with unicode in activity name (should fail as activity doesn't exist)
        unicode_activity = "Chéss Club"
        response = client.post(f"/activities/{unicode_activity}/signup?email=test@mergington.edu")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_sql_injection_protection(self, client, reset_activities):
        """Test protection against SQL injection attempts (though we use in-memory dict)."""
        malicious_email = "'; DROP TABLE activities; --"
        
        response = client.post(f"/activities/Chess Club/signup?email={malicious_email}")
        # Should either succeed (treating as normal email) or fail validation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        # Verify activities still exist
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0


class TestPerformance:
    """Basic performance and load testing."""
    
    def test_response_time_activities_endpoint(self, client, reset_activities):
        """Test that activities endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        # Response should be very fast for in-memory data
        assert (end_time - start_time) < 1.0  # Less than 1 second
    
    def test_bulk_operations(self, client, reset_activities):
        """Test bulk operations performance."""
        import time
        
        # Perform 50 signup operations
        start_time = time.time()
        
        for i in range(50):
            email = f"bulk{i}@mergington.edu"
            activity = list(activities.keys())[i % len(activities)]
            client.post(f"/activities/{activity}/signup?email={email}")
        
        end_time = time.time()
        
        # Should complete bulk operations in reasonable time
        assert (end_time - start_time) < 5.0  # Less than 5 seconds for 50 operations


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""
    
    def test_network_simulation(self, client, reset_activities):
        """Test handling of various HTTP scenarios."""
        # Test extremely long email
        long_email = "a" * 1000 + "@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={long_email}")
        # Should handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        # Test extremely long activity name
        long_activity = "a" * 1000
        response = client.post(f"/activities/{long_activity}/signup?email=test@mergington.edu")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_boundary_conditions(self, client, reset_activities):
        """Test boundary conditions."""
        # Test empty activity name (should be handled by FastAPI routing)
        response = client.post("/activities//signup?email=test@mergington.edu")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test activity name with special characters
        special_activity = "Art & Crafts"
        response = client.post(f"/activities/{special_activity}/signup?email=test@mergington.edu")
        assert response.status_code == status.HTTP_404_NOT_FOUND