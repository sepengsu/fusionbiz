from pydantic import BaseModel
from datetime import datetime
import uuid

class RecordingCreate(BaseModel):
    duration: int = 10
    sample_rate: int = 44100

class RecordingResponse(BaseModel):
    id: str = str(uuid.uuid4())
    filename: str
    duration: int
    created_at: datetime = datetime.now()
    file_path: str