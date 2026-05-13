import logging
import chromadb
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from crewai.tools import tool

from src.agents_src.config.agent_settings import AgentSettings

logger = logging.getLogger(__name__)

_GLOBAL_INDEX = None


def reset_index():
    """Clear cached VectorStoreIndex."""
    global _GLOBAL_INDEX
    _GLOBAL_INDEX = None
    logger.info("RAG index cache invalidated.")


def get_index():
    """Build or return cached LlamaIndex over Chroma."""
    global _GLOBAL_INDEX
    if _GLOBAL_INDEX is not None:
        return _GLOBAL_INDEX

    try:
        settings = AgentSettings()

        temp = settings.MODEL_TEMPERATURE if settings.MODEL_TEMPERATURE is not None else 0.1
        if settings.uses_gemini():
            from llama_index.llms.google_genai import GoogleGenAI

            Settings.llm = GoogleGenAI(
                model=settings.google_genai_model_id(),
                api_key=settings.llm_api_key(),
                temperature=temp,
            )
        else:
            Settings.llm = OpenAI(
                api_key=settings.llm_api_key(),
                model=settings.llamaindex_openai_model(),
                temperature=temp,
            )
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

        db = chromadb.PersistentClient(path=settings.VECTOR_STORE_DIR)
        chroma_collection = db.get_or_create_collection(settings.COLLECTION_NAME)

        logger.info(f"ChromaDB collection '{settings.COLLECTION_NAME}' has {chroma_collection.count()} vectors")

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        _GLOBAL_INDEX = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        return _GLOBAL_INDEX
    except Exception as e:
        logger.error(f"Failed to initialize RAG Index: {e}", exc_info=True)
        return None


def retrieve_context(query: str, top_k: int = 3) -> str:
    """Run similarity search over the index; used before the crew."""
    index = get_index()
    if index is None:
        return "[ERROR: Knowledge base unavailable. No documents indexed yet.]"

    try:
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(query)

        answer_text = str(response).strip()
        if not answer_text:
            answer_text = "[No relevant content found in the knowledge base.]"

        sources = []
        if response.source_nodes:
            for node in response.source_nodes:
                src = node.metadata.get("source", node.metadata.get("file_name", "Unknown"))
                score = getattr(node, "score", None)
                chunk_text = node.text[:300] if node.text else ""
                score_str = f"{score:.3f}" if score is not None else "n/a"
                sources.append(f"Source: {src} (score: {score_str})\n{chunk_text}")

        if sources:
            answer_text += "\n\n--- Retrieved Chunks ---\n" + "\n\n".join(sources)

        logger.info(f"retrieve_context returned {len(sources)} source chunks for query: {query[:80]}")
        return answer_text

    except Exception as e:
        logger.error(f"retrieve_context failed: {e}", exc_info=True)
        return f"[Retrieval error: {e}]"


@tool
def rag_query_tool(query: str) -> str:
    """Search the knowledge base for answers to a question."""
    query_text = query["value"] if isinstance(query, dict) and "value" in query else str(query)
    return retrieve_context(query_text, top_k=3)