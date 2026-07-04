from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.services.memory_service import MemoryService
from src.models import Novel, Character, CharacterRelationship, PlotPoint, Chapter

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
    stats["characters"] = len(novel.characters)
    stats["chapters"] = len(novel.chapters)
    stats["plot_points"] = len(novel.plot_points)
    
    # Count relationships
    from src.models import CharacterRelationship
    relationship_count = db.query(CharacterRelationship).join(
        Character, CharacterRelationship.source_id == Character.id
    ).filter(Character.novel_id == novel_id).count()
    stats["relationships"] = relationship_count
    
    database_items = (
        1
        + stats["characters"]
        + stats["chapters"]
        + stats["plot_points"]
        + relationship_count
    )
    stats["database_items"] = database_items
    stats["total_items"] = max(stats.get("items_count", 0), database_items)
    
    return stats

@router.get("/graph/{novel_id}")
async def get_memory_graph(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get the knowledge graph for a novel.

    This merges two sources:
      1. Cognee's actual extracted knowledge graph (entities/relationships
         Cognee derived from remembered text via cognify/memify) — this is
         what makes it a "memory graph" rather than just an ER diagram.
      2. The app's own structural data (novel/characters/chapters/plot
         points) as a reliable fallback/scaffold, since Cognee's graph is
         empty until enough content has been remembered.

    Previously this endpoint only built #2 and never called into Cognee at
    all, so the "Memory Graph Visualizer" wasn't showing Cognee's memory.
    """
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    graph = {"nodes": [], "edges": [], "dataset": novel.dataset_name}

    # Pull Cognee's actual graph first and seed our node/edge lists with it.
    # NOTE: "origin" (not "source") is used for provenance tagging, since
    # edges already use "source"/"target" to mean source-node-id/target-node-id.
    memory_service = MemoryService()
    cognee_graph = await memory_service.get_graph(dataset=novel.dataset_name)
    for node in cognee_graph.get("nodes", []):
        node.setdefault("origin", "cognee")
        graph["nodes"].append(node)
    for edge in cognee_graph.get("edges", []):
        edge.setdefault("origin", "cognee")
        graph["edges"].append(edge)

    # Add novel node as central hub
    graph["nodes"].append({
        "id": f"novel_{novel.id}",
        "label": novel.title,
        "type": "novel",
        "origin": "database",
        "data": {"genre": novel.genre, "status": novel.status}
    })
    
    # Add character nodes
    characters = novel.characters
    for char in characters:
        graph["nodes"].append({
            "id": f"char_{char.id}",
            "label": char.name,
            "type": "character",
            "data": {
                "role": char.role,
                "description": char.description,
                "traits": char.traits
            }
        })
        # Edge: character belongs to novel
        graph["edges"].append({
            "source": f"novel_{novel.id}",
            "target": f"char_{char.id}",
            "type": "has_character"
        })
    
    # Add chapter nodes
    for chapter in novel.chapters:
        graph["nodes"].append({
            "id": f"chap_{chapter.id}",
            "label": f"Ch.{chapter.chapter_number}: {chapter.title or 'Untitled'}",
            "type": "chapter",
            "data": {
                "title": chapter.title,
                "summary": chapter.summary,
                "word_count": chapter.word_count
            }
        })
        # Edge: chapter belongs to novel
        graph["edges"].append({
            "source": f"novel_{novel.id}",
            "target": f"chap_{chapter.id}",
            "type": "has_chapter"
        })
    
    # Add plot point nodes
    plot_points = db.query(PlotPoint).filter(PlotPoint.novel_id == novel_id).all()
    for pp in plot_points:
        graph["nodes"].append({
            "id": f"plot_{pp.id}",
            "label": pp.title,
            "type": "plot",
            "data": {
                "event_type": pp.event_type,
                "status": pp.status,
                "is_major": pp.is_major
            }
        })
        # Edge: plot point to chapter (if assigned)
        if pp.chapter:
            matching_chapters = [c for c in novel.chapters if c.chapter_number == pp.chapter]
            for mc in matching_chapters:
                graph["edges"].append({
                    "source": f"plot_{pp.id}",
                    "target": f"chap_{mc.id}",
                    "type": "occurs_in"
                })
        # Edge: plot point to involved characters
        if pp.involved_characters:
            character_ids = {char.id for char in characters}
            for char_id in pp.involved_characters:
                if char_id in character_ids:
                    graph["edges"].append({
                        "source": f"plot_{pp.id}",
                        "target": f"char_{char_id}",
                        "type": "involves"
                    })
    
    # Add character-character relationship edges
    for char in characters:
        rels = db.query(CharacterRelationship).filter(
            CharacterRelationship.source_id == char.id
        ).all()
        for rel in rels:
            graph["edges"].append({
                "source": f"char_{rel.source_id}",
                "target": f"char_{rel.target_id}",
                "type": rel.relationship_type,
                "data": {
                    "description": rel.description,
                    "strength": rel.strength
                }
            })
    
    # Add character-chapter edges based on appearance
    for char in characters:
        if char.first_appearance:
            matching = [c for c in novel.chapters if c.chapter_number == char.first_appearance]
            for mc in matching:
                graph["edges"].append({
                    "source": f"char_{char.id}",
                    "target": f"chap_{mc.id}",
                    "type": "first_appears_in"
                })
        if char.last_appearance and char.last_appearance != char.first_appearance:
            matching = [c for c in novel.chapters if c.chapter_number == char.last_appearance]
            for mc in matching:
                graph["edges"].append({
                    "source": f"char_{char.id}",
                    "target": f"chap_{mc.id}",
                    "type": "last_appears_in"
                })

    # Anything added above without an explicit origin came from our own
    # SQL models, not Cognee's extracted memory graph.
    for node in graph["nodes"]:
        node.setdefault("origin", "database")
    for edge in graph["edges"]:
        edge.setdefault("origin", "database")

    return graph