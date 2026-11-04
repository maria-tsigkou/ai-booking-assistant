from fastapi import FastAPI, HTTPException
from psycopg.errors import ExclusionViolation
from booking import search_properties, calculate_price
from datetime import date
from pydantic import BaseModel
from database import (
    get_bookings,
    insert_booking,
    check_database_availability,
    get_properties
)

app = FastAPI()

class BookingRequest(BaseModel):
    property_id: int
    check_in: date
    check_out: date

@app.get("/")
def home():
    """Return a welcome message for the booking API."""
    return {"message": "Welcome to the AI Booking Assistant API"}

@app.get("/properties")
def list_properties():
    """"Return all properties stored in PostgreSQL."""
    return get_properties()

@app.get("/properties/search")
def search_available_properties(
    guests: int,
    check_in: date,
    check_out: date
):
    """Search for available properties based on guests and dates."""
    try:
        return search_properties(guests,check_in,check_out)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

@app.get("/bookings")
def list_bookings():
    """Return all reservations stored in the booking system."""
    return get_bookings()

@app.post("/bookings", status_code=201)
def add_booking(request: BookingRequest):
    """Create a new booking using the submitted reservation details and
        save it in PostgreSQL."""
    try:
        total_price = calculate_price(
            request.property_id,
            request.check_in,
            request.check_out
        )
        if not check_database_availability(
            request.property_id,
            request.check_in,
            request.check_out
        ):
            raise ValueError("Property is not available for these dates")

        booking_id = insert_booking(
            request.property_id,
            request.check_in,
            request.check_out
        )

        return {
            "id": booking_id,
            "property_id": request.property_id,
            "check_in": request.check_in,
            "check_out": request.check_out,
            "total_price": total_price
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    except ExclusionViolation as error:
        raise HTTPException(
            status_code=409, #409 means Conflict
            detail="Property is not available for these dates"
        ) from error