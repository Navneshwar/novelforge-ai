from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
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

class ChapterData(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = ""
    chapter_number: Optional[int] = None
    summary: Optional[str] = ""
    status: Optional[str] = "draft"

class NovelUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    writing_style: Optional[str] = None
    target_word_count: Optional[int] = None
    chapters: Optional[List[ChapterData]] = None

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
    characters: List[dict] = []
    chapters: List[dict] = []

class ChapterCreate(BaseModel):
    title: Optional[str] = None
    content: str = ""
    chapter_number: Optional[int] = None
    summary: Optional[str] = ""

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None

class ChapterResponse(BaseModel):
    id: int
    title: Optional[str]
    content: Optional[str]
    chapter_number: int
    word_count: int
    summary: Optional[str]
    status: str

class GenerateRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
    style: Optional[str] = "continue"
    temperature: Optional[float] = Field(default=0.8, ge=0.0, le=2.0)

class ExtractCharactersRequest(BaseModel):
    text: str

def serialize_novel_response(novel, include_full_content: bool = True) -> NovelResponse:
    """Serialize a Novel model into the frontend response shape."""
    characters = [
        {
            "id": c.id,
            "name": c.name,
            "role": c.role,
            "description": c.description,
            "traits": c.traits or [],
        }
        for c in novel.characters if c.is_active
    ]
    chapters = [
        {
            "id": c.id,
            "title": c.title,
            "number": c.chapter_number,
            "content": c.content or "",
            "word_count": c.word_count or 0,
            "summary": c.summary or "",
            "status": c.status or "draft"
        }
        for c in sorted(novel.chapters, key=lambda x: x.chapter_number)
    ]
    updated_at = novel.updated_at or novel.created_at
    content = novel.content or ""
    
    return NovelResponse(
        id=novel.id,
        title=novel.title,
        genre=novel.genre,
        description=novel.description,
        content=content if include_full_content else content[:500],
        word_count=novel.word_count,
        status=novel.status,
        dataset_name=novel.dataset_name,
        created_at=novel.created_at.isoformat() if novel.created_at else "",
        updated_at=updated_at.isoformat() if updated_at else None,
        characters=characters,
        chapters=chapters
    )

@router.post("/", response_model=NovelResponse)
async def create_novel(
    novel_data: NovelCreate,
    db: Session = Depends(get_db)
):
    """Create a new novel"""
    service = NovelService(db)
    novel = await service.create_novel(novel_data.dict())
    
    return serialize_novel_response(novel)

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
        results.append(serialize_novel_response(novel, include_full_content=False))
    
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
    
    return serialize_novel_response(novel)

@router.put("/{novel_id}", response_model=NovelResponse)
async def update_novel(
    novel_id: int,
    novel_data: NovelUpdate,
    db: Session = Depends(get_db)
):
    """Update a novel, optionally with chapters"""
    service = NovelService(db)
    
    data = novel_data.dict(exclude_none=True)
    chapters_data = data.pop("chapters", None)
    
    novel = await service.update_novel(novel_id, data)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    # Handle bulk chapter saves
    if chapters_data:
        for ch in chapters_data:
            if ch.get("id"):
                await service.update_chapter(novel_id, ch["id"], ch)
            else:
                await service.add_chapter(novel_id, ch)
    
    # Refresh novel to get updated chapters
    novel = await service.get_novel(novel_id)
    return serialize_novel_response(novel)

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

# ── Chapter Endpoints ──────────────────────────────────────────────

@router.get("/{novel_id}/chapters", response_model=List[ChapterResponse])
async def get_chapters(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get all chapters for a novel"""
    service = NovelService(db)
    chapters = await service.get_chapters(novel_id)
    if chapters is None:
        raise HTTPException(status_code=404, detail="Novel not found")
    return [
        ChapterResponse(
            id=c.id,
            title=c.title,
            content=c.content or "",
            chapter_number=c.chapter_number,
            word_count=c.word_count or 0,
            summary=c.summary or "",
            status=c.status or "draft"
        )
        for c in chapters
    ]

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
        "content": chapter.content or "",
        "summary": chapter.summary or "",
        "status": chapter.status or "draft",
        "message": "Chapter added successfully"
    }

@router.put("/{novel_id}/chapters/{chapter_id}", response_model=dict)
async def update_chapter(
    novel_id: int,
    chapter_id: int,
    chapter_data: ChapterUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific chapter"""
    service = NovelService(db)
    chapter = await service.update_chapter(novel_id, chapter_id, chapter_data.dict(exclude_none=True))
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return {
        "id": chapter.id,
        "title": chapter.title,
        "chapter_number": chapter.chapter_number,
        "word_count": chapter.word_count,
        "content": chapter.content or "",
        "summary": chapter.summary or "",
        "status": chapter.status or "draft",
        "message": "Chapter updated successfully"
    }

@router.delete("/{novel_id}/chapters/{chapter_id}")
async def delete_chapter(
    novel_id: int,
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """Delete a chapter"""
    service = NovelService(db)
    result = await service.delete_chapter(novel_id, chapter_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return {"message": "Chapter deleted successfully"}

# ── AI Endpoints ──────────────────────────────────────────────────

@router.post("/{novel_id}/generate")
async def generate_content(
    novel_id: int,
    request: GenerateRequest,
    db: Session = Depends(get_db)
):
    """Generate AI content for a novel"""
    service = NovelService(db)
    result = await service.generate_content(
        novel_id,
        request.prompt,
        request.style,
        context=request.context,
        temperature=request.temperature
    )
    
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
