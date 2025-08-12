from pydantic import BaseModel

class Docs(BaseModel):
    document_id : str
    document_date : str
    document_type : str
    reasoning : str
    gdrive_file_id : str
    gdrive_file_url : str
    download_url : str
    