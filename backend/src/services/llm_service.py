import ollama
import json
import asyncio
from typing import List, Dict, Any, Optional
from src.core.config import settings
from loguru import logger


class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.LLM_ENDPOINT.replace("/v1", ""))
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

    async def generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> str:
        """Generate text using Ollama"""
        try:
            # Combine context and prompt
            full_prompt = (
                f"Context:\n{context}\n\nTask:\n{prompt}" if context else prompt
            )

            response = await asyncio.to_thread(
                lambda: self.client.generate(
                    model=self.model,
                    prompt=full_prompt,
                    options={
                        "temperature": kwargs.get("temperature", self.temperature),
                        "num_predict": kwargs.get("max_tokens", self.max_tokens),
                        "top_p": kwargs.get("top_p", 0.9),
                    },
                )
            )

            return response.response

        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return f"[Error generating content: {str(e)}]"

    async def generate_with_memory(
        self, prompt: str, memory_context: List[Dict], **kwargs
    ) -> str:
        """Generate text with memory context"""
        try:
            # Format memory context
            context_text = (
                "\n".join(
                    [
                        f"📌 {item.get('type', 'Memory')}: {item.get('text', str(item))[:300]}"
                        for item in memory_context
                    ]
                )
                if memory_context
                else "No relevant memory found."
            )

            # Create structured prompt
            full_prompt = f"""You are a novelist AI assistant with perfect memory of the story.

RELEVANT STORY MEMORY:
{context_text}

CURRENT TASK:
{prompt}

Please write in a creative, engaging style that maintains consistency with all story details mentioned above.
"""

            response = await asyncio.to_thread(
                lambda: self.client.generate(
                    model=self.model,
                    prompt=full_prompt,
                    options={
                        "temperature": kwargs.get("temperature", self.temperature),
                        "num_predict": kwargs.get("max_tokens", self.max_tokens),
                        "top_p": kwargs.get("top_p", 0.9),
                    },
                )
            )

            return response.response

        except Exception as e:
            logger.error(f"Error generating with memory: {e}")
            return f"[Error generating content: {str(e)}]"

    async def extract_characters(self, text: str) -> List[str]:
        """Extract character names from text"""
        try:
            prompt = f"""Extract all character names from the following text. Return only the character names, one per line, no other text.

Text:
{text[:2000]}

Characters:
"""

            response = await asyncio.to_thread(
                lambda: self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={"temperature": 0.3, "num_predict": 200},
                )
            )

            # Parse response
            characters = [
                line.strip() for line in response.response.split("\n") if line.strip()
            ]
            return characters

        except Exception as e:
            logger.error(f"Error extracting characters: {e}")
            return []

    async def check_consistency(self, text: str, memory_context: List[Dict]) -> Dict:
        """Check text for consistency with memory"""
        try:
            context_text = (
                "\n".join(
                    [
                        f"📌 {item.get('type', 'Memory')}: {item.get('text', str(item))[:200]}"
                        for item in memory_context[:5]
                    ]
                )
                if memory_context
                else "No memory context available."
            )

            prompt = f"""Analyze the following writing for consistency with the established story memory.

STORY MEMORY:
{context_text}

NEW WRITING TO CHECK:
{text[:1500]}

Please identify any inconsistencies with the memory. Format your response as:
CONTRADICTIONS: [List any contradictions]
WARNINGS: [List any potential issues]
SUGGESTIONS: [Suggestions for improvement]
If no issues found, say "All clear."
"""

            response = await asyncio.to_thread(
                lambda: self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={"temperature": 0.3, "num_predict": 500},
                )
            )

            return {
                "analysis": response.response,
                "has_issues": "All clear" not in response.response,
            }

        except Exception as e:
            logger.error(f"Error checking consistency: {e}")
            return {"error": str(e), "has_issues": False}
