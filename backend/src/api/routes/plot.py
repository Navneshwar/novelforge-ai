from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.models import PlotPoint, PlotArc, Novel
from src.services.memory_service import MemoryService
from loguru import logger

router = APIRouter()

# Request/Response Models
class PlotPointCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: Optional[str] = None  # inciting, rising_action, climax, resolution
    chapter: Optional[int] = None
    timeline_order: Optional[int] = None
    status: Optional[str] = "planned"
    is_major: Optional[bool] = False
    importance: Optional[float] = 0.5
    emotional_weight: Optional[float] = 0.5
    plot_arc: Optional[str] = None
    involved_characters: Optional[List[int]] = []
    locations: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    notes: Optional[str] = None
    foreshadowing: Optional[str] = None
    resolution: Optional[str] = None

class PlotPointUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    chapter: Optional[int] = None
    timeline_order: Optional[int] = None
    status: Optional[str] = None
    is_major: Optional[bool] = None
    importance: Optional[float] = None
    emotional_weight: Optional[float] = None
    plot_arc: Optional[str] = None
    involved_characters: Optional[List[int]] = None
    locations: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    foreshadowing: Optional[str] = None
    resolution: Optional[str] = None

class PlotPointResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    event_type: Optional[str]
    chapter: Optional[int]
    timeline_order: Optional[int]
    status: str
    is_major: bool
    importance: float
    emotional_weight: float
    plot_arc: Optional[str]
    involved_characters: Optional[List[int]]
    locations: Optional[List[str]]
    tags: Optional[List[str]]
    notes: Optional[str]
    foreshadowing: Optional[str]
    resolution: Optional[str]
    created_at: str
    updated_at: Optional[str]

class PlotArcCreate(BaseModel):
    name: str
    description: Optional[str] = None
    arc_type: Optional[str] = None  # main, subplot, character, thematic
    start_chapter: Optional[int] = None
    end_chapter: Optional[int] = None
    status: Optional[str] = "planned"
    plot_point_ids: Optional[List[int]] = []
    notes: Optional[str] = None
    themes: Optional[List[str]] = []

class PlotArcResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    arc_type: Optional[str]
    start_chapter: Optional[int]
    end_chapter: Optional[int]
    status: str
    plot_point_ids: Optional[List[int]]
    notes: Optional[str]
    themes: Optional[List[str]]
    created_at: str
    updated_at: Optional[str]


# ── Plot Points ──────────────────────────────────────────────────────

@router.get("/{novel_id}", response_model=List[PlotPointResponse])
async def get_plot_points(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get all plot points for a novel"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    plot_points = db.query(PlotPoint).filter(
        PlotPoint.novel_id == novel_id
    ).order_by(PlotPoint.timeline_order, PlotPoint.chapter).all()
    
    return [PlotPointResponse(
        id=pp.id,
        title=pp.title,
        description=pp.description,
        event_type=pp.event_type,
        chapter=pp.chapter,
        timeline_order=pp.timeline_order,
        status=pp.status,
        is_major=pp.is_major,
        importance=pp.importance,
        emotional_weight=pp.emotional_weight,
        plot_arc=pp.plot_arc,
        involved_characters=pp.involved_characters,
        locations=pp.locations,
        tags=pp.tags,
        notes=pp.notes,
        foreshadowing=pp.foreshadowing,
        resolution=pp.resolution,
        created_at=pp.created_at.isoformat() if pp.created_at else "",
        updated_at=pp.updated_at.isoformat() if pp.updated_at else None
    ) for pp in plot_points]

@router.post("/{novel_id}", response_model=PlotPointResponse)
async def create_plot_point(
    novel_id: int,
    data: PlotPointCreate,
    db: Session = Depends(get_db)
):
    """Create a new plot point"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    # Auto-assign timeline_order if not provided
    if data.timeline_order is None:
        max_order = db.query(PlotPoint).filter(
            PlotPoint.novel_id == novel_id
        ).count()
        data.timeline_order = max_order + 1
    
    plot_point = PlotPoint(
        novel_id=novel_id,
        title=data.title,
        description=data.description,
        event_type=data.event_type,
        chapter=data.chapter,
        timeline_order=data.timeline_order,
        status=data.status,
        is_major=data.is_major,
        importance=data.importance,
        emotional_weight=data.emotional_weight,
        plot_arc=data.plot_arc,
        involved_characters=data.involved_characters,
        locations=data.locations,
        tags=data.tags,
        notes=data.notes,
        foreshadowing=data.foreshadowing,
        resolution=data.resolution
    )
    
    db.add(plot_point)
    db.commit()
    db.refresh(plot_point)
    
    # Store in memory
    memory_service = MemoryService()
    await memory_service.remember(
        text=f"Plot point: {plot_point.title}. Type: {plot_point.event_type or 'general'}. Description: {plot_point.description or 'No description'}",
        dataset=novel.dataset_name,
        metadata={
            "type": "plot_point",
            "plot_id": plot_point.id,
            "title": plot_point.title,
            "is_major": plot_point.is_major
        }
    )
    
    logger.info(f"Created plot point: {plot_point.title} for novel {novel_id}")
    
    return PlotPointResponse(
        id=plot_point.id,
        title=plot_point.title,
        description=plot_point.description,
        event_type=plot_point.event_type,
        chapter=plot_point.chapter,
        timeline_order=plot_point.timeline_order,
        status=plot_point.status,
        is_major=plot_point.is_major,
        importance=plot_point.importance,
        emotional_weight=plot_point.emotional_weight,
        plot_arc=plot_point.plot_arc,
        involved_characters=plot_point.involved_characters,
        locations=plot_point.locations,
        tags=plot_point.tags,
        notes=plot_point.notes,
        foreshadowing=plot_point.foreshadowing,
        resolution=plot_point.resolution,
        created_at=plot_point.created_at.isoformat() if plot_point.created_at else "",
        updated_at=plot_point.updated_at.isoformat() if plot_point.updated_at else None
    )

@router.put("/{novel_id}/{plot_id}", response_model=PlotPointResponse)
async def update_plot_point(
    novel_id: int,
    plot_id: int,
    data: PlotPointUpdate,
    db: Session = Depends(get_db)
):
    """Update a plot point"""
    plot_point = db.query(PlotPoint).filter(
        PlotPoint.id == plot_id,
        PlotPoint.novel_id == novel_id
    ).first()
    
    if not plot_point:
        raise HTTPException(status_code=404, detail="Plot point not found")
    
    update_data = data.dict(exclude_none=True)
    for key, value in update_data.items():
        if hasattr(plot_point, key):
            setattr(plot_point, key, value)
    
    db.commit()
    db.refresh(plot_point)
    
    logger.info(f"Updated plot point: {plot_point.title}")
    
    return PlotPointResponse(
        id=plot_point.id,
        title=plot_point.title,
        description=plot_point.description,
        event_type=plot_point.event_type,
        chapter=plot_point.chapter,
        timeline_order=plot_point.timeline_order,
        status=plot_point.status,
        is_major=plot_point.is_major,
        importance=plot_point.importance,
        emotional_weight=plot_point.emotional_weight,
        plot_arc=plot_point.plot_arc,
        involved_characters=plot_point.involved_characters,
        locations=plot_point.locations,
        tags=plot_point.tags,
        notes=plot_point.notes,
        foreshadowing=plot_point.foreshadowing,
        resolution=plot_point.resolution,
        created_at=plot_point.created_at.isoformat() if plot_point.created_at else "",
        updated_at=plot_point.updated_at.isoformat() if plot_point.updated_at else None
    )

@router.delete("/{novel_id}/{plot_id}")
async def delete_plot_point(
    novel_id: int,
    plot_id: int,
    db: Session = Depends(get_db)
):
    """Delete a plot point"""
    plot_point = db.query(PlotPoint).filter(
        PlotPoint.id == plot_id,
        PlotPoint.novel_id == novel_id
    ).first()
    
    if not plot_point:
        raise HTTPException(status_code=404, detail="Plot point not found")
    
    title = plot_point.title
    db.delete(plot_point)
    db.commit()
    
    logger.info(f"Deleted plot point: {title}")
    
    return {"message": f"Plot point '{title}' deleted successfully"}


# ── Plot Arcs ────────────────────────────────────────────────────────

@router.get("/{novel_id}/arcs", response_model=List[PlotArcResponse])
async def get_plot_arcs(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get all plot arcs for a novel"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    arcs = db.query(PlotArc).filter(PlotArc.novel_id == novel_id).all()
    
    return [PlotArcResponse(
        id=arc.id,
        name=arc.name,
        description=arc.description,
        arc_type=arc.arc_type,
        start_chapter=arc.start_chapter,
        end_chapter=arc.end_chapter,
        status=arc.status,
        plot_point_ids=arc.plot_point_ids,
        notes=arc.notes,
        themes=arc.themes,
        created_at=arc.created_at.isoformat() if arc.created_at else "",
        updated_at=arc.updated_at.isoformat() if arc.updated_at else None
    ) for arc in arcs]

@router.post("/{novel_id}/arcs", response_model=PlotArcResponse)
async def create_plot_arc(
    novel_id: int,
    data: PlotArcCreate,
    db: Session = Depends(get_db)
):
    """Create a new plot arc"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    arc = PlotArc(
        novel_id=novel_id,
        name=data.name,
        description=data.description,
        arc_type=data.arc_type,
        start_chapter=data.start_chapter,
        end_chapter=data.end_chapter,
        status=data.status,
        plot_point_ids=data.plot_point_ids,
        notes=data.notes,
        themes=data.themes
    )
    
    db.add(arc)
    db.commit()
    db.refresh(arc)
    
    logger.info(f"Created plot arc: {arc.name} for novel {novel_id}")
    
    return PlotArcResponse(
        id=arc.id,
        name=arc.name,
        description=arc.description,
        arc_type=arc.arc_type,
        start_chapter=arc.start_chapter,
        end_chapter=arc.end_chapter,
        status=arc.status,
        plot_point_ids=arc.plot_point_ids,
        notes=arc.notes,
        themes=arc.themes,
        created_at=arc.created_at.isoformat() if arc.created_at else "",
        updated_at=arc.updated_at.isoformat() if arc.updated_at else None
    )
