from fastapi.testclient import TestClient

def test_search_all(client: TestClient):
    payload = {"query": "Test"}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3
    assert data["pagination"]["total_count"] == 3

def test_search_by_text(client: TestClient):
    payload = {"query": "Test Doc 1"}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["document_id"] == "1895-18"

def test_search_by_type(client: TestClient):
    payload = {"query": "type:LEGAL_REGULATORY"}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["document_type"] == "LEGAL_REGULATORY"

def test_search_by_availability(client: TestClient):
    payload = {"query": "available:yes"}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Should match Available docs (2)
    assert len(data["results"]) == 2

def test_search_by_date_regex(client: TestClient):
    # Search for year 2015
    payload = {"query": "date:2015"}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["document_date"] == "2015-01-01"

def test_search_pagination(client: TestClient):
    # Set limit to 1
    payload = {"query": "Test", "limit": 1, "page": 1}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["pagination"]["total_pages"] == 3
    assert data["pagination"]["has_next"] is True
    
    # Next page
    payload["page"] = 2
    response = client.post("/search", json=payload)
    data = response.json()
    assert len(data["results"]) == 1
    assert data["pagination"]["current_page"] == 2
