from fastapi.testclient import TestClient

def test_get_dashboard_status(client: TestClient):
    response = client.get("/dashboard-status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_docs"] == 3
    assert data["available_docs"] == 2
    assert "Legal Regulatory" in data["document_types"]
    assert "Organisational" in data["document_types"]
    assert "Unavailable" in data["document_types"]
    
    # Check years covered (2015, 2016, 2018) -> min 2015, max 2018
    assert data["years_covered"]["from"] == 2015
    assert data["years_covered"]["to"] == 2018
