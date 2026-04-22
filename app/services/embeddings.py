def get_embedding(text: str):
    return None

def get_venue_text(venue) -> str:
    parts = [
        venue.name or "",
        venue.city or "",
        venue.description or "",
        venue.venue_type or "",
        " ".join(venue.tags or []),
        " ".join(venue.amenities or []),
    ]
    return " ".join(filter(None, parts))
