from pydantic import BaseModel, Field
from typing import List, Dict, Any

class LocationContext(BaseModel):
    district: List[str] = Field(default_factory=list)
    commune: List[str] = Field(default_factory=list)

class CanonicalSlotRepresentation(BaseModel):
    time_context: List[int] = Field(default_factory=list)
    location_context: LocationContext = Field(default_factory=LocationContext)
    metrics: List[str] = Field(default_factory=list)
    logical_conditions: List[Dict[str, Any]] = Field(default_factory=list)
