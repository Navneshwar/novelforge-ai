"""
NovelForge AI - Database Seed Script
Creates demo data for testing: a novel with chapters, characters, and plot points.

Usage:
    cd backend
    python seed.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import init_db, SessionLocal
from src.models import Novel, Chapter, Character, CharacterRelationship, PlotPoint, PlotArc
import uuid
from datetime import datetime


def seed_database():
    """Seed the database with demo data"""
    print("🌱 Seeding NovelForge database...")
    
    # Initialize tables
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(Novel).first()
        if existing:
            print("⚠️  Database already has data. Skipping seed.")
            print(f"   Found novel: '{existing.title}' (ID: {existing.id})")
            return
        
        # ── Create Novel ─────────────────────────────────────────────
        dataset_name = f"novel_{uuid.uuid4().hex[:8]}"
        novel = Novel(
            title="The Forgotten Kingdom",
            genre="Fantasy",
            description="In a world where memories are currency, a young archivist discovers that the kingdom's greatest treasure—its collective memory—is being systematically erased. She must journey through the Shattered Lands to restore what was lost before the kingdom forgets itself entirely.",
            content="",
            word_count=0,
            status="writing",
            dataset_name=dataset_name,
            writing_style="Epic fantasy with introspective moments",
            target_word_count=80000
        )
        db.add(novel)
        db.commit()
        db.refresh(novel)
        print(f"📖 Created novel: '{novel.title}' (ID: {novel.id})")
        
        # ── Create Chapters ──────────────────────────────────────────
        chapters_data = [
            {
                "title": "The Last Archive",
                "chapter_number": 1,
                "content": """The Archive of Echoes stood at the heart of Velanor, its crystalline spires catching the dawn light like frozen memories. Elara pressed her palm against the cold surface of the entrance stone, feeling the familiar pulse of stored knowledge beneath her fingertips.

"Another day, another thousand memories to catalog," she murmured, stepping into the vast atrium where countless memory crystals floated in silent orbit.

But today was different. The crystals near the eastern wing had gone dark overnight—not dimmed, not flickering, but completely empty. Twenty years of kingdom history, vanished as if they had never existed.

Elara's hands trembled as she activated the diagnostic protocols. The Archive had never lost a single memory in its three-hundred-year history. Someone—or something—was systematically erasing the kingdom's past.""",
                "summary": "Elara discovers that memories are disappearing from the Archive of Echoes. The crystalline memory storage system that has preserved Velanor's history for three centuries is being emptied.",
                "status": "writing"
            },
            {
                "title": "The Memory Thief",
                "chapter_number": 2,
                "content": """The Council of Remembrance convened in emergency session, their faces grave in the amber glow of the remaining memory crystals. Grand Archivist Theron sat at the head of the obsidian table, his silver hair catching light like a crown.

"Three more sections went dark last night," Elara reported, her voice steady despite the fear coiling in her chest. "The memories of the founding wars, the first treaties with the Thornwalkers, and—" she hesitated, "—the location of the Heartstone."

A murmur rippled through the council. The Heartstone was Velanor's most closely guarded secret, the source of the kingdom's ability to preserve memories at all.

"If someone has stolen the Heartstone's location from our memories," Theron said slowly, "then they intend to find it. And if they find it, they can destroy everything we are."

Kael, the young captain of the Memory Guard, stepped forward. "I've tracked anomalous energy signatures to the Shattered Lands. Whatever is draining our memories, it's coming from beyond the border."

Elara met his eyes. "Then that's where I need to go.\"""",
                "summary": "The Council of Remembrance discovers the scale of the memory loss. The Heartstone's location has been erased. Kael traces the source to the Shattered Lands. Elara volunteers to investigate.",
                "status": "writing"
            },
            {
                "title": "Beyond the Border",
                "chapter_number": 3,
                "content": """The Shattered Lands earned their name from the cataclysm that had torn the continent apart centuries ago—or so the histories claimed. But as Elara crossed the border with Kael at her side, she realized the landscape looked nothing like the descriptions in the Archive.

Instead of barren wasteland, she found forests of glass trees that sang in the wind, rivers of liquid silver, and creatures made of pure light that watched them from the shadows.

"This doesn't match any of our records," Kael said, his hand resting on his sword hilt.

"That's because our records have been altered," Elara whispered, understanding dawning. "Someone didn't just steal memories from the Archive. They replaced them with lies. We've been remembering a false history."

A figure emerged from between the glass trees—a woman with skin like polished obsidian and eyes that swirled with captured starlight.

"Welcome, Archivist," the woman said. "I am Nyra, last keeper of the true memories. I've been waiting for someone brave enough to question the kingdom's lies.\"""",
                "summary": "Elara and Kael enter the Shattered Lands and discover it's nothing like the Archive described. They meet Nyra, who reveals the kingdom's memories have been deliberately falsified.",
                "status": "draft"
            }
        ]
        
        for ch_data in chapters_data:
            chapter = Chapter(
                novel_id=novel.id,
                title=ch_data["title"],
                chapter_number=ch_data["chapter_number"],
                content=ch_data["content"],
                word_count=len(ch_data["content"].split()),
                summary=ch_data["summary"],
                status=ch_data["status"]
            )
            db.add(chapter)
        
        db.commit()
        print(f"📚 Created {len(chapters_data)} chapters")
        
        # ── Create Characters ────────────────────────────────────────
        characters_data = [
            {
                "name": "Elara Voss",
                "description": "A brilliant young archivist with an eidetic memory and a burning curiosity that often leads her into danger.",
                "role": "protagonist",
                "traits": ["curious", "determined", "empathetic", "analytical"],
                "physical_description": "Tall and slender with copper hair that she keeps in a practical braid. Her eyes are an unusual violet—a trait shared by those with natural affinity for memory magic.",
                "background": "Orphaned at seven when her parents disappeared during a memory expedition to the Shattered Lands. Raised by Grand Archivist Theron, who recognized her exceptional talent for memory preservation.",
                "personality": "Intellectually fearless but emotionally guarded. She processes the world through knowledge and facts, struggling with uncertainty. Deeply loyal to those she trusts.",
                "goals": ["Discover what happened to her parents", "Restore the stolen memories", "Uncover the truth about the kingdom's history"],
                "fears": ["Losing her own memories", "Being alone", "Failing to protect the Archive"],
                "strengths": ["Eidetic memory", "Memory magic affinity", "Analytical thinking", "Determination"],
                "weaknesses": ["Emotionally distant", "Stubborn", "Tendency to act alone"],
                "age": 23,
                "gender": "Female",
                "occupation": "Junior Archivist",
                "location": "Archive of Echoes, Velanor",
                "first_appearance": 1,
                "importance_score": 1.0
            },
            {
                "name": "Kael Stormblade",
                "description": "Captain of the Memory Guard, sworn to protect the Archive and its keepers. Honorable but hiding a dangerous secret.",
                "role": "deuteragonist",
                "traits": ["brave", "loyal", "conflicted", "protective"],
                "physical_description": "Broad-shouldered with dark skin and close-cropped black hair. A jagged scar runs from his left temple to his jaw—a wound that cost him three years of memories.",
                "background": "Born in the outer territories, Kael joined the Memory Guard after a memory beast attack killed his family and erased three years of his life. He rose through the ranks through sheer determination.",
                "personality": "Stoic and disciplined on the surface, but driven by deep emotions he rarely shows. His missing memories haunt him, making him fiercely protective of others' right to remember.",
                "goals": ["Recover his lost memories", "Protect Elara", "Bring the memory thief to justice"],
                "fears": ["Losing more memories", "Failing to protect those he's sworn to guard"],
                "strengths": ["Combat expertise", "Strategic thinking", "Unwavering loyalty"],
                "weaknesses": ["Missing memories create blind spots", "Overprotective", "Difficulty trusting"],
                "age": 28,
                "gender": "Male",
                "occupation": "Captain, Memory Guard",
                "location": "Velanor",
                "first_appearance": 2,
                "importance_score": 0.9
            },
            {
                "name": "Nyra",
                "description": "A mysterious woman from the Shattered Lands who claims to be the keeper of the kingdom's true memories.",
                "role": "supporting",
                "traits": ["enigmatic", "wise", "ancient", "truthful"],
                "physical_description": "Skin like polished obsidian, eyes that swirl with captured starlight. Ageless in appearance, moving with fluid grace.",
                "background": "Claims to have been alive since before the cataclysm, preserving the true history that the kingdom chose to forget.",
                "personality": "Patient and cryptic, speaking in layers of meaning. She has waited centuries for someone to seek the truth.",
                "goals": ["Restore the true history", "End the cycle of deliberate forgetting"],
                "fears": ["The true memories dying with her"],
                "strengths": ["Ancient knowledge", "True memory preservation", "Immunity to memory manipulation"],
                "weaknesses": ["Cannot leave the Shattered Lands", "Bound by ancient oaths"],
                "age": None,
                "gender": "Female",
                "occupation": "Keeper of True Memories",
                "location": "Shattered Lands",
                "first_appearance": 3,
                "importance_score": 0.8
            },
            {
                "name": "Grand Archivist Theron",
                "description": "The aging head of the Archive of Echoes, Elara's mentor and surrogate father. He knows more than he reveals.",
                "role": "supporting",
                "traits": ["wise", "secretive", "protective", "burdened"],
                "physical_description": "Elderly with flowing silver hair and kind but troubled grey eyes. Always wears the ceremonial robes of the Grand Archivist.",
                "background": "Has served as Grand Archivist for forty years. He was the one who found orphaned Elara and raised her within the Archive.",
                "personality": "Gentle and scholarly, but carries a heavy weight of secrets. His loyalty is divided between protecting Elara and protecting the kingdom's carefully constructed narrative.",
                "goals": ["Protect Elara", "Maintain the Archive", "Guard the kingdom's secrets"],
                "fears": ["Elara discovering the truth about her parents", "The Archive's destruction"],
                "strengths": ["Vast knowledge", "Political influence", "Memory magic mastery"],
                "weaknesses": ["Age", "Conflicted loyalties", "Guilt over past decisions"],
                "age": 72,
                "gender": "Male",
                "occupation": "Grand Archivist",
                "location": "Archive of Echoes, Velanor",
                "first_appearance": 2,
                "importance_score": 0.7
            },
            {
                "name": "The Erasure",
                "description": "A shadowy entity that feeds on memories, growing stronger with each one it consumes. Its true nature and origin are unknown.",
                "role": "antagonist",
                "traits": ["relentless", "intelligent", "ancient", "hungry"],
                "physical_description": "Appears as a shifting void in the shape of a person, with tendrils of darkness that reach toward memories like a predator stalking prey.",
                "background": "Unknown. Appears to have awakened recently, but some evidence suggests it has existed since the cataclysm—perhaps even caused it.",
                "personality": "Not truly sentient in a human sense, but possesses a cunning intelligence focused entirely on consuming and growing.",
                "goals": ["Consume all memories in the kingdom", "Reach the Heartstone"],
                "fears": ["True memories", "The Heartstone's power"],
                "strengths": ["Memory manipulation", "Growing power", "Cannot be physically harmed"],
                "weaknesses": ["True memories act as a barrier", "Weakened by strong emotional bonds"],
                "age": None,
                "gender": None,
                "occupation": None,
                "location": "Unknown",
                "first_appearance": 1,
                "importance_score": 0.85
            }
        ]
        
        character_objects = []
        for char_data in characters_data:
            character = Character(
                novel_id=novel.id,
                name=char_data["name"],
                description=char_data["description"],
                role=char_data["role"],
                traits=char_data["traits"],
                physical_description=char_data["physical_description"],
                background=char_data["background"],
                personality=char_data["personality"],
                goals=char_data["goals"],
                fears=char_data["fears"],
                strengths=char_data["strengths"],
                weaknesses=char_data["weaknesses"],
                age=char_data["age"],
                gender=char_data["gender"],
                occupation=char_data["occupation"],
                location=char_data["location"],
                first_appearance=char_data.get("first_appearance"),
                importance_score=char_data.get("importance_score", 0.5)
            )
            db.add(character)
            character_objects.append(character)
        
        db.commit()
        for c in character_objects:
            db.refresh(c)
        print(f"👥 Created {len(characters_data)} characters")
        
        # ── Create Character Relationships ───────────────────────────
        # Elara (0) ↔ Kael (1)
        relationships = [
            {
                "source": character_objects[0],
                "target": character_objects[1],
                "type": "ally",
                "description": "Traveling companions on the journey to the Shattered Lands. Growing mutual trust and unspoken attraction.",
                "strength": 0.8
            },
            {
                "source": character_objects[0],
                "target": character_objects[3],
                "type": "family",
                "description": "Theron raised Elara as a surrogate father after her parents vanished.",
                "strength": 0.95
            },
            {
                "source": character_objects[0],
                "target": character_objects[2],
                "type": "ally",
                "description": "Nyra holds answers Elara desperately needs. Their relationship is built on cautious trust.",
                "strength": 0.5
            },
            {
                "source": character_objects[0],
                "target": character_objects[4],
                "type": "enemy",
                "description": "The Erasure threatens everything Elara has sworn to protect.",
                "strength": 0.9
            },
            {
                "source": character_objects[1],
                "target": character_objects[3],
                "type": "subordinate",
                "description": "Kael serves under Theron's authority as Captain of the Memory Guard.",
                "strength": 0.6
            },
        ]
        
        for rel_data in relationships:
            rel = CharacterRelationship(
                source_id=rel_data["source"].id,
                target_id=rel_data["target"].id,
                relationship_type=rel_data["type"],
                description=rel_data["description"],
                strength=rel_data["strength"]
            )
            db.add(rel)
        
        db.commit()
        print(f"🔗 Created {len(relationships)} character relationships")
        
        # ── Create Plot Points ───────────────────────────────────────
        plot_points_data = [
            {
                "title": "Discovery of Memory Loss",
                "description": "Elara discovers that memories are being systematically erased from the Archive of Echoes.",
                "event_type": "inciting",
                "chapter": 1,
                "timeline_order": 1,
                "is_major": True,
                "importance": 1.0,
                "emotional_weight": 0.8,
                "involved_characters": [character_objects[0].id],
                "tags": ["mystery", "discovery"],
                "notes": "This is the catalyst that sets the entire plot in motion."
            },
            {
                "title": "Emergency Council Meeting",
                "description": "The Council of Remembrance learns the Heartstone's location has been erased.",
                "event_type": "rising_action",
                "chapter": 2,
                "timeline_order": 2,
                "is_major": True,
                "importance": 0.9,
                "emotional_weight": 0.7,
                "involved_characters": [character_objects[0].id, character_objects[1].id, character_objects[3].id],
                "tags": ["politics", "revelation"]
            },
            {
                "title": "Journey to the Shattered Lands",
                "description": "Elara and Kael cross the border into the unknown territory.",
                "event_type": "rising_action",
                "chapter": 3,
                "timeline_order": 3,
                "is_major": True,
                "importance": 0.85,
                "emotional_weight": 0.6,
                "involved_characters": [character_objects[0].id, character_objects[1].id],
                "tags": ["adventure", "journey"]
            },
            {
                "title": "Meeting Nyra",
                "description": "Elara and Kael encounter Nyra, who reveals the kingdom's history has been falsified.",
                "event_type": "rising_action",
                "chapter": 3,
                "timeline_order": 4,
                "is_major": True,
                "importance": 0.95,
                "emotional_weight": 0.9,
                "involved_characters": [character_objects[0].id, character_objects[1].id, character_objects[2].id],
                "tags": ["revelation", "twist"]
            },
            {
                "title": "The Heartstone Quest",
                "description": "The group must find the Heartstone before The Erasure reaches it.",
                "event_type": "rising_action",
                "chapter": None,
                "timeline_order": 5,
                "is_major": True,
                "importance": 0.9,
                "status": "planned",
                "involved_characters": [character_objects[0].id, character_objects[1].id, character_objects[2].id],
                "tags": ["quest", "urgency"]
            },
        ]
        
        for pp_data in plot_points_data:
            pp = PlotPoint(
                novel_id=novel.id,
                title=pp_data["title"],
                description=pp_data["description"],
                event_type=pp_data["event_type"],
                chapter=pp_data.get("chapter"),
                timeline_order=pp_data["timeline_order"],
                is_major=pp_data["is_major"],
                importance=pp_data["importance"],
                emotional_weight=pp_data.get("emotional_weight", 0.5),
                involved_characters=pp_data.get("involved_characters"),
                tags=pp_data.get("tags"),
                notes=pp_data.get("notes"),
                status=pp_data.get("status", "drafted")
            )
            db.add(pp)
        
        db.commit()
        print(f"📍 Created {len(plot_points_data)} plot points")
        
        # ── Create Plot Arc ──────────────────────────────────────────
        arc = PlotArc(
            novel_id=novel.id,
            name="The Memory Conspiracy",
            description="The main plot arc following Elara's discovery that the kingdom's memories are being stolen, leading to the revelation that the kingdom's entire history was deliberately falsified.",
            arc_type="main",
            start_chapter=1,
            end_chapter=None,
            status="active",
            plot_point_ids=[1, 2, 3, 4, 5],
            notes="This arc should culminate in a confrontation between Elara and whoever is behind the memory theft.",
            themes=["truth vs. comfortable lies", "the power of memory", "identity", "sacrifice"]
        )
        db.add(arc)
        db.commit()
        print(f"🏛️  Created plot arc: '{arc.name}'")
        
        # ── Update novel content with all chapters ────────────────────
        all_content = ""
        for ch in db.query(Chapter).filter(Chapter.novel_id == novel.id).order_by(Chapter.chapter_number).all():
            all_content += f"\n\n## Chapter {ch.chapter_number}: {ch.title}\n\n{ch.content}"
        
        novel.content = all_content.strip()
        novel.word_count = len(all_content.split())
        novel.last_written_at = datetime.utcnow()
        db.commit()
        
        print(f"\n✅ Seed complete!")
        print(f"   Novel: '{novel.title}' (ID: {novel.id})")
        print(f"   Chapters: {len(chapters_data)}")
        print(f"   Characters: {len(characters_data)}")
        print(f"   Relationships: {len(relationships)}")
        print(f"   Plot Points: {len(plot_points_data)}")
        print(f"   Word Count: {novel.word_count}")
        print(f"\n🚀 Start the server with: python main.py")
        print(f"   Then open: http://localhost:3000")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
