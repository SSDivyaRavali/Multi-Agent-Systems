import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import numpy as np
from config import QDRANT_URL, COLLECTION_NAME, EMBEDDING_MODEL, OPENAI_API_KEY
from openai import OpenAI

logger = logging.getLogger("documentor_rag.vector_store")

class VectorStoreManager:
    """Manages vector storage and retrieval using Qdrant."""
    
    def __init__(self):
        """Initialize the vector store with Qdrant client and OpenAI for embeddings."""
        self.client = QdrantClient(url=QDRANT_URL)
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.collection_name = COLLECTION_NAME
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create the collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # OpenAI text-embedding-3-small uses 1536 dimensions
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embeddings for the given text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def add_document(self, document_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """Add document chunks to the vector store."""
        try:
            points = []
            
            for chunk in chunks:
                embedding = self.get_embedding(chunk['text'])
                
                point = PointStruct(
                    id=f"{document_id}_{chunk['chunk_id']}",
                    vector=embedding,
                    payload={
                        'document_id': document_id,
                        'chunk_id': chunk['chunk_id'],
                        'text': chunk['text'],
                        'start_word': chunk['start_word'],
                        'end_word': chunk['end_word']
                    }
                )
                points.append(point)
            
            # Upsert points in batches to avoid timeouts
            batch_size = 20
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
            
            logger.info(f"Added {len(points)} chunks for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            return False
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks to the query."""
        try:
            query_embedding = self.get_embedding(query)
            
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            results = []
            for result in search_results:
                payload = result.payload
                results.append({
                    'document_id': payload['document_id'],
                    'chunk_id': payload['chunk_id'],
                    'text': payload['text'],
                    'score': result.score,
                    'start_word': payload['start_word'],
                    'end_word': payload['end_word']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a specific document."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
            logger.info(f"Deleted document {document_id} from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Retrieve all chunks for a specific document."""
        try:
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id)
                        )
                    ]
                ),
                limit=1000,  # Adjust based on expected max chunks per document
                with_vectors=False
            )
            
            chunks = []
            for point in scroll_result[0]:  # scroll_result is a tuple of (points, next_offset)
                payload = point.payload
                chunks.append({
                    'chunk_id': payload['chunk_id'],
                    'text': payload['text'],
                    'start_word': payload['start_word'],
                    'end_word': payload['end_word']
                })
            
            # Sort chunks by their position in the document
            chunks.sort(key=lambda x: x['chunk_id'])
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks for document {document_id}: {str(e)}")
            return []
