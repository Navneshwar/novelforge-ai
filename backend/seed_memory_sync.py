"""
NovelForge — sync seeded DB rows into Cognee memory.

seed.py writes chapters/characters/relationships straight into SQLite via
SQLAlchemy. That's how it builds the demo story quickly, but it means Cognee
never sees any of it — only the real API routes (POST /api/novels/{id}/chapters,
POST /api/characters/{novel_id}, etc.) call memory_service.remember(). If you
demo the graph visualizer right after `python seed.py`, it will be empty.

This script closes that gap: it reads back what seed.py already created and
calls remember() on each item, using the exact same text format the real
routes use, so the memory + graph you see live matches what a user going
through the actual UI would produce.

Also adds one throwaway character (Bram the Merchant) specifically so you
have something to demonstrate forget() on — added here, deleted live during
the demo.

Usage:
    cd backend
    python seed.py                 # creates the DB rows (run once)
    python seed_memory_sync.py     # pushes them into Cognee (run once)
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import SessionLocal
from src.models import Novel, Chapter, Character, CharacterRelationship
from src.services.memory_service import MemoryService


async def sync_to_memory():
    db = SessionLocal()
    memory_service = MemoryService()

    try:
        novel = db.query(Novel).first()
        if not novel:
            print("No novel found — run `python seed.py` first.")
            return

        print(f"Syncing '{novel.title}' (dataset: {novel.dataset_name}) into Cognee...")

        # ── Chapters — same format as novel_service.add_chapter() ──────
        chapters = (
            db.query(Chapter)
            .filter(Chapter.novel_id == novel.id)
            .order_by(Chapter.chapter_number)
            .all()
        )
        for ch in chapters:
            await memory_service.remember(
                text=(
                    f"Chapter {ch.chapter_number}: {ch.title}\n"
                    f"Summary: {ch.summary or 'No summary'}\n"
                    f"Content excerpt: {(ch.content or '')[:1500]}"
                ),
                dataset=novel.dataset_name,
                metadata={"type": "chapter", "chapter_id": ch.id, "number": ch.chapter_number},
            )
            print(f"  remembered chapter {ch.chapter_number}: {ch.title}")

        # ── Characters — same format as the character creation route ───
        characters = db.query(Character).filter(Character.novel_id == novel.id).all()
        for c in characters:
            await memory_service.remember(
                text=f"Character: {c.name}. Role: {c.role or 'character'}. Description: {c.description or 'No description'}",
                dataset=novel.dataset_name,
                metadata={"type": "character", "character_id": c.id, "name": c.name},
            )
            print(f"  remembered character: {c.name}")

        # ── Relationships — same format as the relationship route ──────
        rels = db.query(CharacterRelationship).join(
            Character, CharacterRelationship.source_id == Character.id
        ).filter(Character.novel_id == novel.id).all()
        char_by_id = {c.id: c for c in characters}
        for r in rels:
            source = char_by_id.get(r.source_id)
            target = char_by_id.get(r.target_id)
            if not source or not target:
                continue
            await memory_service.remember(
                text=f"Relationship: {source.name} - {r.relationship_type} -> {target.name}",
                dataset=novel.dataset_name,
                metadata={
                    "type": "relationship",
                    "source": source.name,
                    "target": target.name,
                    "relationship_type": r.relationship_type,
                },
            )
            print(f"  remembered relationship: {source.name} -> {target.name}")

        # ── Demo-only throwaway character, for the forget() demo ───────
        bram_existing = db.query(Character).filter(
            Character.novel_id == novel.id, Character.name == "Bram the Merchant"
        ).first()
        if not bram_existing:
            bram = Character(
                novel_id=novel.id,
                name="Bram the Merchant",
                description="A minor trader Elara buys supplies from in Velanor. Not part of the main plot.",
                role="minor",
            )
            db.add(bram)
            db.commit()
            db.refresh(bram)
        else:
            bram = bram_existing

        await memory_service.remember(
            text=f"Character: {bram.name}. Role: minor. Description: {bram.description}",
            dataset=novel.dataset_name,
            metadata={"type": "character", "character_id": bram.id, "name": bram.name},
        )
        print(f"  remembered throwaway character: {bram.name} (id={bram.id}) — use this for the forget() demo")

        print(f"\nDone. Dataset '{novel.dataset_name}' now has real Cognee memory.")
        print(f"Novel ID: {novel.id} — open it in the app and check the graph visualizer.")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(sync_to_memory())
