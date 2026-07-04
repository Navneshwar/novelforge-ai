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
                cognee.config.set_llm_provider("ollama")
                cognee.config.set_llm_model(settings.LLM_MODEL)
                cognee.config.set_llm_endpoint(settings.LLM_ENDPOINT)
                
                cognee.config.set_embedding_provider("ollama")
                cognee.config.set_embedding_model(settings.EMBEDDING_MODEL)
                cognee.config.set_embedding_endpoint(settings.EMBEDDING_ENDPOINT)
                cognee.config.set_embedding_dimensions(settings.EMBEDDING_DIMENSIONS)
                
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
            await self.initialize()
            # Try to get stats from Cognee
            try:
                results = await cognee.recall(
                    query="*",
                    dataset=dataset,
                    limit=100
                )
                items_count = len(results) if results else 0
            except Exception:
                items_count = 0
            
            return {
                "dataset": dataset,
                "status": "active",
                "items_count": items_count,
                "total_embeddings": items_count
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "dataset": dataset,
                "status": "active",
                "items_count": 0,
                "total_embeddings": 0
            }
    
    async def get_graph(self, dataset: str = "default") -> Dict:
        """Get the knowledge graph for a dataset"""
        try:
            await self.initialize()
            # Attempt to retrieve graph data from Cognee
            try:
                # Cognee may expose graph data through its API
                results = await cognee.recall(
                    query="all entities and relationships",
                    dataset=dataset,
                    limit=50
                )
                nodes = []
                edges = []
                for i, item in enumerate(results or []):
                    node_label = str(item.get('text', item) if isinstance(item, dict) else item)[:100]
                    node_type = item.get('type', 'concept') if isinstance(item, dict) else 'concept'
                    nodes.append({
                        "id": f"cognee_{i}",
                        "label": node_label,
                        "type": node_type,
                        "data": item if isinstance(item, dict) else {"text": str(item)}
                    })
                return {"nodes": nodes, "edges": edges, "dataset": dataset}
            except Exception as e:
                logger.warning(f"Could not retrieve Cognee graph: {e}")
                return {"nodes": [], "edges": [], "dataset": dataset}
        except Exception as e:
            logger.error(f"Error getting graph: {e}")
            return {"nodes": [], "edges": [], "error": str(e)}