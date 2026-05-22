import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion import parse_pdf_document

router = APIRouter()

@router.post("/ingest/")
def ingest_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Safely write the uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.file.read())
            tmp_path = tmp_file.name
            
        # Parse the document synchronously
        parsed_markdown = parse_pdf_document(tmp_path)
        
        return {
            "filename": file.filename,
            "status": "success",
            "extracted_content": parsed_markdown
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Guarantee cleanup of the temporary file to prevent disk leaks
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)