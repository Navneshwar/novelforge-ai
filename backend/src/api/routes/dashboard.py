from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models import Character, CharacterRelationship, Chapter, GenerationHistory, Novel, PlotPoint, Project

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    novels_count = db.query(func.count(Novel.id)).scalar() or 0
    characters_count = db.query(func.count(Character.id)).scalar() or 0
    chapters_count = db.query(func.count(Chapter.id)).scalar() or 0
    plot_points_count = db.query(func.count(PlotPoint.id)).scalar() or 0
    relationships_count = db.query(func.count(CharacterRelationship.id)).scalar() or 0
    projects_count = db.query(func.count(Project.id)).scalar() or 0
    generations_count = db.query(func.count(GenerationHistory.id)).scalar() or 0
    
    recent_novels = db.query(Novel).order_by(
        Novel.updated_at.desc().nullslast(),
        Novel.created_at.desc()
    ).limit(5).all()
    
    return {
        "totals": {
            "novels": novels_count,
            "projects": projects_count,
            "chapters": chapters_count,
            "characters": characters_count,
            "relationships": relationships_count,
            "plot_points": plot_points_count,
            "generations": generations_count,
        },
        "recent_novels": [
            {
                "id": novel.id,
                "title": novel.title,
                "genre": novel.genre,
                "status": novel.status,
                "word_count": novel.word_count,
                "updated_at": (novel.updated_at or novel.created_at).isoformat()
                if (novel.updated_at or novel.created_at)
                else None,
            }
            for novel in recent_novels
        ],
    }
