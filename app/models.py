from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Venue(Base):
    __tablename__ = "venues"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    address = Column(String)
    capacity_min = Column(Integer)
    capacity_max = Column(Integer, index=True)
    price_per_head = Column(Float, index=True)
    price_flat = Column(Float)
    description = Column(Text)
    tags = Column(ARRAY(String), default=[])
    amenities = Column(ARRAY(String), default=[])
    venue_type = Column(String, index=True)
    attributes = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=generate_uuid)
    query = Column(Text, nullable=False)
    filters = Column(JSONB, default={})
    contact_email = Column(String, index=True)
    contact_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
