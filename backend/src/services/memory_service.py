import cognee
import json
from typing import List, Dict, Any, Optional
from src.core.config import settings
from loguru import logger
import asyncio
import os

class MemoryService:
    def __init__(self):
        self.cognee = cognee
        self._initialized = False
    
    async def initialize(self):
        """Initialize Cognee with Ollama configuration"""
        if not self._initialized:
            try:
                # Configure Cognee for local Ollama
                await cognee.set_llm_provider(
                    provider="ollama",
                    model=settings.LLM_MODEL,
                    endpoint=settings.LLM_ENDPOINT
                )
                await cognee.set_embedding_provider(
                    provider="ollama",
                    model=settings.EMBEDDING_MODEL,
                    endpoint=settings.EMBEDDING_ENDPOINT,
                    dimensions=settings.EMBEDDING_DIMENSIONS
                )
                self._initialized = True
                logger.info(f"Cognee initialized with Ollama using model: {settings.LLM_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Cognee: {e}")
                raise
    
    async def remember(self, text: str, dataset: str = "default", metadata: Dict = None) -> Dict:
        """Store text in Cognee memory"""
        try:
            await self.initialize()
            result = await cognee.remember(
                text=text,
                dataset=dataset,
                metadata=metadata or {}
            )
            logger.info(f"Stored in Cognee: dataset={dataset}, text_length={len(text)}")
            return {"success": True, "dataset": dataset}
        except Exception as e:
            logger.error(f"Error in remember: {e}")
            return {"success": False, "error": str(e)}
    
    async def remember_file(self, file_path: str, dataset: str = "default") -> Dict:
        """Store file contents in Cognee memory"""
        try:
            await self.initialize()
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}
                
            result = await cognee.remember(
                file=file_path,
                dataset=dataset
            )
            logger.info(f"Stored file in Cognee: {file_path}, dataset={dataset}")
            return {"success": True, "dataset": dataset}
        except Exception as e:
            logger.error(f"Error in remember_file: {e}")
            return {"success": False, "error": str(e)}
    
    async def recall(self, query: str, dataset: str = "default", limit: int = 10) -> List[Dict]:
        """Recall relevant information from memory"""
        try:
            await self.initialize()
            results = await cognee.recall(
                query=query,
                dataset=dataset,
                limit=limit
            )
            
            # Format results for consistency
            formatted_results = []
            for item in results:
                if isinstance(item, dict):
                    formatted_results.append(item)
                else:
                    formatted_results.append({
                        "text": str(item),
                        "type": "memory",
                        "relevance": 0.5  # Default if not provided
                    })
            
            logger.info(f"Recalled {len(formatted_results)} items for query: {query[:50]}...")
            return formatted_results
        except Exception as e:
            logger.error(f"Error in recall: {e}")
            return []
    
    async def improve(self, dataset: str = "default") -> Dict:
        """Run memify to derive new insights from memory"""
        try:
            await self.initialize()
            result = await cognee.improve(dataset=dataset)
            logger.info(f"Improved memory for dataset: {dataset}")
            return {"success": True, "dataset": dataset}
        except Exception as e:
            logger.error(f"Error in improve: {e}")
            return {"success": False, "error": str(e)}
    
    async def forget(self, dataset: str = "default", item_id: Optional[str] = None) -> Dict:
        """Surgically remove memory items"""
        try:
            await self.initialize()
            if item_id:
                await cognee.forget(dataset=dataset, id=item_id)
                logger.info(f"Forgot item {item_id} from dataset: {dataset}")
            else:
                await cognee.forget(dataset=dataset)
                logger.info(f"Forgot entire dataset: {dataset}")
            return {"success": True, "dataset": dataset}
        except Exception as e:
            logger.error(f"Error in forget: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_stats(self, dataset: str = "default") -> Dict:
        """Get memory statistics for a dataset"""
        try:
            # This is a placeholder - Cognee may not have direct stats endpoint
            # We'll return basic info
            return {
                "dataset": dataset,
                "status": "active",
                "items_count": 0,  # Cognee doesn't provide count directly
                "total_embeddings": 0
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"dataset": dataset, "error": str(e)}
    
    async def get_graph(self, dataset: str = "default") -> Dict:
        """Get the knowledge graph for a dataset"""
        try:
            await self.initialize()
            # Cognee may have graph export functionality
            # This is a placeholder that returns empty graph
            return {
                "nodes": [],
                "edges": [],
                "dataset": dataset
            }
        except Exception as e:
            logger.error(f"Error getting graph: {e}")
            return {"nodes": [], "edges": [], "error": str(e)}