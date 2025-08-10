from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional

class Track(BaseModel):
    title: str
    side: Optional[str] = None
    track_number: Optional[int] = None
    duration_seconds: Optional[float] = None

class Project(BaseModel):
    name: str
    pdfs: List[Path] = []
    wavs: List[Path] = []

class ExtractionResult(BaseModel):
    source: str
    status: str
    tracks: List[Track] = []
    error: Optional[str] = None

class ReportRow(BaseModel):
    project_name: str
    track_title: str
    wav_file: Optional[str]
    duration_seconds: Optional[float]

