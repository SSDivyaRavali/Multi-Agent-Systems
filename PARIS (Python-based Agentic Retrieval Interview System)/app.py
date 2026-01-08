import os
import streamlit as st
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from config import UPLOAD_FOLDER, LOGGING_CONFIG
from rag_pipeline import RAGPipeline
import logging.config

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("documentor_rag.app")

# Initialize the RAG pipeline
@st.cache_resource
def get_rag_pipeline():
    return RAGPipeline()

rag_pipeline = get_rag_pipeline()

def setup_page():
    """Set up the Streamlit page configuration."""
    st.set_page_config(
        page_title="DocuMentor RAG",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📚 DocuMentor RAG")
    st.markdown("""
    **Document Understanding and Question Answering System**  
    Upload documents or enter a URL to get started.
    """)

def handle_file_upload() -> List[str]:
    """Handle file uploads and return list of document IDs."""
    st.sidebar.header("Upload Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Choose files", 
        type=['pdf', 'docx', 'txt', 'html'],
        accept_multiple_files=True
    )
    
    document_ids = []
    if uploaded_files:
        with st.spinner("Processing uploaded files..."):
            for uploaded_file in uploaded_files:
                try:
                    # Save the uploaded file temporarily
                    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Process the document
                    doc_id = rag_pipeline.add_document(file_path=file_path)
                    if doc_id:
                        document_ids.append(doc_id)
                        st.sidebar.success(f"Processed: {uploaded_file.name}")
                    else:
                        st.sidebar.error(f"Failed to process: {uploaded_file.name}")
                        
                except Exception as e:
                    logger.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    st.sidebar.error(f"Error processing {uploaded_file.name}")
    
    return document_ids

def handle_url_input() -> List[str]:
    """Handle URL input and return list of document IDs."""
    st.sidebar.header("Or enter a URL")
    url = st.sidebar.text_input("Enter a URL to process:")
    document_ids = []
    
    if url:
        if st.sidebar.button("Process URL"):
            with st.spinner(f"Processing URL: {url}..."):
                try:
                    doc_id = rag_pipeline.add_document(url=url)
                    if doc_id:
                        document_ids.append(doc_id)
                        st.sidebar.success(f"Successfully processed URL")
                    else:
                        st.sidebar.error("Failed to process URL")
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {str(e)}")
                    st.sidebar.error("Error processing URL")
    
    return document_ids

def display_qa_interface():
    """Display the question-answering interface."""
    st.header("Ask a Question")
    question = st.text_area("Enter your question about the document(s):", height=100)
    
    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Please enter a question.")
            return
            
        with st.spinner("Searching for answers..."):
            try:
                result = rag_pipeline.query(question)
                
                st.subheader("Answer:")
                st.write(result["answer"])
                
                if result.get("relevant_chunks"):
                    with st.expander("View relevant context"):
                        for i, chunk in enumerate(result["relevant_chunks"][:3]):  # Show top 3 chunks
                            st.markdown(f"**Context {i+1}** (Score: {chunk['score']:.2f})")
                            st.text(chunk['text'][:500] + (chunk['text'][500:] and '...'))
                            st.markdown("---")
                
            except Exception as e:
                logger.error(f"Error in QA: {str(e)}")
                st.error("An error occurred while processing your question. Please try again.")

def display_document_actions():
    """Display actions for document analysis."""
    st.sidebar.markdown("---")
    st.sidebar.header("Document Actions")
    
    action = st.sidebar.radio(
        "Choose an action:",
        ["Question Answering", "Generate Summary", "Generate Questions"]
    )
    
    if action == "Generate Summary":
        st.header("Document Summary")
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                # For simplicity, using the first document if multiple are uploaded
                # In a real app, you'd let the user select which document to summarize
                document_ids = st.session_state.get("document_ids", [])
                if document_ids:
                    summary = rag_pipeline.generate_summary(document_ids[0])
                    if summary:
                        st.markdown(summary)
                    else:
                        st.warning("Could not generate a summary for the document.")
                else:
                    st.warning("Please upload a document first.")
    
    elif action == "Generate Questions":
        st.header("Generate Practice Questions")
        num_questions = st.slider("Number of questions to generate:", 1, 10, 5)
        
        if st.button("Generate Questions"):
            with st.spinner("Generating questions..."):
                document_ids = st.session_state.get("document_ids", [])
                if document_ids:
                    questions = rag_pipeline.generate_questions(document_ids[0], num_questions)
                    if questions:
                        for i, q in enumerate(questions, 1):
                            with st.expander(f"Question {i}"):
                                st.write(q["question"])
                                for opt, text in q["options"].items():
                                    st.write(f"{opt.upper()}. {text}")
                                st.markdown(f"**Answer: {q['answer'].upper()}**")
                    else:
                        st.warning("Could not generate questions for the document.")
                else:
                    st.warning("Please upload a document first.")

def main():
    """Main application function."""
    setup_page()
    
    # Initialize session state for document tracking
    if "document_ids" not in st.session_state:
        st.session_state.document_ids = []
    
    # Handle file uploads and URL processing
    file_doc_ids = handle_file_upload()
    url_doc_ids = handle_url_input()
    
    # Update session state with new document IDs
    new_doc_ids = file_doc_ids + url_doc_ids
    if new_doc_ids:
        st.session_state.document_ids = list(set(st.session_state.document_ids + new_doc_ids))
    
    # Display document actions in sidebar
    display_document_actions()
    
    # Main content area
    if not st.session_state.document_ids:
        st.info("👈 Please upload documents or enter a URL to get started.")
    else:
        display_qa_interface()
    
    # Display document info in sidebar
    if st.session_state.document_ids:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Processed Documents")
        for doc_id in st.session_state.document_ids[:5]:  # Show first 5
            st.sidebar.text(doc_id[:8] + "..." + doc_id[-4:])
        
        if len(st.session_state.document_ids) > 5:
            st.sidebar.text(f"...and {len(st.session_state.document_ids) - 5} more")
        
        if st.sidebar.button("Clear Documents"):
            st.session_state.document_ids = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()
