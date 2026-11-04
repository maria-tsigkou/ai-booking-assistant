# AI Booking Assistant

A property booking backend built with Python, FastAPI, PostgreSQL, Docker and pytest.

## Features

-Search properties by guest capacity and dates
-Calculate booking prices
-Create and retrieve bookings
-Prevent overlapping bookings
-Automated unit and API tests
-Mocked database dependencies

## Technologies

Python, FastAPI, PostgreSQL, Docker, pytest.

## Local setup

1. Copy `.env.example` to `.env` and configure database credentials.
2. Run `docker compose up -d`.
3. On a fresh database, apply `sql/schema.sql`
4. Install dependencies with `pip install -r requirements.txt`
5. Load the database enviroment variables.
6. Start the API with `uvicorn main:app --reload`.
7. Open http://localhost:8000/docs.

## Roadmap
- [x] Booking backend
- [x] PostgreSQL integration
- [x] Automated tests
- [ ] Dockerize FastAPI
- [ ] Github Actions CI/CD
- [ ] LLM-powered booking assistant
- [ ] Azure deployment