from pydantic import BaseModel

class Docs(BaseModel):
    document_id : str
    document_description : str
    document_date : str
    document_type : str
    reasoning : str
    file_path : str
    download_url : str
    source : str
    availability : str
    