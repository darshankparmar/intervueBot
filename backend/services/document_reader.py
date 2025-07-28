from agno.document import Document
from agno.document.chunking.fixed import FixedSizeChunking
from agno.vectordb.chroma import ChromaDb
from agno.embedder.base import Embedder
from dotenv import load_dotenv
from agno.embedder.google import GeminiEmbedder

import fitz

import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')

embedder = GeminiEmbedder(
    id='models/text-embedding-004',
    dimensions=1536,
    api_key=api_key
)

vector_db = ChromaDb(
    collection='embeddingTable',
    embedder=embedder,
    path='./chromaDb',
    persistent_client=True
)

async def document_embedding(file_data: dict):
    
    if vector_db.get_count() == 0:
        vector_db.create()
    else:
        print("Collection already exists")
    
    print("Embedding document")
    document = Document(
        content=file_data['text'],
        meta_data={
            'file_name': file_data['filename'],
            'user_id': file_data['user_id'],
            'created_at': file_data['created_at']
        }
    )
    
    print('document created...')
    
    chunking = FixedSizeChunking(
        chunk_size=1000,
        overlap=200
    )
    
    chunks = chunking.chunk(document)
    
    print("Chunks Created...")
    
    vector_db.insert(chunks)
    
    stored_count = vector_db.get_count()
    
    return {
        'message': 'Document embedded successfully',
        'chunks_count': len(chunks),
        "stored_vectors_count": stored_count,
        "status": "Success" if stored_count >= len(chunks) else "Partial/Failed"
    }
    
