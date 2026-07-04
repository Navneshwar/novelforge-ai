from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_optional_user
from src.models import Novel, Project, User

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    novel_ids: list[int] = []


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: str | None = Field(default=None, max_length=50)
    novel_ids: list[int] | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    status: str
    owner_id: int | None
    novels: list[dict]
    created_at: str
    updated_at: str | None


def serialize_project(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        owner_id=project.owner_id,
        novels=[
            {
                "id": novel.id,
                "title": novel.title,
                "genre": novel.genre,
                "status": novel.status,
            }
            for novel in project.novels
        ],
        created_at=project.created_at.isoformat() if project.created_at else "",
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


@router.get("/", response_model=list[ProjectResponse])
async def get_projects(
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    query = db.query(Project)
    if user:
        query = query.filter(Project.owner_id == user.id)
    return [serialize_project(project) for project in query.order_by(Project.id.desc()).all()]


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreate,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    project = Project(
        name=request.name.strip(),
        description=request.description,
        owner_id=user.id if user else None,
    )
    if request.novel_ids:
        project.novels = db.query(Novel).filter(Novel.id.in_(request.novel_ids)).all()
    db.add(project)
    db.commit()
    db.refresh(project)
    return serialize_project(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return serialize_project(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    request: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    data = request.dict(exclude_unset=True)
    novel_ids = data.pop("novel_ids", None)
    for key, value in data.items():
        setattr(project, key, value)
    if novel_ids is not None:
        project.novels = db.query(Novel).filter(Novel.id.in_(novel_ids)).all() if novel_ids else []
    
    db.commit()
    db.refresh(project)
    return serialize_project(project)


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
