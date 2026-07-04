from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.models import Novel, WorldElement

router = APIRouter()

# Request/Response Models
class WorldElementCreate(BaseModel):
    category: str  # location, lore, magic, culture, fauna
    name: str
    description: Optional[str] = ""
    properties: Optional[dict] = None
    connections: Optional[list] = None
    tags: Optional[list] = None
    notes: Optional[str] = ""

class WorldElementUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[dict] = None
    connections: Optional[list] = None
    tags: Optional[list] = None
    notes: Optional[str] = None

class WorldElementResponse(BaseModel):
    id: int
    novel_id: int
    category: str
    name: str
    description: Optional[str]
    properties: Optional[dict]
    connections: Optional[list]
    tags: Optional[list]
    notes: Optional[str]

    class Config:
        from_attributes = True


def _serialize(el: WorldElement) -> dict:
    return {
        "id": el.id,
        "novel_id": el.novel_id,
        "category": el.category,
        "name": el.name,
        "description": el.description,
        "properties": el.properties,
        "connections": el.connections,
        "tags": el.tags,
        "notes": el.notes,
    }


@router.get("/{novel_id}", response_model=List[WorldElementResponse])
async def get_world_elements(
    novel_id: int,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all world-building elements for a novel, optionally filtered by category"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    query = db.query(WorldElement).filter(WorldElement.novel_id == novel_id)
    if category:
        query = query.filter(WorldElement.category == category)
    
    elements = query.order_by(WorldElement.sort_order, WorldElement.name).all()
    return [_serialize(el) for el in elements]


@router.post("/{novel_id}", response_model=WorldElementResponse)
async def create_world_element(
    novel_id: int,
    data: WorldElementCreate,
    db: Session = Depends(get_db)
):
    """Create a new world-building element"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    element = WorldElement(
        novel_id=novel_id,
        category=data.category,
        name=data.name,
        description=data.description,
        properties=data.properties,
        connections=data.connections,
        tags=data.tags,
        notes=data.notes,
    )
    
    db.add(element)
    db.commit()
    db.refresh(element)
    
    return _serialize(element)


@router.put("/{novel_id}/{element_id}", response_model=WorldElementResponse)
async def update_world_element(
    novel_id: int,
    element_id: int,
    data: WorldElementUpdate,
    db: Session = Depends(get_db)
):
    """Update a world-building element"""
    element = (
        db.query(WorldElement)
        .filter(WorldElement.novel_id == novel_id, WorldElement.id == element_id)
        .first()
    )
    if not element:
        raise HTTPException(status_code=404, detail="World element not found")
    
    update_data = data.dict(exclude_none=True)
    for key, value in update_data.items():
        setattr(element, key, value)
    
    db.commit()
    db.refresh(element)
    
    return _serialize(element)


@router.delete("/{novel_id}/{element_id}")
async def delete_world_element(
    novel_id: int,
    element_id: int,
    db: Session = Depends(get_db)
):
    """Delete a world-building element"""
    element = (
        db.query(WorldElement)
        .filter(WorldElement.novel_id == novel_id, WorldElement.id == element_id)
        .first()
    )
    if not element:
        raise HTTPException(status_code=404, detail="World element not found")
    
    db.delete(element)
    db.commit()
    
    return {"message": "World element deleted successfully"}
