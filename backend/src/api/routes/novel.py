from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.services.novel_service import NovelService

router = APIRouter()

# Request/Response Models
class NovelCreate(BaseModel):
    title: str
    genre: Optional[str] = "General"
    description: Optional[str] = ""
    content: Optional[str] = ""
    target_word_count: Optional[int] = None
    writing_style: Optional[str] = ""

class NovelUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    writing_style: Optional[str] = None
    target_word_count: Optional[int] = None

class NovelResponse(BaseModel):
    id: int
    title: str
    genre: str
    description: Optional[str]
    content: Optional[str]
    word_count: int
    status: str
    dataset_name: str
    created_at: str
    updated_at: Optional[str]
    characters: List[str] = []
    chapters: List[dict] = []

class ChapterCreate(BaseModel):
    title: Optional[str] = None
    content: str
    chapter_number: Optional[int] = None
    summary: Optional[str] = ""

class GenerateRequest(BaseModel):
    prompt: str
    style: Optional[str] = "continue"
    temperature: Optional[float] = 0.8

class ExtractCharactersRequest(BaseModel):
    text: str

@router.post("/", response_model=NovelResponse)
async def create_novel(
    novel_data: NovelCreate,
    db: Session = Depends(get_db)
):
    """Create a new novel"""
    service = NovelService(db)
    novel = await service.create_novel(novel_data.dict())
    
    return NovelResponse(
        id=novel.id,
        title=novel.title,
        genre=novel.genre,
        description=novel.description,
        content=novel.content,
        word_count=novel.word_count,
        status=novel.status,
        dataset_name=novel.dataset_name,
        created_at=novel.created_at.isoformat() if novel.created_at else "",
        updated_at=novel.updated_at.isoformat() if novel.updated_at else None,
        characters=[],
        chapters=[]
    )

@router.get("/", response_model=List[NovelResponse])
async def get_all_novels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all novels"""
    service = NovelService(db)
    novels = await service.get_all_novels(skip, limit)
    
    results = []
    for novel in novels:
        characters = [c.name for c in novel.characters if c.is_active]
        chapters = [{"id": c.id, "title": c.title, "number": c.chapter_number} for c in novel.chapters]
        
        results.append(NovelResponse(
            id=novel.id,
            title=novel.title,
            genre=novel.genre,
            description=novel.description,
            content=novel.content[:500] if novel.content else "",  # Truncate for list view
            word_count=novel.word_count,
            status=novel.status,
            dataset_name=novel.dataset_name,
            created_at=novel.created_at.isoformat() if novel.created_at else "",
            updated_at=novel.updated_at.isoformat() if novel.updated_at else None,
            characters=characters,
            chapters=chapters
        ))
    
    return results

@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get a novel by ID"""
    service = NovelService(db)
    novel = await service.get_novel(novel_id)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    characters = [c.name for c in novel.characters if c.is_active]
    chapters = [{"id": c.id, "title": c.title, "number": c.chapter_number} for c in novel.chapters]
    
    return NovelResponse(
        id=novel.id,
        title=novel.title,
        genre=novel.genre,
        description=novel.description,
        content=novel.content,
        word_count=novel.word_count,
        status=novel.status,
        dataset_name=novel.dataset_name,
        created_at=novel.created_at.isoformat() if novel.created_at else "",
        updated_at=novel.updated_at.isoformat() if novel.updated_at else None,
        characters=characters,
        chapters=chapters
    )

@router.put("/{novel_id}", response_model=NovelResponse)
async def update_novel(
    novel_id: int,
    novel_data: NovelUpdate,
    db: Session = Depends(get_db)
):
    """Update a novel"""
    service = NovelService(db)
    novel = await service.update_novel(novel_id, novel_data.dict(exclude_none=True))
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    characters = [c.name for c in novel.characters if c.is_active]
    chapters = [{"id": c.id, "title": c.title, "number": c.chapter_number} for c in novel.chapters]
    
    return NovelResponse(
        id=novel.id,
        title=novel.title,
        genre=novel.genre,
        description=novel.description,
        content=novel.content,
        word_count=novel.word_count,
        status=novel.status,
        dataset_name=novel.dataset_name,
        created_at=novel.created_at.isoformat() if novel.created_at else "",
        updated_at=novel.updated_at.isoformat() if novel.updated_at else None,
        characters=characters,
        chapters=chapters
    )

@router.delete("/{novel_id}")
async def delete_novel(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Delete a novel"""
    service = NovelService(db)
    novel = await service.get_novel(novel_id)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    # Delete from memory
    memory_service = service.memory_service
    await memory_service.forget(dataset=novel.dataset_name)
    
    db.delete(novel)
    db.commit()
    
    return {"message": "Novel deleted successfully"}

@router.post("/{novel_id}/chapters", response_model=dict)
async def add_chapter(
    novel_id: int,
    chapter_data: ChapterCreate,
    db: Session = Depends(get_db)
):
    """Add a chapter to a novel"""
    service = NovelService(db)
    chapter = await service.add_chapter(novel_id, chapter_data.dict())
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    return {
        "id": chapter.id,
        "title": chapter.title,
        "chapter_number": chapter.chapter_number,
        "word_count": chapter.word_count,
        "message": "Chapter added successfully"
    }

@router.post("/{novel_id}/generate")
async def generate_content(
    novel_id: int,
    request: GenerateRequest,
    db: Session = Depends(get_db)
):
    """Generate AI content for a novel"""
    service = NovelService(db)
    result = await service.generate_content(novel_id, request.prompt, request.style)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.post("/{novel_id}/extract-characters")
async def extract_characters(
    novel_id: int,
    request: ExtractCharactersRequest,
    db: Session = Depends(get_db)
):
    """Extract characters from text"""
    service = NovelService(db)
    result = await service.extract_characters_from_text(novel_id, request.text)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result