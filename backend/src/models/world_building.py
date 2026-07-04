from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class WorldElement(Base):
    __tablename__ = "world_elements"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    
    # Core fields
    category = Column(String(100), nullable=False)  # location, lore, magic, culture, fauna
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Flexible properties stored as JSON
    properties = Column(JSON, nullable=True)  # category-specific key-value pairs
    connections = Column(JSON, nullable=True)  # list of connected element IDs or names
    tags = Column(JSON, nullable=True)  # searchable tags
    
    # Optional metadata
    image_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="world_elements")
