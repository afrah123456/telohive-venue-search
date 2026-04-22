# TeloHive Venue Search API

A backend service for AI-native venue matching and discovery. Users describe what they're looking for in plain English the system filters, ranks, and explains why each venue matched.

Built as a take-home assessment for TeloHive (Task 1: AI Venue Search Backend).

---

## Problem Summary

Booking venues today is slow and manual spreadsheets, back-and-forth emails, and generic search results. This service makes venue discovery feel intelligent. A user describes their event in plain English and gets back a ranked list of venues with a clear explanation of why each one fits.

The core challenge is handling both hard constraints (capacity, budget, city) and fuzzy intent ("startup mixer", "industrial vibe", "demo day") in the same query.

---

## Architecture Overview

The service is a REST API built with FastAPI and PostgreSQL. Search runs in three layers:

Layer 1 - Structured filtering: SQL WHERE clauses filter venues by hard constraints first city, capacity, budget, venue type. A venue that does not meet capacity is never the right answer regardless of description quality.

Layer 2 - Keyword scoring: Each filtered venue is scored by how well its name, description, tags, and amenities match the query terms. Scores range from 0 to 1.

Layer 3 - Match explanation: Groq (Llama 3.3 70B) generates a one-sentence explanation for each result, telling the user specifically why this venue matched their request.

---

## Tech Stack

- Python + FastAPI
- PostgreSQL
- SQLAlchemy
- Groq (Llama 3.3 70B)
- Docker Compose (included, see note below)

---

## Note on Docker

Docker Compose is included and fully configured. During local development I ran into a disk space issue on the system C drive (less than 1 GB free) that prevented Docker from building images. Moving the Docker WSL disk to the D drive hit a Windows WSL2 access restriction I could not resolve cleanly in the available time.

Rather than spend time debugging the environment, I ran everything directly  PostgreSQL installed locally, Python virtualenv, uvicorn. The Docker Compose setup is complete and would work on a machine with sufficient disk space.

---

## Local Setup

1. Clone the repo
   git clone your-repo-url
   cd telohive

2. Create a .env file
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/telohive
   GROQ_API_KEY=your_groq_api_key_here
   Get a free Groq API key at https://console.groq.com

3. Install dependencies
   pip install -r requirements.txt

4. Create the database
   Open psql and run: CREATE DATABASE telohive;

5. Run the app
   python -m uvicorn app.main:app --reload

6. Seed sample data
   python data/seed.py

API docs available at http://localhost:8000/docs

---

## Docker Setup (alternative)

docker-compose up --build

API docs available at http://localhost:8000/docs

---

## How to Run Tests

pytest tests/ -v

Tests cover: create venue, get venue, list venues, update venue, delete venue, search venues, create lead, and 404 handling.

---

## API Endpoints

| Method | Endpoint         | Description          |
|--------|------------------|----------------------|
| GET    | /                | Health check         |
| GET    | /health          | Detailed health      |
| POST   | /venues/         | Create a venue       |
| GET    | /venues/         | List all venues      |
| GET    | /venues/{id}     | Get venue by ID      |
| PUT    | /venues/{id}     | Update a venue       |
| DELETE | /venues/{id}     | Delete a venue       |
| POST   | /venues/search   | Search venues        |
| POST   | /leads/          | Save a lead          |
| GET    | /leads/          | List all leads       |
| GET    | /leads/{id}      | Get lead by ID       |

---

## API Usage Examples

Search request:
POST /venues/search
{
  "query": "Rooftop venue in Boston for a startup mixer with 80 people",
  "city": "Boston",
  "capacity": 80
}

Search response:
{
  "results": [
    {
      "venue": { "name": "The Rooftop at Seaport", "city": "Boston" },
      "score": 0.95,
      "match_explanation": "The Rooftop at Seaport is a strong match with its rooftop location in Boston, capacity for 150 guests, and AV support."
    }
  ],
  "total": 1,
  "query": "Rooftop venue in Boston for a startup mixer with 80 people"
}

Create a lead:
POST /leads/
{
  "query": "Rooftop venue in Boston for 80 people",
  "filters": { "city": "Boston", "capacity": 80 },
  "contact_email": "user@example.com",
  "contact_name": "Jane Smith"
}

---

## Design Decisions

Why JSONB for attributes?
Venue operational attributes vary widely. JSONB lets us store flexible key-value pairs without a schema migration every time a new attribute type appears.

Why Groq instead of OpenAI?
Groq runs Llama 3.3 70B on custom LPU hardware with sub-second response times. For a search experience, latency matters. It is also free on the free tier which made iteration faster.

Why keyword scoring instead of vector embeddings?
pgvector requires a PostgreSQL extension that is not bundled with standard installations. Keyword scoring is reliable, explainable, and fast. Vector search is the clear next step for production.

Why structured filters run before scoring?
Hard constraints should eliminate candidates before relevance scoring begins. A venue that seats 40 people is never the right answer for a 200-person event regardless of description quality.

Why ARRAY for tags and amenities?
PostgreSQL native arrays allow clean filtering with the ANY operator without a join table. For this data size it is the right tradeoff between simplicity and queryability.

---

## Known Limitations

- No authentication - any client can create, update, or delete venues
- Keyword scoring does not understand synonyms or semantic similarity
- No persistent caching - resets on server restart
- pgvector not installed - semantic search is not active in this version
- Tests require a running PostgreSQL instance

---

## What I Would Improve With 1-2 More Days

1. pgvector semantic search - replace keyword scoring with vector embeddings
2. Alembic migrations - proper migration history instead of create_all on startup
3. JWT authentication - protect write endpoints, add admin-only access
4. Better test coverage - integration tests with a test database
5. AWS deployment - EC2 for the API, RDS for PostgreSQL, Route 53 for DNS
6. Rate limiting - protect the search endpoint from abuse
7. Lead notifications - webhook or email when a new lead comes in
