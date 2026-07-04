from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.models import Novel, Chapter, Character, PlotPoint
from src.services.memory_service import MemoryService
from src.services.llm_service import LLMService
from loguru import logger
import uuid
from datetime import datetime

class NovelService:
    def __init__(self, db: Session):
        self.db = db
        self.memory_service = MemoryService()
        self.llm_service = LLMService()
    
    async def create_novel(self, data: Dict) -> Novel:
        """Create a new novel"""
        dataset_name = f"novel_{uuid.uuid4().hex[:8]}"
        
        novel = Novel(
            title=data.get("title", "Untitled Novel"),
            genre=data.get("genre", "General"),
            description=data.get("description", ""),
            dataset_name=dataset_name,
            content=data.get("content", ""),
            word_count=len((data.get("content") or "").split()),
            status=data.get("status", "draft"),
            writing_style=data.get("writing_style", ""),
            target_word_count=data.get("target_word_count")
        )
        
        self.db.add(novel)
        self.db.commit()
        self.db.refresh(novel)
        
        logger.info(f"Created novel: {novel.title} (ID: {novel.id})")
        return novel
    
    async def get_novel(self, novel_id: int) -> Optional[Novel]:
        """Get novel by ID"""
        return self.db.query(Novel).filter(Novel.id == novel_id).first()
    
    async def get_all_novels(self, skip: int = 0, limit: int = 100) -> List[Novel]:
        """Get all novels"""
        return self.db.query(Novel).order_by(
            desc(Novel.updated_at),
            desc(Novel.created_at)
        ).offset(skip).limit(limit).all()
    
    async def update_novel(self, novel_id: int, data: Dict) -> Optional[Novel]:
        """Update novel"""
        novel = await self.get_novel(novel_id)
        if not novel:
            return None
        
        # Update fields
        for key, value in data.items():
            if hasattr(novel, key) and value is not None:
                setattr(novel, key, value)
        
        # Update word count if content changed
        if "content" in data:
            novel.word_count = len((data["content"] or "").split())
            novel.last_written_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(novel)
        
        # Store in memory
        await self.memory_service.remember(
            text=self._build_novel_memory_text(novel),
            dataset=novel.dataset_name,
            metadata={"type": "novel_metadata", "novel_id": novel_id}
        )
        
        return novel
    
    async def add_chapter(self, novel_id: int, data: Dict) -> Optional[Chapter]:
        """Add a chapter to a novel"""
        novel = await self.get_novel(novel_id)
        if not novel:
            return None
        
        chapter_number = data.get("chapter_number", len(novel.chapters) + 1)
        
        chapter = Chapter(
            novel_id=novel_id,
            title=data.get("title", f"Chapter {chapter_number}"),
            content=data.get("content", ""),
            chapter_number=chapter_number,
            summary=data.get("summary", ""),
            status=data.get("status", "draft")
        )
        
        if chapter.content:
            chapter.word_count = len(chapter.content.split())
        
        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)
        
        # Store chapter in memory
        await self.memory_service.remember(
            text=(
                f"Chapter {chapter_number}: {chapter.title}\n"
                f"Summary: {chapter.summary or 'No summary'}\n"
                f"Content excerpt: {(chapter.content or '')[:1500]}"
            ),
            dataset=novel.dataset_name,
            metadata={"type": "chapter", "chapter_id": chapter.id, "number": chapter_number}
        )
        
        logger.info(f"Added chapter {chapter_number} to novel {novel_id}")
        return chapter
    
    async def generate_content(
        self,
        novel_id: int,
        prompt: str,
        style: str = "continue",
        context: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """Generate content using AI"""
        novel = await self.get_novel(novel_id)
        if not novel:
            return {"error": "Novel not found"}
        
        # Recall relevant memory
        memory_results = await self.memory_service.recall(
            query=prompt,
            dataset=novel.dataset_name,
            limit=5
        )
        if context:
            memory_results.insert(0, {
                "text": context,
                "type": "editor_context",
                "relevance": 1.0
            })
        
        # Generate with LLM
        generated_text = await self.llm_service.generate_with_memory(
            prompt=prompt,
            memory_context=memory_results,
            temperature=temperature or 0.8
        )
        
        return {
            "generated_text": generated_text,
            "memory_used": memory_results
        }
    
    async def extract_characters_from_text(self, novel_id: int, text: str) -> Dict:
        """Extract characters from text and add them to novel"""
        novel = await self.get_novel(novel_id)
        if not novel:
            return {"error": "Novel not found"}
        
        # Extract character names
        characters = await self.llm_service.extract_characters(text)
        
        # Add characters to database
        added_characters = []
        for char_name in characters:
            # Check if character already exists
            existing = self.db.query(Character).filter(
                Character.novel_id == novel_id,
                Character.name.ilike(char_name)
            ).first()
            
            if not existing:
                new_char = Character(
                    novel_id=novel_id,
                    name=char_name,
                    role="character"
                )
                self.db.add(new_char)
                added_characters.append(char_name)
                
                # Store in memory
                await self.memory_service.remember(
                    text=f"Character: {char_name}",
                    dataset=novel.dataset_name,
                    metadata={"type": "character", "name": char_name}
                )
        
        self.db.commit()
        
        return {
            "characters": characters,
            "added": added_characters,
            "total": len(characters)
        }

    def _build_novel_memory_text(self, novel: Novel) -> str:
        """Build compact memory text for the latest novel state."""
        content_excerpt = (novel.content or "")[-2500:]
        return (
            f"Novel: {novel.title}\n"
            f"Genre: {novel.genre}\n"
            f"Description: {novel.description or 'No description'}\n"
            f"Status: {novel.status}\n"
            f"Latest content excerpt: {content_excerpt}"
        )
