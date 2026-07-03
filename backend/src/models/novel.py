from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class Novel(Base):
    __tablename__ = "novels"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    genre = Column(String(100), default="General")
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # Full novel content
    word_count = Column(Integer, default=0)
    status = Column(String(50), default="draft")  # draft, writing, editing, complete
    
    # Cognee dataset name for this novel
    dataset_name = Column(String(255), unique=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_written_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    target_word_count = Column(Integer, nullable=True)
    outline = Column(Text, nullable=True)  # JSON or plain text outline
    writing_style = Column(String(255), nullable=True)
    
    # Relationships
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="novel", cascade="all, delete-orphan")
    plot_points = relationship("PlotPoint", back_populates="novel", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    chapter_number = Column(Integer, nullable=False)
    word_count = Column(Integer, default=0)
    
    # Chapter metadata
    summary = Column(Text, nullable=True)
    status = Column(String(50), default="draft")  # draft, writing, editing, complete
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="chapters")