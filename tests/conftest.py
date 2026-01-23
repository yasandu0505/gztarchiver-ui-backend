import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from services.metadata_store import MetadataStore

@pytest.fixture
def mock_metadata_store():
    with patch('services.metadata_store.MetadataStore.get_all_documents') as mock_get:
        # Sample data
        mock_data = [
            {
                "document_id": "1895-18",
                "description": "Test Doc 1",
                "document_date": "2015-01-01",
                "document_type": "ORGANISATIONAL",
                "availability": "Available"
            },
            {
                "document_id": "1947-44",
                "description": "Test Doc 2",
                "document_date": "2016-01-01",
                "document_type": "LEGAL_REGULATORY",
                "availability": "Available"
            },
            {
                "document_id": "2056-34",
                "description": "Test Doc 3",
                "document_date": "2018-02-01",
                "document_type": "UNAVAILABLE",
                "availability": "Unavailable"
            }
        ]
        mock_get.return_value = mock_data
        yield mock_get

@pytest.fixture
def client(mock_metadata_store):
    return TestClient(app)
