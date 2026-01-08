# PARIS (Python-based Agentic Retrieval Interview System)

PARIS (Python-based Agentic Retrieval Interview System) is a powerful document processing and question-answering system that leverages Retrieval-Augmented Generation (RAG) to provide context-aware responses from your documents.

## Features

- **Document Processing**: Supports PDFs, Word documents, and web pages
- **Efficient Chunking**: Handles large documents with smart text chunking
- **Q&A System**: Get accurate answers based on document content
- **Document Summarization**: Generate concise summaries of uploaded documents
- **Question Generation**: Create practice questions from document content
- **Vector Search**: Fast and accurate semantic search using Qdrant
- **Web Interface**: User-friendly Streamlit-based UI

## Prerequisites

- Python 3.8+
- Qdrant server (local or remote)
- OpenAI API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd PARIS
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_URL=http://localhost:6333  # or your Qdrant server URL
   ```

## Running Qdrant

### Option 1: Local Qdrant with Docker (Recommended)

```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### Option 2: Qdrant Cloud

Sign up at [Qdrant Cloud](https://cloud.qdrant.io/) and get your cloud URL and API key.

## Running the Application

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

## Usage

1. **Upload Documents**: Use the sidebar to upload PDF, DOCX, or TXT files, or enter a URL to process web pages.
2. **Ask Questions**: Type your question in the main text area and click "Get Answer" to receive a response based on the document content.
3. **Generate Summary**: Use the "Document Actions" sidebar to generate a summary of the uploaded document.
4. **Create Practice Questions**: Generate multiple-choice questions based on the document content.

## Project Structure

- `app.py`: Main Streamlit application
- `rag_pipeline.py`: Core RAG pipeline implementation
- `vector_store.py`: Qdrant vector store integration
- `document_processor.py`: Document loading and processing utilities
- `config.py`: Configuration and settings
- `requirements.txt`: Python dependencies

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `QDRANT_URL`: URL of your Qdrant server (default: http://localhost:6333)
- `COLLECTION_NAME`: Name of the Qdrant collection (default: document_embeddings)

## Customization

You can customize the following parameters in `config.py`:
- `CHUNK_SIZE`: Size of text chunks (default: 1000 characters)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 characters)
- `EMBEDDING_MODEL`: OpenAI embedding model (default: "text-embedding-3-small")
- `LLM_MODEL`: OpenAI language model for generation (default: "gpt-3.5-turbo")

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain)
- [Qdrant](https://qdrant.tech/)
- [OpenAI](https://openai.com/)
- [Streamlit](https://streamlit.io/)
