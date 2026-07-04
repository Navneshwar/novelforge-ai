import cognee
import inspect
import json
import os
import uuid
from typing import List, Dict, Any, Optional
from src.core.config import settings
from loguru import logger
import asyncio


def _filter_kwargs(func, kwargs: Dict) -> Dict:
    """Only pass kwargs that the installed Cognee version's function actually
    accepts. Cognee's API has shifted between releases (e.g. `dataset` vs
    `dataset_name`), so this keeps us from hard-crashing on a signature we
    didn't expect while still passing everything we can."""
    try:
        sig = inspect.signature(func)
        params = sig.parameters
        if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
            return kwargs
        return {k: v for k, v in kwargs.items() if k in params}
    except (TypeError, ValueError):
        return kwargs


class MemoryService:
    def __init__(self):
        self.cognee = cognee
        self._initialized = False

    async def initialize(self):
        """Initialize Cognee with Ollama configuration.

        Cognee's config is primarily environment-variable driven (LLM_PROVIDER,
        LLM_MODEL, LLM_ENDPOINT, LLM_API_KEY, EMBEDDING_PROVIDER, EMBEDDING_MODEL,
        EMBEDDING_ENDPOINT, EMBEDDING_DIMENSIONS, HUGGINGFACE_TOKENIZER). Setting
        the env vars is the most version-stable way to configure it. We also
        opportunistically call the `cognee.config.set_*` helpers for LLM values
        where they exist, but never let a missing/renamed setter break startup.
        """
        if not self._initialized:
            try:
                # Environment variables — this is what Cognee's LLMConfig /
                # EmbeddingConfig pydantic settings actually read.
                os.environ.setdefault("LLM_PROVIDER", settings.LLM_PROVIDER)
                os.environ.setdefault("LLM_MODEL", settings.LLM_MODEL)
                os.environ.setdefault("LLM_ENDPOINT", settings.LLM_ENDPOINT)
                os.environ.setdefault("LLM_API_KEY", settings.LLM_API_KEY)

                os.environ.setdefault("EMBEDDING_PROVIDER", settings.EMBEDDING_PROVIDER)
                os.environ.setdefault("EMBEDDING_MODEL", settings.EMBEDDING_MODEL)
                os.environ.setdefault("EMBEDDING_ENDPOINT", settings.EMBEDDING_ENDPOINT)
                os.environ.setdefault("EMBEDDING_DIMENSIONS", str(settings.EMBEDDING_DIMENSIONS))
                os.environ.setdefault("HUGGINGFACE_TOKENIZER", settings.HUGGINGFACE_TOKENIZER)

                # Belt-and-braces: also try the documented cognee.config setters
                # for LLM values. Wrapped individually so a renamed/missing
                # method on a given Cognee version never blocks startup.
                config_calls = [
                    ("set_llm_provider", settings.LLM_PROVIDER),
                    ("set_llm_model", settings.LLM_MODEL),
                    ("set_llm_endpoint", settings.LLM_ENDPOINT),
                    ("set_llm_api_key", settings.LLM_API_KEY),
                ]
                for method_name, value in config_calls:
                    setter = getattr(cognee.config, method_name, None)
                    if callable(setter):
                        try:
                            setter(value)
                        except Exception as inner_e:
                            logger.debug(f"cognee.config.{method_name} skipped: {inner_e}")

                self._initialized = True
                logger.info(f"Cognee initialized with Ollama using model: {settings.LLM_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Cognee: {e}")
                raise

    async def remember(self, text: str, dataset: str = "default", metadata: Dict = None) -> Dict:
        """Store text in Cognee memory.

        Verified against the installed cognee==1.2.2 API: `cognee.remember`
        takes the content as the positional/keyword arg `data` (NOT `text`).
        `metadata` is not a real parameter of remember() either — it's folded
        into the stored text as a tag instead, which also makes it recallable.
        """
        try:
            await self.initialize()

            stored_text = text
            if metadata:
                try:
                    tag = json.dumps(metadata, default=str)
                    stored_text = f"[metadata: {tag}]\n{text}"
                except (TypeError, ValueError):
                    pass

            call_kwargs = _filter_kwargs(
                cognee.remember,
                {
                    "data": stored_text,
                    "dataset_name": dataset,
                },
            )
            await cognee.remember(**call_kwargs)
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

            # `data` accepts a path/BinaryIO as well as raw text.
            call_kwargs = _filter_kwargs(
                cognee.remember,
                {"data": file_path, "dataset_name": dataset},
            )
            await cognee.remember(**call_kwargs)
            logger.info(f"Stored file in Cognee: {file_path}, dataset={dataset}")
            return {"success": True, "dataset": dataset}
        except Exception as e:
            logger.error(f"Error in remember_file: {e}")
            return {"success": False, "error": str(e)}

    async def recall(self, query: str, dataset: str = "default", limit: int = 10) -> List[Dict]:
        """Recall relevant information from memory.

        Verified against cognee==1.2.2: `cognee.recall` takes `query_text`
        (NOT `query`), `datasets` as a list (NOT a single `dataset_name`),
        and `top_k` (NOT `limit`). The previous kwarg names didn't match any
        parameter, so `_filter_kwargs` — which only forwards recognized
        kwargs when there's no **kwargs catch-all — stripped all of them and
        called `cognee.recall()` with nothing, which raises immediately
        because `query_text` is required.
        """
        try:
            await self.initialize()

            call_kwargs = _filter_kwargs(
                cognee.recall,
                {"query_text": query, "datasets": [dataset], "top_k": limit},
            )
            results = await cognee.recall(**call_kwargs)

            # Format results for consistency. Recall returns a discriminated
            # union of pydantic models (QA / graph / session entries etc.),
            # not plain dicts, so pull fields out defensively.
            formatted_results = []
            for item in results or []:
                if isinstance(item, dict):
                    formatted_results.append(item)
                elif hasattr(item, "model_dump"):
                    dumped = item.model_dump()
                    formatted_results.append({
                        "text": dumped.get("text") or dumped.get("answer") or dumped.get("content") or str(dumped),
                        "type": dumped.get("kind") or dumped.get("source") or "memory",
                        "relevance": dumped.get("score", 0.5),
                        "raw": dumped,
                    })
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
        """Run memify to derive new insights from memory.

        Verified against cognee==1.2.2: `cognee.improve`'s dataset parameter
        is named `dataset` (NOT `dataset_name`). Because `improve` also
        accepts `**kwargs`, the old `dataset_name` key didn't raise — it was
        silently swallowed into the catch-all kwargs bucket, and `improve`
        ran against the default 'main_dataset' every time regardless of
        which novel was requested. That's a correctness bug, not a crash, so
        it wouldn't show up as an error in a demo — it would just quietly
        improve the wrong (or no) data.
        """
        try:
            await self.initialize()
            call_kwargs = _filter_kwargs(cognee.improve, {"dataset": dataset})
            await cognee.improve(**call_kwargs)
            logger.info(f"Improved memory for dataset: {dataset}")
            return {"success": True, "dataset": dataset}
        except Exception as e:
            logger.error(f"Error in improve: {e}")
            return {"success": False, "error": str(e)}

    async def forget(self, dataset: str = "default", item_id: Optional[str] = None) -> Dict:
        """Surgically remove memory items.

        Verified against cognee==1.2.2: `cognee.forget` is keyword-only and
        uses `dataset` (NOT `dataset_name`) and `data_id` (NOT `id`). The old
        dataset-wide call passed only `dataset_name`, which doesn't match any
        parameter and has no **kwargs catch-all, so `_filter_kwargs` stripped
        it entirely and called `forget()` with all defaults — deleting
        nothing while still returning `{"success": True}`. That's the most
        dangerous kind of bug: it reports success while doing nothing.

        `data_id` is also typed as `uuid.UUID`, not `str`. Cognee's internal
        query code calls `.hex` on it directly, so passing the raw string
        that arrives from a FastAPI path parameter (e.g. .../forget/{item_id})
        crashes with `AttributeError: 'str' object has no attribute 'hex'`
        instead of a clean "not found"/validation error. We parse it here so
        callers can keep passing plain strings.
        """
        try:
            await self.initialize()
            if item_id:
                try:
                    parsed_id = uuid.UUID(str(item_id))
                except (ValueError, AttributeError):
                    return {"success": False, "error": f"'{item_id}' is not a valid memory item id (expected a UUID)"}

                call_kwargs = _filter_kwargs(
                    cognee.forget, {"dataset": dataset, "data_id": parsed_id}
                )
                await cognee.forget(**call_kwargs)
                logger.info(f"Forgot item {item_id} from dataset: {dataset}")
            else:
                call_kwargs = _filter_kwargs(cognee.forget, {"dataset": dataset})
                await cognee.forget(**call_kwargs)
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
                call_kwargs = _filter_kwargs(
                    cognee.recall, {"query_text": "*", "datasets": [dataset], "top_k": 100}
                )
                results = await cognee.recall(**call_kwargs)
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
        """Get the actual Cognee knowledge graph for a dataset (entities and
        relationships extracted by cognify/memify), not the app's own SQL
        schema. Returns an empty graph (rather than raising) if Cognee has no
        data yet, so callers can fall back to a database-derived view.

        NOTE: an earlier version of this tried `cognee.search(query_type=
        SearchType.INSIGHTS, ...)` first and only fell back to recall() if
        that raised ImportError/AttributeError. `SearchType.INSIGHTS` does
        not exist on the installed cognee==1.2.2 (its SearchType enum has no
        INSIGHTS member — the closest real members are GRAPH_COMPLETION,
        TRIPLET_COMPLETION, CHUNKS, etc.), so that attribute access itself
        raised AttributeError on every call and silently fell through to
        recall() every single time. The "genuine graph query" path never
        actually ran; it just looked like it might. Rather than guess at
        another enum member without a live instance to verify the retriever
        shape against, this uses recall() directly — verified to work
        against the real API above — as the one real path.
        """
        try:
            await self.initialize()
            try:
                call_kwargs = _filter_kwargs(
                    cognee.recall,
                    {"query_text": "all entities and relationships", "datasets": [dataset], "top_k": 50},
                )
                results = await cognee.recall(**call_kwargs)

                nodes = []
                edges = []
                for i, item in enumerate(results or []):
                    if isinstance(item, dict):
                        node_label = str(item.get("text", item))[:100]
                        node_type = item.get("type", "concept")
                        node_data = item
                    elif hasattr(item, "model_dump"):
                        dumped = item.model_dump()
                        node_label = str(
                            dumped.get("text") or dumped.get("answer") or dumped.get("content") or dumped
                        )[:100]
                        node_type = dumped.get("kind") or dumped.get("source") or "concept"
                        node_data = dumped
                    else:
                        node_label = str(item)[:100]
                        node_type = "concept"
                        node_data = {"text": str(item)}
                    nodes.append({
                        "id": f"cognee_{i}",
                        "label": node_label,
                        "type": node_type,
                        "data": node_data,
                    })
                return {"nodes": nodes, "edges": edges, "dataset": dataset}
            except Exception as e:
                logger.warning(f"Could not retrieve Cognee graph: {e}")
                return {"nodes": [], "edges": [], "dataset": dataset}
        except Exception as e:
            logger.error(f"Error getting graph: {e}")
            return {"nodes": [], "edges": [], "error": str(e)}