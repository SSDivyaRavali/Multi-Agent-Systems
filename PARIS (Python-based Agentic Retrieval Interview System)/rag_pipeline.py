import logging
import hashlib
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager

logger = logging.getLogger("documentor_rag.rag_pipeline")

class RAGPipeline:
    """Main RAG pipeline for document processing and question answering."""
    
    def __init__(self):
        """Initialize the RAG pipeline with document processor and vector store."""
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStoreManager()
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
    def _generate_document_id(self, source: str) -> str:
        """Generate a unique ID for a document based on its source."""
        return hashlib.md5(source.encode()).hexdigest()
    
    def add_document(self, file_path: str = None, url: str = None) -> Optional[str]:
        """
        Add a document to the RAG system from a file or URL.
        Returns the document ID if successful, None otherwise.
        """
        try:
            if file_path:
                source = f"file:{file_path}"
                text = self.document_processor.load_document(file_path)
            elif url:
                source = f"url:{url}"
                text = self.document_processor.load_webpage(url)
            else:
                raise ValueError("Either file_path or url must be provided")
            
            if not text:
                logger.error(f"Failed to extract text from {source}")
                return None
                
            doc_id = self._generate_document_id(source)
            
            # Chunk the document
            chunks = self.document_processor.chunk_text(
                text, 
                chunk_size=CHUNK_SIZE, 
                overlap=CHUNK_OVERLAP
            )
            
            # Add to vector store
            if self.vector_store.add_document(doc_id, chunks):
                logger.info(f"Successfully added document: {source}")
                return doc_id
            else:
                logger.error(f"Failed to add document to vector store: {source}")
                return None
                
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return None
    
    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        Returns a dictionary with the answer and relevant context.
        """
        try:
            # Search for relevant chunks
            relevant_chunks = self.vector_store.search_similar(question, top_k=top_k)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": []
                }
            
            # Prepare context for the LLM
            context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
            
            # Generate response using the LLM
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful assistant that answers questions based on the provided context. 
                    If you don't know the answer, just say that you don't know, don't try to make up an answer.
                    """
                },
                {
                    "role": "user",
                    "content": f"""Context: {context}
                    \n\nQuestion: {question}
                    \nAnswer the question based on the context above. If the context doesn't contain the answer, say you don't know.
                    """
                }
            ]
            
            response = self.openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Prepare sources (unique document IDs)
            sources = list({chunk['document_id'] for chunk in relevant_chunks})
            
            return {
                "answer": answer,
                "sources": sources,
                "relevant_chunks": relevant_chunks
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            return {
                "answer": "Sorry, I encountered an error while processing your question.",
                "sources": []
            }
    
    def generate_summary(self, document_id: str) -> Optional[str]:
        """Generate a summary of a document using the LLM."""
        try:
            # Get all chunks for the document
            chunks = self.vector_store.get_document_chunks(document_id)
            if not chunks:
                logger.error(f"No chunks found for document {document_id}")
                return None
            
            # Concatenate chunks (with a limit to avoid token limits)
            max_chars = 10000  # Conservative limit to avoid token limits
            full_text = ""
            for chunk in chunks:
                if len(full_text) + len(chunk['text']) > max_chars:
                    break
                full_text += "\n" + chunk['text']
            
            # Generate summary using the LLM
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates concise summaries of documents."
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following document in 3-5 bullet points:\n\n{full_text}"
                }
            ]
            
            response = self.openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary for document {document_id}: {str(e)}")
            return None
    
    def generate_questions(self, document_id: str, num_questions: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Generate multiple-choice questions based on the document content."""
        try:
            # Get all chunks for the document
            chunks = self.vector_store.get_document_chunks(document_id)
            if not chunks:
                logger.error(f"No chunks found for document {document_id}")
                return None
            
            # Sample chunks to avoid token limits
            sample_size = min(10, len(chunks))
            sample_chunks = chunks[:sample_size]
            context = "\n\n".join([chunk['text'] for chunk in sample_chunks])
            
            # Generate questions using the LLM
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful assistant that generates multiple-choice questions based on the provided context.
                    For each question, provide 4 options (a, b, c, d) and indicate the correct answer.
                    Format your response as a JSON array of objects with 'question', 'options', and 'answer' fields.
                    The 'options' field should be a dictionary with keys 'a', 'b', 'c', 'd'.
                    The 'answer' field should be the letter of the correct option (a, b, c, or d).
                    """
                },
                {
                    "role": "user",
                    "content": f"""Generate {num_questions} multiple-choice questions based on the following context:
                    \n\n{context}"""
                }
            ]
            
            response = self.openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            try:
                questions_data = json.loads(response.choices[0].message.content)
                if 'questions' in questions_data:
                    return questions_data['questions']
                return questions_data
            except json.JSONDecodeError:
                logger.error("Failed to parse questions from LLM response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return None
