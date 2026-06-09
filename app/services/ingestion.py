from pathlib import Path
from fastapi import HTTPException
from llama_cloud import LlamaCloud
from app.core.config import settings


# Initialize the LlamaCloud client
client = LlamaCloud(api_key=settings.LLAMA_CLOUD_API_KEY)

def parse_pdf_document(file_path: str) -> str:
    """
    Uploads a PDF to LlamaCloud and uses the agentic tier to extract 
    text while preserving complex structures like tables in Markdown.
    """
    # 1. Upload the file to LlamaCloud
    file_obj = client.files.create(
        file=Path(file_path),
        purpose="parse"
    )
    
    # 2. Parse the uploaded file
    result = client.parsing.parse(
        file_id=file_obj.id,
        tier="agentic",  # The agentic tier is optimized for high-fidelity extraction
        version="latest",
        expand=["markdown"]
    )
    
    # 3. Combine extracted markdown from all pages
    markdown_content = []
    if result.markdown and result.markdown.pages:
        for page in result.markdown.pages:
            markdown_content.append(page.markdown)
            
    return "\n\n".join(markdown_content)

    