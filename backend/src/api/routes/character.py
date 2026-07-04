from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.models import Character, CharacterRelationship, Novel
from src.services.memory_service import MemoryService
from loguru import logger

router = APIRouter()

# Request/Response Models
class CharacterCreate(BaseModel):
    name: str
    description: Optional[str] = None
    role: Optional[str] = "character"
    traits: Optional[List[str]] = []
    physical_description: Optional[str] = None
    background: Optional[str] = None
    personality: Optional[str] = None
    goals: Optional[List[str]] = []
    fears: Optional[List[str]] = []
    strengths: Optional[List[str]] = []
    weaknesses: Optional[List[str]] = []
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    location: Optional[str] = None

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    traits: Optional[List[str]] = None
    physical_description: Optional[str] = None
    background: Optional[str] = None
    personality: Optional[str] = None
    goals: Optional[List[str]] = None
    fears: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

class CharacterResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    role: Optional[str]
    traits: Optional[List[str]]
    physical_description: Optional[str]
    background: Optional[str]
    personality: Optional[str]
    goals: Optional[List[str]]
    fears: Optional[List[str]]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    age: Optional[int]
    gender: Optional[str]
    occupation: Optional[str]
    location: Optional[str]
    is_active: bool
    importance_score: float
    created_at: str
    updated_at: Optional[str]

class RelationshipCreate(BaseModel):
    target_id: int
    relationship_type: str
    description: Optional[str] = None
    strength: Optional[float] = 0.5

class RelationshipResponse(BaseModel):
    id: int
    source_id: int
    target_id: int
    relationship_type: str
    description: Optional[str]
    strength: float

@router.get("/{novel_id}", response_model=List[CharacterResponse])
async def get_characters(
    novel_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all characters for a novel"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    query = db.query(Character).filter(Character.novel_id == novel_id)
    if active_only:
        query = query.filter(Character.is_active == True)
    
    characters = query.all()
    
    return [CharacterResponse(
        id=char.id,
        name=char.name,
        description=char.description,
        role=char.role,
        traits=char.traits,
        physical_description=char.physical_description,
        background=char.background,
        personality=char.personality,
        goals=char.goals,
        fears=char.fears,
        strengths=char.strengths,
        weaknesses=char.weaknesses,
        age=char.age,
        gender=char.gender,
        occupation=char.occupation,
        location=char.location,
        is_active=char.is_active,
        importance_score=char.importance_score,
        created_at=char.created_at.isoformat() if char.created_at else "",
        updated_at=char.updated_at.isoformat() if char.updated_at else None
    ) for char in characters]

@router.post("/{novel_id}", response_model=CharacterResponse)
async def create_character(
    novel_id: int,
    character_data: CharacterCreate,
    db: Session = Depends(get_db)
):
    """Create a new character"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    # Check for duplicate name
    existing = db.query(Character).filter(
        Character.novel_id == novel_id,
        Character.name.ilike(character_data.name)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Character '{character_data.name}' already exists")
    
    character = Character(
        novel_id=novel_id,
        name=character_data.name,
        description=character_data.description,
        role=character_data.role,
        traits=character_data.traits,
        physical_description=character_data.physical_description,
        background=character_data.background,
        personality=character_data.personality,
        goals=character_data.goals,
        fears=character_data.fears,
        strengths=character_data.strengths,
        weaknesses=character_data.weaknesses,
        age=character_data.age,
        gender=character_data.gender,
        occupation=character_data.occupation,
        location=character_data.location
    )
    
    db.add(character)
    db.commit()
    db.refresh(character)
    
    # Store in memory
    memory_service = MemoryService()
    await memory_service.remember(
        text=f"Character: {character.name}. Role: {character.role or 'character'}. Description: {character.description or 'No description'}",
        dataset=novel.dataset_name,
        metadata={
            "type": "character",
            "character_id": character.id,
            "name": character.name
        }
    )
    
    logger.info(f"Created character: {character.name} for novel {novel_id}")
    
    return CharacterResponse(
        id=character.id,
        name=character.name,
        description=character.description,
        role=character.role,
        traits=character.traits,
        physical_description=character.physical_description,
        background=character.background,
        personality=character.personality,
        goals=character.goals,
        fears=character.fears,
        strengths=character.strengths,
        weaknesses=character.weaknesses,
        age=character.age,
        gender=character.gender,
        occupation=character.occupation,
        location=character.location,
        is_active=character.is_active,
        importance_score=character.importance_score,
        created_at=character.created_at.isoformat() if character.created_at else "",
        updated_at=character.updated_at.isoformat() if character.updated_at else None
    )

@router.put("/{novel_id}/{character_id}", response_model=CharacterResponse)
async def update_character(
    novel_id: int,
    character_id: int,
    character_data: CharacterUpdate,
    db: Session = Depends(get_db)
):
    """Update a character"""
    character = db.query(Character).filter(
        Character.id == character_id,
        Character.novel_id == novel_id
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Update fields
    update_data = character_data.dict(exclude_none=True)
    for key, value in update_data.items():
        if hasattr(character, key):
            setattr(character, key, value)
    
    db.commit()
    db.refresh(character)
    
    # Update memory
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel:
        memory_service = MemoryService()
        await memory_service.remember(
            text=f"Updated character: {character.name}. Role: {character.role or 'character'}",
            dataset=novel.dataset_name,
            metadata={
                "type": "character_update",
                "character_id": character.id,
                "name": character.name
            }
        )
    
    return CharacterResponse(
        id=character.id,
        name=character.name,
        description=character.description,
        role=character.role,
        traits=character.traits,
        physical_description=character.physical_description,
        background=character.background,
        personality=character.personality,
        goals=character.goals,
        fears=character.fears,
        strengths=character.strengths,
        weaknesses=character.weaknesses,
        age=character.age,
        gender=character.gender,
        occupation=character.occupation,
        location=character.location,
        is_active=character.is_active,
        importance_score=character.importance_score,
        created_at=character.created_at.isoformat() if character.created_at else "",
        updated_at=character.updated_at.isoformat() if character.updated_at else None
    )

@router.delete("/{novel_id}/{character_id}")
async def delete_character(
    novel_id: int,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Delete a character"""
    character = db.query(Character).filter(
        Character.id == character_id,
        Character.novel_id == novel_id
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Delete relationships first
    db.query(CharacterRelationship).filter(
        (CharacterRelationship.source_id == character_id) |
        (CharacterRelationship.target_id == character_id)
    ).delete()
    
    db.delete(character)
    db.commit()
    
    return {"message": f"Character '{character.name}' deleted successfully"}

@router.post("/{novel_id}/{character_id}/relationships", response_model=RelationshipResponse)
async def add_relationship(
    novel_id: int,
    character_id: int,
    relationship_data: RelationshipCreate,
    db: Session = Depends(get_db)
):
    """Add a relationship between characters"""
    # Check if characters exist
    source = db.query(Character).filter(
        Character.id == character_id,
        Character.novel_id == novel_id
    ).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source character not found")
    
    target = db.query(Character).filter(
        Character.id == relationship_data.target_id,
        Character.novel_id == novel_id
    ).first()
    
    if not target:
        raise HTTPException(status_code=404, detail="Target character not found")
    
    # Check for existing relationship
    existing = db.query(CharacterRelationship).filter(
        CharacterRelationship.source_id == character_id,
        CharacterRelationship.target_id == relationship_data.target_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists")
    
    relationship = CharacterRelationship(
        source_id=character_id,
        target_id=relationship_data.target_id,
        relationship_type=relationship_data.relationship_type,
        description=relationship_data.description,
        strength=relationship_data.strength or 0.5
    )
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    
    # Store in memory
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel:
        memory_service = MemoryService()
        await memory_service.remember(
            text=f"Relationship: {source.name} - {relationship_data.relationship_type} -> {target.name}",
            dataset=novel.dataset_name,
            metadata={
                "type": "relationship",
                "source": source.name,
                "target": target.name,
                "relationship_type": relationship_data.relationship_type
            }
        )
    
    return RelationshipResponse(
        id=relationship.id,
        source_id=relationship.source_id,
        target_id=relationship.target_id,
        relationship_type=relationship.relationship_type,
        description=relationship.description,
        strength=relationship.strength
    )

@router.get("/{novel_id}/{character_id}/relationships", response_model=List[RelationshipResponse])
async def get_relationships(
    novel_id: int,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Get all relationships for a character"""
    relationships = db.query(CharacterRelationship).filter(
        (CharacterRelationship.source_id == character_id) |
        (CharacterRelationship.target_id == character_id)
    ).all()
    
    return [RelationshipResponse(
        id=rel.id,
        source_id=rel.source_id,
        target_id=rel.target_id,
        relationship_type=rel.relationship_type,
        description=rel.description,
        strength=rel.strength
    ) for rel in relationships]

@router.post("/{novel_id}/{character_id}/generate-backstory")
async def generate_backstory(
    novel_id: int,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Generate a backstory for a character using AI"""
    from src.services.llm_service import LLMService
    
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    character = db.query(Character).filter(
        Character.id == character_id,
        Character.novel_id == novel_id
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Recall memory context about this character
    memory_service = MemoryService()
    memory_context = await memory_service.recall(
        query=f"character {character.name} backstory background history",
        dataset=novel.dataset_name,
        limit=5
    )
    
    # Get relationships for richer context
    relationships = db.query(CharacterRelationship).filter(
        (CharacterRelationship.source_id == character_id) |
        (CharacterRelationship.target_id == character_id)
    ).all()
    
    rel_descriptions = []
    for rel in relationships:
        other_char = db.query(Character).filter(
            Character.id == (rel.target_id if rel.source_id == character_id else rel.source_id)
        ).first()
        if other_char:
            rel_descriptions.append(f"{rel.relationship_type} with {other_char.name}")
    
    # Build character profile for prompt
    char_profile = f"Name: {character.name}\n"
    if character.role:
        char_profile += f"Role: {character.role}\n"
    if character.description:
        char_profile += f"Description: {character.description}\n"
    if character.traits:
        char_profile += f"Traits: {', '.join(character.traits)}\n"
    if character.age:
        char_profile += f"Age: {character.age}\n"
    if character.gender:
        char_profile += f"Gender: {character.gender}\n"
    if character.occupation:
        char_profile += f"Occupation: {character.occupation}\n"
    if character.goals:
        char_profile += f"Goals: {', '.join(character.goals)}\n"
    if character.fears:
        char_profile += f"Fears: {', '.join(character.fears)}\n"
    if rel_descriptions:
        char_profile += f"Relationships: {', '.join(rel_descriptions)}\n"
    
    # Generate backstory with LLM
    llm_service = LLMService()
    prompt = f"""Write a compelling backstory for a character in a {novel.genre} novel titled "{novel.title}".

CHARACTER PROFILE:
{char_profile}

NOVEL CONTEXT:
{novel.description or 'No description provided.'}

Write a 2-3 paragraph backstory that:
- Explains their motivations and personality
- Fits the novel's genre and tone
- Creates interesting hooks for the story
- Is consistent with the character details above

Write ONLY the backstory, no headers or labels."""

    backstory = await llm_service.generate_with_memory(
        prompt=prompt,
        memory_context=memory_context,
        temperature=0.8
    )
    
    # Save backstory to character
    character.background = backstory
    db.commit()
    db.refresh(character)
    
    # Store in memory
    await memory_service.remember(
        text=f"Backstory for {character.name}: {backstory[:500]}",
        dataset=novel.dataset_name,
        metadata={
            "type": "character_backstory",
            "character_id": character_id,
            "name": character.name
        }
    )
    
    logger.info(f"Generated backstory for character: {character.name}")
    
    return {
        "backstory": backstory,
        "character_id": character_id,
        "character_name": character.name,
        "message": "Backstory generated successfully"
    }