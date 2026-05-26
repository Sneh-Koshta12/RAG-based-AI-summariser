import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion import parse_pdf_document
from app.services.vector_store import chunk_and_store_markdown

router = APIRouter()

@router.post("/ingest/")
def ingest_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.file.read())
            tmp_path = tmp_file.name
            
        # 1. Phase 1: Extract structured Markdown
        parsed_markdown = parse_pdf_document(tmp_path)
        
        # 2. Phase 2: Chunk, Embed, and Store in Database
        total_chunks = chunk_and_store_markdown(parsed_markdown, file.filename)
        
        return {
            "filename": file.filename,
            "status": "success",
            "message": f"Document processed and split into {total_chunks} vectorized chunks.",
            "extracted_preview": parsed_markdown[:500] + "..." # Just return a preview now to save bandwidth
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)