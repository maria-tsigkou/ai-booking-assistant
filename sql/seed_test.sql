-- Sample properties for automated tests.
-- Run only against a disposable test database.

INSERT INTO propreties (id, name, price_per_night, capacity)
VALUES
    (1, 'Sea View Apartment', 120.00, 4),
    (2, 'Mountain Villa', 200.00, 6);

-- Existing booking for availability tests
INSERT INTO bookings (propery_id, check_in, check_out)
    VALUES (1, '2027-09-10','2720-09-15');

-- Keep automatically generated IDs in sync.
SELECT setval(
    pg_get_serial_sequence('properties','id'),
    (SELECT MAX(id) FROM properties)
);