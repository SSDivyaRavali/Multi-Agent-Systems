import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup
import requests
import re

logger = logging.getLogger("documentor_rag.document_processor")

class DocumentProcessor:
    """Handles loading and processing of different document types."""
    
    @staticmethod
    def load_document(file_path: str) -> Optional[str]:
        """Load and extract text from a document based on its file extension."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
                
            if file_path.suffix.lower() == '.pdf':
                return DocumentProcessor._read_pdf(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return DocumentProcessor._read_docx(file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                return DocumentProcessor._read_html(file_path)
            elif file_path.suffix.lower() == '.txt':
                return DocumentProcessor._read_text(file_path)
            else:
                logger.warning(f"Unsupported file format: {file_path.suffix}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def _read_pdf(file_path: Path) -> str:
        """Extract text from PDF file."""
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    
    @staticmethod
    def _read_docx(file_path: Path) -> str:
        """Extract text from Word document."""
        doc = Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
    @staticmethod
    def _read_html(file_path: Path) -> str:
        """Extract text from HTML file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text()
    
    @staticmethod
    def _read_text(file_path: Path) -> str:
        """Read plain text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    @staticmethod
    def load_webpage(url: str) -> Optional[str]:
        """Load and extract text from a web page."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text and clean up
            text = soup.get_text()
            # Remove extra whitespace and newlines
            text = ' '.join(text.split())
            return text
            
        except Exception as e:
            logger.error(f"Error loading webpage {url}: {str(e)}")
            return None
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks with metadata."""
        if not text:
            return []
            
        words = text.split()
        chunks = []
        start = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = ' '.join(words[start:end])
            
            chunks.append({
                'text': chunk_text,
                'start_word': start,
                'end_word': end - 1,
                'chunk_id': len(chunks)
            })
            
            # Move forward, considering overlap
            if end == len(words):
                break
            start = end - overlap
            
        return chunks
