CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price_per_night NUMERIC(10,2) NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL
        REFERENCES properties(id),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    CONSTRAINT valid_booking_dates
        CHECK (check_out>check_in),
    CONSTRAINT no_overlapping_bookings
        EXCLUDE USING gist (
            property_id WITH =,
            daterange(check_in,check_out, '[)') WITH &&
        )
);