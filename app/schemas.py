from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VenueBase(BaseModel):
    name: str
    city: str
    address: Optional[str] = None
    capacity_min: Optional[int] = None
    capacity_max: Optional[int] = None
    price_per_head: Optional[float] = None
    price_flat: Optional[float] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    amenities: Optional[List[str]] = []
    venue_type: Optional[str] = None
    attributes: Optional[dict] = {}


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    capacity_min: Optional[int] = None
    capacity_max: Optional[int] = None
    price_per_head: Optional[float] = None
    price_flat: Optional[float] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    venue_type: Optional[str] = None
    attributes: Optional[dict] = None


class VenueResponse(VenueBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural language search query")
    city: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=1, description="Minimum capacity needed")
    max_price_per_head: Optional[float] = Field(None, ge=0, description="Maximum price per head")
    amenities: Optional[List[str]] = None
    venue_type: Optional[str] = None
    limit: Optional[int] = Field(10, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)


class SearchResult(BaseModel):
    venue: VenueResponse
    score: Optional[float] = None
    match_explanation: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str


class LeadCreate(BaseModel):
    query: str = Field(..., min_length=1, description="The user search query or inquiry")
    filters: Optional[dict] = {}
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None


class LeadResponse(LeadCreate):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
