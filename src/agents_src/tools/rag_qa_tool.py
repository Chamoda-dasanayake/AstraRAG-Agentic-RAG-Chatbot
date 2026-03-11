import logging
import chromadb
from crewai.tools import tool
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

from src.agents_src.config.agent_settings import AgentSettings

logger = logging.getLogger(__name__)

# Global variable to cache the index
_GLOBAL_INDEX = None

def get_index():
    """Helper to initialize the index only once, safely."""
    global _GLOBAL_INDEX
    if _GLOBAL_INDEX is not None:
        return _GLOBAL_INDEX

    try:
        settings = AgentSettings()
        
        # Configure LLM & Embeddings
        Settings.llm = Groq(
            model=settings.MODEL_NAME,
            temperature=settings.MODEL_TEMPERATURE,
            api_key=settings.GROQ_API_KEY,
        )
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

        # Setup Vector Store
        db = chromadb.PersistentClient(path=settings.VECTOR_STORE_DIR)
        chroma_collection = db.get_or_create_collection(settings.COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        _GLOBAL_INDEX = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        return _GLOBAL_INDEX
    except Exception as e:
        logger.error(f"Failed to initialize RAG Index: {e}")
        return None

@tool
def rag_query_tool(query: str) -> str:
    """Search the knowledge base for answers."""
    
    # 1. Basic input handling
    query_text = query["value"] if isinstance(query, dict) and "value" in query else str(query)

    # 2. Safety check for the index
    index = get_index()
    if index is None:
        return "Error: The knowledge base is currently unavailable. Please check backend logs."

    try:
        # 3. Query Execution (Keep top_k low for Groq Free Tier)
        query_engine = index.as_query_engine(similarity_top_k=2)
        response = query_engine.query(query_text)
        
        answer_text = str(response).strip() or "No relevant information found."
        
        if response.source_nodes:
            sources_info = "\n\nRetrieved Source Files:\n"
            # Get unique file names
            seen_files = set()
            for node in response.source_nodes:
                file_name = node.metadata.get('file_name', 'Unknown Source')
                if file_name not in seen_files:
                    sources_info += f"- {file_name}\n"
                    seen_files.add(file_name)
            answer_text += sources_info
            
        return answer_text

    except Exception as e:
        logger.exception("Tool execution failed")
        return f"Tool Error: {str(e)}"