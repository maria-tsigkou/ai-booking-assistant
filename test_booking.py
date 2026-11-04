from datetime import date
from decimal import Decimal
from booking import calculate_price, search_properties
from database import check_database_availability
from unittest.mock import patch
import pytest

class TestPriceCalculation:
    """Tests for calculating booking prices."""

    def test_valid_price(self):
        """Check that the total booking price is calculated correctly."""
        total = calculate_price(
            property_id=1,
            check_in=date(2027,11,10),
            check_out=date(2027,11,13)
        )
        assert total == Decimal("360.00")

    def test_invalid_dates(self):
        """Test that check-out before check-in raises a ValueError."""
        with pytest.raises(ValueError):
            calculate_price(
                property_id=1,
                check_in=date(2027,11,15),
                check_out=date(2027,11,10)
            )

    def test_invalid_property(self):
        """Check that a nonexistent property raises a ValueError."""
        with pytest.raises(ValueError, match="Property not found"):
            calculate_price(
                property_id=999,
                check_in=date(2027,11,10),
                check_out=date(2027,11,13)
        )

    def test_same_day_booking(self):
        """Check that check-in and check-out cannot be on the same day."""
        with pytest.raises(ValueError, match="Invalid booking dates"):
            calculate_price(
                property_id=1,
                check_in=date(2027,11,10),
                check_out=date(2027,11,10)
            )

    def test_one_night_booking(self):
        """Check that a one-nigh stay has the correct price."""
        total = calculate_price(
            property_id=1,
            check_in=date(2027,11,10),
            check_out=date(2027,11,11)
        )
        assert total == Decimal("120.00")

class TestPropertySearch:
    """Tests for searching available properties."""

    def test_capacity(self):
        """Check that search results have enough capacity for guests."""
        results = search_properties(
            guests=5,
            check_in=date(2027,12,10),
            check_out=date(2027,12,13)
        )
        assert len(results) == 1
        assert results[0]["name"] == "Mountain Villa"

    def test_no_property_with_enough_capacity(self):
        """Check that searching for too many guests returns no properties."""
        results = search_properties(
            guests=7,
            check_in=date(2027,12,10),
            check_out=date(2027,12,13)
        )
        assert results == []

    def test_invalid_guest_count(self):
        """Check that searching for zero guests raises a ValueError."""
        with pytest.raises(ValueError):
            search_properties(
                guests=0,
                check_in=date(2027,12,10),
                check_out=date(2027,12,13)
            )

    def test_invalid_dates(self):
        """Check that sarching with invalid dates raises a ValueError"""
        with pytest.raises(ValueError, match="Invalid booking dates"):
            search_properties(
                guests=2,
                check_in=date(2027,12,15),
                check_out=date(2027,12,10)
            )

    def test_unavailable_property(self):
        """Check that a booked property is excluded from search results."""
        results = search_properties(
            guests=2,
            check_in=date(2027,9,12),
            check_out=date(2027,9,14)
        )
        #property_ids -> a list of the IDs returned by our search function
        property_ids = [property_data["id"] for property_data in results]
        assert 1 not in property_ids
        assert 2 in property_ids

class TestBookingAvailability:
    """Tests for checking property availability."""

    def test_available_property(self):
        """Check that a property is available when there are no bookings."""
        available = check_database_availability(
            property_id=1,
            check_in=date(2027,12,20),
            check_out=date(2027,12,23)
        )
        assert available is True

    def test_overlapping_booking(self):
        """Check that overlapping dates are unavailable."""
        available = check_database_availability(
            property_id=1,
            check_in=date(2027, 9, 12),
            check_out=date(2027, 9, 14)
        )

        assert available is False

    def test_back_to_back_booking(self):
        """Check that a new booking can start when another ends."""
        available = check_database_availability(
            property_id=1,
            check_in=date(2027, 9, 15),
            check_out=date(2027, 9, 18)
        )

        assert available is True

    def test_different_property_same_dates(self):
        """Check that another property remains available for the same dates."""
        available = check_database_availability(
            property_id=2,
            check_in=date(2027, 9, 12),
            check_out=date(2027, 9, 14)
        )

        assert available is True

class TestMockedPriceCalculation:
    """Tests for price calculation without accessing the database"""

    def test_price_with_mock_property(self):
        """Check the price using a fake property instead of PostgreSQL."""

        fake_property={
            "id":10,
            "name":"Test Apartment",
            "price_per_night": Decimal("150.00"),
            "capacity":4
        }
        with patch("booking.get_property_by_id", return_value=fake_property):
            total = calculate_price(
                property_id=10,
                check_in=date(2027,12,10),
                check_out=date(2027,12,13)
            )
        assert total == Decimal("450.00")

    def test_property_not_found(self):
        """Check that a missing property raises an error."""
        with patch("booking.get_property_by_id", return_value=None):
            with pytest.raises(ValueError, match="Property not found"):
                calculate_price(
                    property_id=999,
                    check_in=date(2027, 12, 10),
                    check_out=date(2027, 12, 13)
                )
    def test_invalid_dates_without_database(self):
        """Check that invalid dates are rejected without a database lookup."""
        with patch("booking.get_property_by_id") as mock_lookup:
            with pytest.raises(ValueError, match="Invalid booking dates"):
                calculate_price(
                    property_id=1,
                    check_in=date(2027, 12, 15),
                    check_out=date(2027, 12, 10)
                )

            mock_lookup.assert_not_called()
class TestMockedPropertySearch:
    """Tests for property searching without accessing PostgreSQL."""

    def test_search_by_capacity(self):
        """Check that properties with insufficient capacity are excluded."""
        fake_properties = [
            {
                "id": 1,
                "name": "Small Apartment",
                "price_per_night": Decimal("100.00"),
                "capacity": 2
            },
            {
                "id": 2,
                "name": "Large Villa",
                "price_per_night": Decimal("200.00"),
                "capacity": 6
            }
        ]

        with patch("booking.get_properties", return_value=fake_properties), \
             patch("booking.check_database_availability", return_value=True), \
             patch("booking.get_property_by_id", side_effect=lambda property_id: next(
                 p for p in fake_properties if p["id"] == property_id
             )):

            results = search_properties(
                guests=5,
                check_in=date(2027, 12, 10),
                check_out=date(2027, 12, 13)
            )

        assert len(results) == 1
        assert results[0]["name"] == "Large Villa"
        assert results[0]["total_price"] == Decimal("600.00")

    def test_no_properties(self):
        """Check that an empty property database returns no results."""
        with patch("booking.get_properties", return_value=[]):
            results = search_properties(
                guests=2,
                check_in=date(2027, 12, 10),
                check_out=date(2027, 12, 13)
            )

        assert results == []

    def test_all_properties_unavailable(self):
        """Check that unavailable properties are excluded from search."""
        fake_properties = [
            {
                "id": 1,
                "name": "Test Apartment",
                "price_per_night": Decimal("100.00"),
                "capacity": 4
            }
        ]

        with patch("booking.get_properties", return_value=fake_properties), \
             patch("booking.check_database_availability", return_value=False):

            results = search_properties(
                guests=2,
                check_in=date(2027, 12, 10),
                check_out=date(2027, 12, 13)
            )

        assert results == []