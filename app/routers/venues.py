import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Venue
from app.schemas import VenueCreate, VenueUpdate, VenueResponse, SearchRequest, SearchResponse
from app.services.search import search_venues

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/venues", tags=["Venues"])


@router.post("/", response_model=VenueResponse, status_code=201)
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
    """Create a new venue and store it in the database."""
    logger.info(f"Creating venue: {venue.name} in {venue.city}")
    db_venue = Venue(**venue.model_dump())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue


@router.get("/", response_model=List[VenueResponse])
def list_venues(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """List all venues with pagination support."""
    logger.info(f"Listing venues — skip: {skip}, limit: {limit}")
    return db.query(Venue).offset(skip).limit(limit).all()


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: str, db: Session = Depends(get_db)):
    """Get a single venue by its ID."""
    logger.info(f"Getting venue: {venue_id}")
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        logger.warning(f"Venue not found: {venue_id}")
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue


@router.put("/{venue_id}", response_model=VenueResponse)
def update_venue(venue_id: str, venue_update: VenueUpdate, db: Session = Depends(get_db)):
    """Update an existing venue by its ID."""
    logger.info(f"Updating venue: {venue_id}")
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        logger.warning(f"Venue not found for update: {venue_id}")
        raise HTTPException(status_code=404, detail="Venue not found")
    update_data = venue_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venue, field, value)
    db.commit()
    db.refresh(venue)
    return venue


@router.delete("/{venue_id}", status_code=204)
def delete_venue(venue_id: str, db: Session = Depends(get_db)):
    """Delete a venue by its ID."""
    logger.info(f"Deleting venue: {venue_id}")
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        logger.warning(f"Venue not found for deletion: {venue_id}")
        raise HTTPException(status_code=404, detail="Venue not found")
    db.delete(venue)
    db.commit()


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest, db: Session = Depends(get_db)):
    """Search venues using structured filters and keyword-based ranking.
    
    Combines hard constraint filtering (city, capacity, budget) with
    keyword scoring and Groq-generated match explanations.
    """
    logger.info(f"Search request: {request.query}")
    results = search_venues(db, request)
    logger.info(f"Search returned {len(results)} results")
    return SearchResponse(results=results, total=len(results), query=request.query)
