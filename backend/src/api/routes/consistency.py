from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.services.consistency_service import ConsistencyService
from src.models import Novel

router = APIRouter()

# Request/Response Models
class ConsistencyCheckResponse(BaseModel):
    novel_id: int
    total_issues: int
    issues: List[dict]
    status: str  # "clear" or "warning"

class IssueResponse(BaseModel):
    id: str
    type: str
    severity: str
    title: str
    description: str
    location: Optional[str] = None
    suggestion: Optional[str] = None

class ResolveResponse(BaseModel):
    success: bool
    issue_id: str
    message: str

@router.post("/check/{novel_id}", response_model=ConsistencyCheckResponse)
async def run_consistency_check(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Run a full consistency check on a novel"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    service = ConsistencyService(db)
    result = await service.check_novel_consistency(novel_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return ConsistencyCheckResponse(
        novel_id=result["novel_id"],
        total_issues=result["total_issues"],
        issues=result["issues"],
        status=result["status"]
    )

@router.get("/issues/{novel_id}", response_model=List[IssueResponse])
async def get_consistency_issues(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get all consistency issues for a novel"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    service = ConsistencyService(db)
    issues = await service.get_consistency_issues(novel_id)
    
    return [IssueResponse(
        id=issue.get("id", f"issue_{i}"),
        type=issue.get("type", "unknown"),
        severity=issue.get("severity", "medium"),
        title=issue.get("title", "Consistency issue"),
        description=issue.get("description", ""),
        location=issue.get("location"),
        suggestion=issue.get("suggestion")
    ) for i, issue in enumerate(issues)]

@router.post("/resolve/{novel_id}/{issue_id}", response_model=ResolveResponse)
async def resolve_issue(
    novel_id: int,
    issue_id: str,
    db: Session = Depends(get_db)
):
    """Resolve a specific consistency issue"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    service = ConsistencyService(db)
    result = await service.resolve_issue(novel_id, issue_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ResolveResponse(
        success=True,
        issue_id=issue_id,
        message="Issue resolved successfully"
    )

@router.get("/summary/{novel_id}")
async def get_consistency_summary(
    novel_id: int,
    db: Session = Depends(get_db)
):
    """Get a summary of consistency status"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    # Get character count
    characters = novel.characters
    chapters = novel.chapters
    plot_points = novel.plot_points
    
    return {
        "novel_id": novel_id,
        "title": novel.title,
        "characters_count": len(characters),
        "chapters_count": len(chapters),
        "plot_points_count": len(plot_points),
        "last_checked": novel.updated_at.isoformat() if novel.updated_at else None,
        "status": "active",
        "memory_dataset": novel.dataset_name
    }