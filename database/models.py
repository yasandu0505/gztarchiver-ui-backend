from pydantic import BaseModel

class Docs(BaseModel):
    document_id: str
    description: str
    document_date: str
    document_type: str
    reasoning: str
    download_url: str
    source: str
    availability: str
    file_path: str = ""

    