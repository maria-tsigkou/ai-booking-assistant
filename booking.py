
from datetime import date
from database import (
    check_database_availability,
    get_property_by_id,
    get_properties)

def calculate_price(property_id: int,check_in: date,check_out: date):
    """Calculate the total booking price based on the number of nights, using property data
        from PostgreSQL."""
    if check_out<=check_in:
        raise ValueError("Invalid booking dates")

    property_data = get_property_by_id(property_id)
    if property_data is None:
        raise ValueError("Property not found")

    property_price = property_data["price_per_night"]
    total_nights = (check_out - check_in).days
    total_price = total_nights * property_price

    return total_price

def search_properties(guests: int,check_in: date,check_out: date):
    """Find available properties that can accommodate the requested guests."""
    if guests<=0:
        raise ValueError("Guests must be at least 1")
    if check_out<=check_in:
        raise ValueError("Invalid booking dates")

    results = []
    for property_data in get_properties():

        property_id = property_data["id"]
        if property_data["capacity"] < guests:
            continue
        if not check_database_availability(property_id, check_in, check_out):
            continue

        total_price = calculate_price(property_id,check_in,check_out)
        results.append({
            "id": property_id,
            "name": property_data["name"],
            "total_price": total_price
        })

    return results
