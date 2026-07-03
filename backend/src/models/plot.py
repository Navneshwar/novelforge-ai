from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class PlotPoint(Base):
    __tablename__ = "plot_points"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(100), nullable=True)  # inciting, rising_action, climax, resolution
    
    # Timeline
    chapter = Column(Integer, nullable=True)
    timeline_order = Column(Integer, nullable=True)  # order within chapter
    
    # Status
    status = Column(String(50), default="planned")  # planned, drafted, written, revised
    is_major = Column(Boolean, default=False)
    
    # Metadata
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    emotional_weight = Column(Float, default=0.5)
    plot_arc = Column(String(100), nullable=True)  # arc name or ID
    
    # Related entities
    involved_characters = Column(JSON, nullable=True)  # List of character IDs
    locations = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)  # ["mystery", "romance", "action"]
    
    # Notes
    notes = Column(Text, nullable=True)
    foreshadowing = Column(Text, nullable=True)  # hints for future events
    resolution = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="plot_points")

class PlotArc(Base):
    __tablename__ = "plot_arcs"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    arc_type = Column(String(100), nullable=True)  # main, subplot, character, thematic
    
    # Timeline
    start_chapter = Column(Integer, nullable=True)
    end_chapter = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(50), default="planned")  # planned, active, resolved
    
    # Related plot points
    plot_point_ids = Column(JSON, nullable=True)  # List of plot point IDs
    
    # Notes
    notes = Column(Text, nullable=True)
    themes = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())