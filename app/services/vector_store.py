from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from app.core.config import settings

# Initialize MongoDB Connection
client = MongoClient(settings.MONGO_URI)
collection = client[settings.MONGO_DB_NAME][settings.MONGO_COLLECTION_NAME]

# Initialize Local Open-Source Embedding Model
# "all-MiniLM-L6-v2" is fast and lightweight. 
# For higher accuracy, you can change this to "BAAI/bge-small-en-v1.5"
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    # If you have an NVIDIA GPU, change "cpu" to "cuda" below
    model_kwargs={'device': 'cpu'}, 
    encode_kwargs={'normalize_embeddings': True} # Normalization improves cosine similarity search
)

# Initialize Vector Store Interface
vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,
    index_name="vector_index" 
)

def chunk_and_store_markdown(markdown_text: str, filename: str):
    """
    Splits markdown semantically by headers, then by character limits, 
    and uploads the embedded chunks to MongoDB Atlas using local embeddings.
    """
    # 1. Semantic Splitting
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    header_splits = markdown_splitter.split_text(markdown_text)

    # 2. Size Splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    final_chunks = text_splitter.split_documents(header_splits)

    # 3. Inject Metadata
    for chunk in final_chunks:
        chunk.metadata["source_file"] = filename

    # 4. Generate Embeddings locally and Store in MongoDB
    vector_store.add_documents(final_chunks)
    
    return len(final_chunks)