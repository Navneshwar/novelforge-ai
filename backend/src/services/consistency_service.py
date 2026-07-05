from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.models import Novel, Character, PlotPoint, Chapter
from src.services.memory_service import MemoryService
from src.services.llm_service import LLMService
from loguru import logger
import json
import asyncio

class ConsistencyService:
    def __init__(self, db: Session):
        self.db = db
        self.memory_service = MemoryService()
        self.llm_service = LLMService()
    
    async def check_novel_consistency(self, novel_id: int) -> Dict:
        """Run full consistency check on a novel"""
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return {"error": "Novel not found", "issues": []}
        
        issues = []
        
        # Check character consistency
        character_issues = await self._check_characters(novel_id)
        issues.extend(character_issues)
        
        # Check plot consistency
        plot_issues = await self._check_plot_points(novel_id)
        issues.extend(plot_issues)
        
        # Check memory consistency (real LLM-based contradiction check against
        # the most recently written chapter, using Cognee-recalled context)
        latest_chapter = (
            self.db.query(Chapter)
            .filter(Chapter.novel_id == novel_id)
            .order_by(Chapter.chapter_number.desc())
            .first()
        )
        memory_issues = await self._check_memory_consistency(
            novel.dataset_name,
            text_to_check=latest_chapter.content if latest_chapter else None,
        )
        issues.extend(memory_issues)
        
        # Check chapter continuity
        chapter_issues = await self._check_chapter_continuity(novel_id)
        issues.extend(chapter_issues)
        
        # Store issues in memory for later recall
        if issues:
            await self.memory_service.remember(
                text=f"Consistency issues found: {len(issues)} issues",
                dataset=novel.dataset_name,
                metadata={"type": "consistency_check", "issue_count": len(issues)}
            )
        
        return {
            "novel_id": novel_id,
            "total_issues": len(issues),
            "issues": issues,
            "status": "warning" if issues else "clear"
        }
    
    async def _check_characters(self, novel_id: int) -> List[Dict]:
        """Check character consistency"""
        issues = []
        characters = self.db.query(Character).filter(Character.novel_id == novel_id).all()
        
        # Check for duplicate characters
        names = {}
        for char in characters:
            if char.name.lower() in names:
                issues.append({
                    "type": "character",
                    "severity": "medium",
                    "title": f"Duplicate character: {char.name}",
                    "description": f"Character '{char.name}' appears multiple times with different IDs",
                    "location": f"Character: {char.name}",
                    "suggestion": "Merge or rename duplicate characters"
                })
            names[char.name.lower()] = char.id
        
        # Check for characters with no traits
        for char in characters:
            if not char.traits and not char.description:
                issues.append({
                    "type": "character",
                    "severity": "low",
                    "title": f"Underdeveloped character: {char.name}",
                    "description": f"Character '{char.name}' has no traits or description",
                    "location": f"Character: {char.name}",
                    "suggestion": "Add traits or description to develop this character"
                })
        
        return issues
    
    async def _check_plot_points(self, novel_id: int) -> List[Dict]:
        """Check plot consistency"""
        issues = []
        plot_points = self.db.query(PlotPoint).filter(PlotPoint.novel_id == novel_id).all()
        
        # Check for major plot points with no resolution
        unresolved = [p for p in plot_points if p.is_major and p.status != "resolved"]
        if len(unresolved) > 3:
            issues.append({
                "type": "plot",
                "severity": "high",
                "title": f"Unresolved major plot points: {len(unresolved)}",
                "description": f"Major plot points {', '.join([p.title for p in unresolved[:3]])} are unresolved",
                "location": "Overall plot",
                "suggestion": "Resolve major plot points before continuing"
            })
        
        # Check for inconsistent timeline
        plot_points_with_order = [p for p in plot_points if p.timeline_order is not None]
        if plot_points_with_order:
            orders = [p.timeline_order for p in plot_points_with_order]
            if len(set(orders)) != len(orders):
                issues.append({
                    "type": "timeline",
                    "severity": "high",
                    "title": "Duplicate timeline orders",
                    "description": "Multiple plot points share the same timeline order",
                    "location": "Plot timeline",
                    "suggestion": "Reassign timeline orders to avoid duplicates"
                })
        
        return issues
    
    async def _check_memory_consistency(
        self, dataset: str, text_to_check: Optional[str] = None
    ) -> List[Dict]:
        """Check consistency using Cognee-recalled context + an actual LLM
        contradiction analysis (llm_service.check_consistency), instead of
        just flagging whenever recall() returns any results at all — recall
        returns semantically related memories by design, not contradictions,
        so treating "got results" as "found a problem" produced a false
        positive on almost every run."""
        issues = []

        if not text_to_check or not text_to_check.strip():
            return issues

        try:
            memory_context = await asyncio.wait_for(
                self.memory_service.recall(
                    query=text_to_check[:500],
                    dataset=dataset,
                    limit=5
                ),
                timeout=15,
            )

            analysis = await asyncio.wait_for(
                self.llm_service.check_consistency(
                    text=text_to_check,
                    memory_context=memory_context
                ),
                timeout=20,
            )

            if analysis.get("has_issues"):
                issues.append({
                    "type": "consistency",
                    "severity": "medium",
                    "title": "Potential contradiction with story memory",
                    "description": analysis.get("analysis", "")[:500],
                    "location": "Memory layer",
                    "suggestion": "Review the flagged passage against established story details"
                })
        except asyncio.TimeoutError:
            logger.warning(
                f"Memory consistency check timed out for dataset={dataset} "
                "(local LLM took too long) — skipping this check for now"
            )
        except Exception as e:
            logger.error(f"Error checking memory consistency: {e}")

        return issues
    
    async def _check_chapter_continuity(self, novel_id: int) -> List[Dict]:
        """Check chapter continuity"""
        issues = []
        chapters = self.db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_number).all()
        
        if len(chapters) < 2:
            return issues
        
        # Check for gap in chapter numbers
        chapter_numbers = [c.chapter_number for c in chapters]
        expected_numbers = list(range(1, len(chapters) + 1))
        
        if set(chapter_numbers) != set(expected_numbers):
            issues.append({
                "type": "consistency",
                "severity": "low",
                "title": "Inconsistent chapter numbering",
                "description": f"Chapter numbers: {chapter_numbers}, expected: {expected_numbers}",
                "location": "Chapter structure",
                "suggestion": "Renumber chapters sequentially"
            })
        
        # Check for empty chapters
        for chapter in chapters:
            if not chapter.content or len(chapter.content.strip()) < 100:
                issues.append({
                    "type": "consistency",
                    "severity": "medium",
                    "title": f"Chapter {chapter.chapter_number} has insufficient content",
                    "description": f"Chapter {chapter.chapter_number} is too short or empty",
                    "location": f"Chapter {chapter.chapter_number}",
                    "suggestion": "Expand or remove this chapter"
                })
        
        return issues
    
    async def get_consistency_issues(self, novel_id: int) -> List[Dict]:
        """Get all consistency issues for a novel"""
        # Check if we have stored issues
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return []
        
        try:
            results = await self.memory_service.recall(
                query="consistency issue",
                dataset=novel.dataset_name,
                limit=20
            )
            
            # Extract issues from memory
            issues = []
            for item in results:
                if "issue" in str(item).lower():
                    issues.append({
                        "id": f"mem_{len(issues)}",
                        "type": "consistency",
                        "severity": "medium",
                        "title": "Memory consistency issue",
                        "description": str(item)[:200],
                        "location": "Memory"
                    })
            
            return issues
        except Exception as e:
            logger.error(f"Error getting consistency issues: {e}")
            return []
    
    async def resolve_issue(self, novel_id: int, issue_id: str) -> Dict:
        """Resolve a specific consistency issue"""
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            return {"error": "Novel not found"}
        
        # Remember the resolution
        await self.memory_service.remember(
            text=f"Resolved consistency issue: {issue_id}",
            dataset=novel.dataset_name,
            metadata={"type": "issue_resolution", "issue_id": issue_id}
        )
        
        logger.info(f"Resolved issue {issue_id} for novel {novel_id}")
        return {"success": True, "issue_id": issue_id}