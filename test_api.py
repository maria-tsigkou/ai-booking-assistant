from main import app
from fastapi.testclient import TestClient
from unittest.mock import patch

client = TestClient(app)

class TestAPI:
    """Tests for the FastAPI endpoints."""
    def test_home(self):
        """Check that the home endpoint responds successfully."""
        response = client.get("/")

        assert response.status_code == 200

    def test_get_properties(self):
        """Check that the properties endpoint returns a list."""
        response = client.get("/properties")

        assert response.status_code == 200
        assert isinstance(response.json(),list)

    def test_search_invalid_dates(self):
        """Check that invalid search dates return HTTP 400."""
        response = client.get(
            "/properties/search",
            params={
                "guests":2,
                "check_in":"2027-12-15",
                "check_out":"2027-12-10"
            }
        )
        assert response.status_code == 400

    def test_booking_invalid_property(self):
        """Check that booking a nonexistent property returns HTTP 400."""
        response = client.post(
            "/bookings",
            json={
                "property_id":999,
                "check_in":"2027-12-10",
                "check_out":"2027-12-13"
            }
        )
        assert response.status_code == 400

class TestMockedAPI:
    """API tests using mocked database operations."""

    def test_get_properties_mocked(self):
        """Check that the API returns fake properties."""
        fake_properties = [
            {
                "id": 10,
                "name": "Mock Apartment",
                "price_per_night": 150.0,
                "capacity": 4
            }
        ]

        with patch("main.get_properties", return_value=fake_properties):
            response = client.get("/properties")

        assert response.status_code == 200
        assert response.json() == fake_properties

    def test_get_bookings_mocked(self):
        """Check that the API returns fake bookings."""
        fake_bookings = [
            {
                "id": 1,
                "property_id": 10,
                "check_in": "2027-12-10",
                "check_out": "2027-12-13"
            }
        ]

        with patch("main.get_bookings", return_value=fake_bookings):
            response = client.get("/bookings")

        assert response.status_code == 200
        assert response.json() == fake_bookings