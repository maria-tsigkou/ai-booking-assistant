import psycopg
from datetime import date
from psycopg.rows import dict_row
import os

def get_connection():
    """Create a connection to  PostgreSQL using enviroment variables."""
    return psycopg.connect(
        host=os.getenv("DB_HOST","localhost"),
        port=int(os.getenv("DB_PORT","5432")),
        dbname=os.getenv("DB_NAME","booking_db"),
        user=os.getenv("DB_USER","booking_user"),
        password=os.environ["DB_PASSWORD"]
    )

def get_bookings():
    """Retrieves all bookings stored in PostgreSQL as dictionaries."""
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * FROM bookings;")
            return cursor.fetchall() #retrieves all rows returned by the SQL query.

def get_properties():
    """Retrieves all properties from PostgreSQL as dictionaries."""
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * FROM properties;")
            return cursor.fetchall()

def get_property_by_id(property_id: int):
    """Retrieves one property from PostgreSQL by its ID."""
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM properties WHERE id = %s;",
                (property_id,)
            )
            return cursor.fetchone()

def check_database_availability(
        property_id: int,
        check_in: date,
        check_out: date
) -> bool:
    """Check whether a property has overlapping bookigns in PostgreSQL"""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM bookings
                WHERE property_id = %s
                    AND check_in < %s
                    AND check_out > %s
                LIMIT 1;
                """,
                (property_id, check_out, check_in)
            )
            return cursor.fetchone() is None

def insert_booking(property_id: int, check_in: date, check_out: date):
    """Insert a new booking into PostgreSQL and return its ID."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO bookings (property_id, check_in, check_out)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (property_id, check_in, check_out)
            )
            result = cursor.fetchone()

            if result is None:
                raise RuntimeError("Failed to retrieve the new booking ID")

            return result[0]
