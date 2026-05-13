import logging
import tempfile
from pathlib import Path
from typing import List

import chromadb
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.schema import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from pypdf import PdfReader

from src.agents_src.config.agent_settings import AgentSettings
from src.agents_src.tools.rag_qa_tool import reset_index

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(
        self,
        vector_store_path: str = None,
        collection_name: str = None
    ):
        settings = AgentSettings()
        self.vector_store_path = vector_store_path or settings.VECTOR_STORE_DIR
        self.collection_name = collection_name or settings.COLLECTION_NAME
        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self._init_chroma_db()

    def _init_chroma_db(self):
        try:
            self.db = chromadb.PersistentClient(path=self.vector_store_path)
            self.chroma_collection = self.db.get_or_create_collection(
                name=self.collection_name
            )
            logger.info(f"ChromaDB initialized at {self.vector_store_path}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise

    def process_pdf(self, file_path: str, document_name: str = None) -> dict:
        """Parse PDF, chunk, embed, and upsert into Chroma."""
        try:
            if document_name is None:
                document_name = Path(file_path).stem

            logger.info(f"Processing PDF: {file_path}")

            pdf_text = self._extract_text_from_pdf(file_path)
            
            if not pdf_text.strip():
                logger.warning(f"No text extracted from PDF: {file_path}")
                return {
                    "success": False,
                    "message": "No text could be extracted from the PDF",
                    "document_name": document_name
                }

            parser = SimpleNodeParser.from_defaults(
                chunk_size=1024, 
                chunk_overlap=50
            )
            
            doc = Document(text=pdf_text, metadata={"source": document_name})
            nodes = parser.get_nodes_from_documents([doc])
            
            logger.info(f"Created {len(nodes)} nodes from {document_name}")

            vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            index = VectorStoreIndex(
                nodes,
                storage_context=storage_context,
                vector_store=vector_store,
                embed_model=self.embed_model
            )

            logger.info(f"Successfully indexed PDF: {document_name}")

            reset_index()
            logger.info("RAG index cache invalidated after new upload.")
            
            return {
                "success": True,
                "message": f"PDF '{document_name}' uploaded and indexed successfully",
                "document_name": document_name,
                "node_count": len(nodes),
                "text_length": len(pdf_text)
            }

        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error processing PDF: {str(e)}",
                "document_name": document_name
            }

    def process_pdf_bytes(self, pdf_bytes: bytes, document_name: str) -> dict:
        """Process in-memory PDF bytes via a temp file."""
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False
            ) as temp:
                temp.write(pdf_bytes)
                temp_file = temp.name

            return self.process_pdf(temp_file, document_name)

        except Exception as e:
            logger.error(f"Error processing PDF bytes: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error processing PDF: {str(e)}",
                "document_name": document_name
            }
        finally:
            if temp_file and Path(temp_file).exists():
                try:
                    Path(temp_file).unlink()
                except Exception as e:
                    logger.warning(f"Could not delete temp file: {e}")

    @staticmethod
    def _extract_text_from_pdf(file_path: str) -> str:
        """Extract plain text from a PDF path."""
        try:
            text = []
            with open(file_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)
                logger.info(f"PDF has {len(reader.pages)} pages")
                
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                    logger.debug(f"Extracted text from page {page_num}")

            return "\n".join(text)

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    def get_uploaded_documents(self) -> List[str]:
        """Distinct document names from Chroma metadata."""
        try:
            results = self.chroma_collection.get()
            documents = set()
            
            if results and results.get("metadatas"):
                for metadata in results["metadatas"]:
                    if metadata and "source" in metadata:
                        documents.add(metadata["source"])
            
            return sorted(list(documents))

        except Exception as e:
            logger.error(f"Error getting uploaded documents: {e}")
            return []

    def delete_document(self, document_name: str) -> dict:
        """Delete vectors whose metadata matches the given filename."""
        try:
            target_name = (document_name or "").strip()
            if not target_name:
                return {
                    "success": False,
                    "message": "Document name cannot be empty.",
                    "deleted_count": 0,
                    "document_name": document_name,
                }

            existing = self.chroma_collection.get(include=["metadatas"])
            ids = existing.get("ids", []) if existing else []
            metadatas = existing.get("metadatas", []) if existing else []

            target_lower = target_name.lower()
            matched_ids = []
            for item_id, metadata in zip(ids, metadatas):
                if not metadata:
                    continue
                source_val = str(metadata.get("source", "")).strip()
                file_name_val = str(metadata.get("file_name", "")).strip()

                candidates = {
                    source_val.lower(),
                    file_name_val.lower(),
                    Path(source_val).name.lower(),
                    Path(file_name_val).name.lower(),
                }
                candidates.discard("")

                if target_lower in candidates or Path(target_name).name.lower() in candidates:
                    matched_ids.append(item_id)

            if not matched_ids:
                return {
                    "success": False,
                    "message": f"Document '{target_name}' was not found in the index.",
                    "deleted_count": 0,
                    "document_name": target_name,
                }

            self.chroma_collection.delete(ids=matched_ids)
            reset_index()
            logger.info(f"Deleted {len(matched_ids)} vectors for document '{target_name}'")

            return {
                "success": True,
                "message": f"Document '{target_name}' removed successfully.",
                "deleted_count": len(matched_ids),
                "document_name": target_name,
            }
        except Exception as e:
            logger.error(f"Error deleting document '{document_name}': {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error deleting document: {str(e)}",
                "deleted_count": 0,
                "document_name": document_name,
            }
