import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, PropertyMock
from main import app

@pytest.fixture
def mock_metadata_store():
    mock_data = [
        {
            "document_id": "1895-18",
            "description": "Department of Census and Statistics - The Colombo Consumer's Price Index for the Month of December 2014 was 180.2",
            "document_date": "2015-01-01",
            "document_type": "ORGANISATIONAL",
            "categorisation": "This gazette notification announces the Colombo Consumers' Price Index...",
            "source": "https://example.com/1895-18_E.pdf",
            "availability": "Available",
            "file_path": "path/to/1895-18"
        },
        {
            "document_id": "1947-44",
            "description": "Central Bank of Sri Lanka - Order under the Registered Stock & Securities Ordinance to raise of loan in Sri Lanka",
            "document_date": "2016-01-01",
            "document_type": "LEGAL_REGULATORY",
            "categorisation": "This gazette content primarily involves the exercise of regulatory powers...",
            "source": "https://example.com/1947-44_E.pdf",
            "availability": "Available",
            "file_path": "path/to/1947-44"
        },
        {
            "document_id": "2056-34",
            "description": "Land Acquisition - Aarabokka, Hambanthota D/S Division, Hambanthota District and 3 other notices (S only)",
            "document_date": "2018-02-01",
            "document_type": "UNAVAILABLE",
            "categorisation": "NOT-FOUND",
            "source": "N/A",
            "availability": "Unavailable",
            "file_path": "path/to/2056-34"
        }
    ]

    with patch(
        "services.metadata_store.MetadataStore.documents",
        new_callable=PropertyMock
    ) as mock_documents:
        mock_documents.return_value = mock_data
        yield mock_documents


@pytest.fixture
def client(mock_metadata_store):
    return TestClient(app)
