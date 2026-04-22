from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from groq import Groq
from app.models import Venue
from app.schemas import SearchRequest, SearchResult, VenueResponse
from app.core.config import settings


def apply_structured_filters(query, request: SearchRequest):
    filters = []
    if request.city:
        filters.append(Venue.city.ilike(f"%{request.city}%"))
    if request.capacity:
        filters.append(Venue.capacity_max >= request.capacity)
    if request.max_price_per_head:
        filters.append(
            or_(
                Venue.price_per_head <= request.max_price_per_head,
                Venue.price_per_head == None
            )
        )
    if request.venue_type:
        filters.append(Venue.venue_type.ilike(f"%{request.venue_type}%"))
    if filters:
        query = query.filter(and_(*filters))
    return query


def generate_match_explanation(venue: Venue, user_query: str, client: Groq) -> str:
    try:
        prompt = f"""
User is looking for: "{user_query}"
Venue: {venue.name} in {venue.city}, type: {venue.venue_type}, capacity: {venue.capacity_min}-{venue.capacity_max}, price: ${venue.price_per_head}/head
Amenities: {", ".join(venue.amenities or [])}
Tags: {", ".join(venue.tags or [])}
Description: {venue.description}

Write one clear sentence explaining why this venue matches the user request. Be specific and mention 2-3 matching attributes.
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"{venue.name} matches your search criteria."


def score_venue(venue: Venue, request: SearchRequest) -> float:
    score = 0.5
    query_lower = request.query.lower()
    if venue.name and any(word in venue.name.lower() for word in query_lower.split()):
        score += 0.2
    if venue.description and any(word in venue.description.lower() for word in query_lower.split()):
        score += 0.15
    if venue.tags:
        matching_tags = [t for t in venue.tags if t.lower() in query_lower]
        score += len(matching_tags) * 0.05
    if venue.amenities:
        matching_amenities = [a for a in venue.amenities if a.lower() in query_lower]
        score += len(matching_amenities) * 0.05
    return min(score, 1.0)


def search_venues(db: Session, request: SearchRequest) -> List[SearchResult]:
    client = Groq(api_key=settings.GROQ_API_KEY)
    query = db.query(Venue)
    query = apply_structured_filters(query, request)
    filtered_venues = query.all()
    if not filtered_venues:
        return []
    scored_venues = [(venue, score_venue(venue, request)) for venue in filtered_venues]
    scored_venues.sort(key=lambda x: x[1], reverse=True)
    paginated = scored_venues[request.offset: request.offset + request.limit]
    results = []
    for venue, score in paginated:
        explanation = generate_match_explanation(venue, request.query, client)
        results.append(
            SearchResult(
                venue=VenueResponse.model_validate(venue),
                score=round(score, 4),
                match_explanation=explanation,
            )
        )
    return results
