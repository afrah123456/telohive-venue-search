import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "TeloHive Venue Search API"


def test_create_venue():
    venue_data = {
        "name": "Test Venue",
        "city": "Boston",
        "capacity_min": 20,
        "capacity_max": 100,
        "price_per_head": 80.0,
        "description": "A test venue in Boston for startup events.",
        "tags": ["test", "startup"],
        "amenities": ["wifi", "AV support"],
        "venue_type": "loft"
    }
    response = client.post("/venues/", json=venue_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Venue"
    assert data["city"] == "Boston"


def test_create_venue_missing_required_field():
    venue_data = {"city": "Boston"}
    response = client.post("/venues/", json=venue_data)
    assert response.status_code == 422


def test_create_venue_missing_city():
    venue_data = {"name": "Test Venue"}
    response = client.post("/venues/", json=venue_data)
    assert response.status_code == 422


def test_get_venue():
    venue_data = {
        "name": "Get Test Venue",
        "city": "Cambridge",
        "capacity_max": 50,
        "description": "Test venue for get test.",
        "tags": [],
        "amenities": []
    }
    create_response = client.post("/venues/", json=venue_data)
    venue_id = create_response.json()["id"]
    response = client.get(f"/venues/{venue_id}")
    assert response.status_code == 200
    assert response.json()["id"] == venue_id


def test_get_venue_not_found():
    response = client.get("/venues/nonexistent-id")
    assert response.status_code == 404


def test_list_venues():
    response = client.get("/venues/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_venues_pagination():
    response = client.get("/venues/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_list_venues_invalid_limit():
    response = client.get("/venues/?limit=0")
    assert response.status_code == 422


def test_update_venue():
    venue_data = {
        "name": "Update Test Venue",
        "city": "Boston",
        "capacity_max": 100,
        "description": "Before update.",
        "tags": [],
        "amenities": []
    }
    create_response = client.post("/venues/", json=venue_data)
    venue_id = create_response.json()["id"]
    update_data = {"description": "After update."}
    response = client.put(f"/venues/{venue_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["description"] == "After update."


def test_update_venue_not_found():
    response = client.put("/venues/nonexistent-id", json={"name": "New Name"})
    assert response.status_code == 404


def test_delete_venue():
    venue_data = {
        "name": "Delete Test Venue",
        "city": "Boston",
        "capacity_max": 50,
        "description": "To be deleted.",
        "tags": [],
        "amenities": []
    }
    create_response = client.post("/venues/", json=venue_data)
    venue_id = create_response.json()["id"]
    response = client.delete(f"/venues/{venue_id}")
    assert response.status_code == 204
    get_response = client.get(f"/venues/{venue_id}")
    assert get_response.status_code == 404


def test_delete_venue_not_found():
    response = client.delete("/venues/nonexistent-id")
    assert response.status_code == 404


def test_search_venues():
    search_data = {
        "query": "Rooftop venue in Boston for a startup mixer with 80 people",
        "city": "Boston",
        "capacity": 80
    }
    response = client.post("/venues/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert "query" in data


def test_search_venues_empty_query():
    search_data = {"query": ""}
    response = client.post("/venues/search", json=search_data)
    assert response.status_code in [200, 422]


def test_search_venues_no_results():
    search_data = {
        "query": "venue in Antarctica",
        "city": "Antarctica"
    }
    response = client.post("/venues/search", json=search_data)
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_search_venues_budget_filter():
    search_data = {
        "query": "venue in Boston",
        "city": "Boston",
        "max_price_per_head": 50.0
    }
    response = client.post("/venues/search", json=search_data)
    assert response.status_code == 200


def test_create_lead():
    lead_data = {
        "query": "Rooftop venue in Boston for 80 people",
        "filters": {"city": "Boston", "capacity": 80},
        "contact_email": "test@example.com",
        "contact_name": "Test User"
    }
    response = client.post("/leads/", json=lead_data)
    assert response.status_code == 201
    data = response.json()
    assert data["query"] == lead_data["query"]


def test_create_lead_missing_query():
    lead_data = {"contact_email": "test@example.com"}
    response = client.post("/leads/", json=lead_data)
    assert response.status_code == 422


def test_get_lead_not_found():
    response = client.get("/leads/nonexistent-id")
    assert response.status_code == 404


def test_list_leads():
    response = client.get("/leads/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
