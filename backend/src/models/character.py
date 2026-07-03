from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    role = Column(String(100), nullable=True)  # protagonist, antagonist, supporting, etc.
    
    # Character attributes as JSON
    traits = Column(JSON, nullable=True)  # ["brave", "intelligent", "mysterious"]
    physical_description = Column(Text, nullable=True)
    background = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    goals = Column(JSON, nullable=True)  # ["find the treasure", "avenge family"]
    fears = Column(JSON, nullable=True)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    
    # Story metadata
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    occupation = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Internal tracking
    first_appearance = Column(Integer, nullable=True)  # Chapter number
    last_appearance = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    importance_score = Column(Float, default=0.5)  # 0.0 to 1.0
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="characters")
    relationships_from = relationship("CharacterRelationship", 
                                     foreign_keys="CharacterRelationship.source_id",
                                     back_populates="source", 
                                     cascade="all, delete-orphan")
    relationships_to = relationship("CharacterRelationship", 
                                   foreign_keys="CharacterRelationship.target_id",
                                   back_populates="target", 
                                   cascade="all, delete-orphan")

class CharacterRelationship(Base):
    __tablename__ = "character_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(100), nullable=False)  # friend, enemy, family, etc.
    description = Column(Text, nullable=True)
    strength = Column(Float, default=0.5)  # 0.0 to 1.0
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    source = relationship("Character", foreign_keys=[source_id], back_populates="relationships_from")
    target = relationship("Character", foreign_keys=[target_id], back_populates="relationships_to")