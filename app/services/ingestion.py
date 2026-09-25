from pathlib import Path
from llama_parse import LlamaParse
from app.core.config import settings

# Initialize the LlamaParse client natively
parser = LlamaParse(
    api_key=settings.LLAMA_CLOUD_API_KEY,
    result_type="markdown",
    verbose=True
)

def parse_pdf_document(file_path: str) -> str:
    """
    Uploads a PDF to LlamaCloud to extract text while 
    preserving complex structures like tables in Markdown.
    """
    # load_data handles the upload, processing, and return cycle automatically
    documents = parser.load_data(file_path)
    
    # Combine extracted markdown text from the parsed document objects
    markdown_content = [doc.text for doc in documents]
            
    return "\n\n".join(markdown_content)