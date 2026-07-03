from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.services.memory_service import MemoryService
from src.models import Novel

router = APIRouter()

# Request/Response Models
class RememberRequest(BaseModel):
    text: str
    metadata: Optional[dict] = {}

class RecallRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class MemoryResponse(BaseModel):
    success: bool
    dataset: Optional[str] = None
    error: Optional[str] = None

class RecallResponse(BaseModel):
    items: List[dict]
    total: int

@router.post("/remember/{novel_id}")
async def remember_text(
    novel_id: int,
    request: RememberRequest,
    db: Session = Depends(get_db)
):
    """Store text in Cognee memory"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    memory_service = MemoryService()
    result = await memory_service.remember(
        text=request.text,
        dataset=novel.dataset_name,
        metadata=request.metadata
    )
    
    return result

@router.post("/recall/{novel_id}", response_model=RecallResponse)
async def recall_memory(
    novel_id: int,
    request: RecallRequest,
    db: Session = Depends(get_db)
):
    """Recall relevant information from memory"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    memory_service = MemoryService()
    results = await memory_service.recall(
        query=request.query,
        dataset=novel.dataset_name,
        limit=request.limit
    )
    
    return RecallResponse(
        items=results,
        total=len(results)
    )

@router.post("/improve/{novel_id}")
async def improve_memory(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Run memify to improve memory"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    memory_service = MemoryService()
    result = await memory_service.improve(dataset=novel.dataset_name)
    
    return result

@router.delete("/forget/{novel_id}/{item_id}")
async def forget_item(
    novel_id: int,
    item_id: str,
    db: Session = Depends(get_db)
):
    """Forget a specific memory item"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    memory_service = MemoryService()
    result = await memory_service.forget(
        dataset=novel.dataset_name,
        item_id=item_id
    )
    
    return result

@router.delete("/forget/{novel_id}")
async def forget_dataset(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Forget entire dataset for a novel"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    memory_service = MemoryService()
    result = await memory_service.forget(dataset=novel.dataset_name)
    
    return result

@router.get("/stats/{novel_id}")
async def get_memory_stats(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get memory statistics"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    memory_service = MemoryService()
    stats = await memory_service.get_stats(dataset=novel.dataset_name)
    
    # Add additional stats from database
    stats["characters"] = db.query(Novel).filter(Novel.id == novel_id).first().characters.count()
    stats["chapters"] = db.query(Novel).filter(Novel.id == novel_id).first().chapters.count()
    stats["plot_points"] = db.query(Novel).filter(Novel.id == novel_id).first().plot_points.count()
    
    return stats

@router.get("/graph/{novel_id}")
async def get_memory_graph(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get the knowledge graph for a novel"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    memory_service = MemoryService()
    graph = await memory_service.get_graph(dataset=novel.dataset_name)
    
    # Add novel-specific nodes from database
    characters = novel.characters
    for char in characters:
        graph["nodes"].append({
            "id": f"char_{char.id}",
            "label": char.name,
            "type": "character",
            "data": {
                "role": char.role,
                "description": char.description
            }
        })
    
    # Add chapter nodes
    for chapter in novel.chapters:
        graph["nodes"].append({
            "id": f"chap_{chapter.id}",
            "label": f"Chapter {chapter.chapter_number}",
            "type": "chapter",
            "data": {
                "title": chapter.title,
                "summary": chapter.summary
            }
        })
    
    # Add relationships (characters to chapters)
    # This would need actual character-chapter mapping data
    
    return graph