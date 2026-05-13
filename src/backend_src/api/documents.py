import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.backend_src.services.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize PDF processor
pdf_processor = PDFProcessor()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document to the vector store.
    
    Args:
        file: PDF file to upload
        
    Returns:
        dict with upload status and metadata
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        logger.info(f"Processing uploaded file: {file.filename}")
        
        # Process the PDF
        result = pdf_processor.process_pdf_bytes(
            content,
            document_name=file.filename
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return {
            "status": "success",
            "message": result["message"],
            "document_name": result["document_name"],
            "node_count": result.get("node_count"),
            "text_length": result.get("text_length")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/list")
def list_documents():
    """
    Get list of all uploaded documents.
    
    Returns:
        dict with list of document names
    """
    try:
        documents = pdf_processor.get_uploaded_documents()
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving document list"
        )


@router.delete("/delete")
def delete_document(document_name: str):
    """
    Delete an indexed document by its name.

    Args:
        document_name: Uploaded document filename

    Returns:
        dict with deletion result
    """
    if not document_name or not document_name.strip():
        raise HTTPException(status_code=400, detail="document_name is required")

    try:
        result = pdf_processor.delete_document(document_name.strip())
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("message", "Document not found"))
        return {
            "status": "success",
            "message": result["message"],
            "document_name": result["document_name"],
            "deleted_count": result["deleted_count"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document '{document_name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
