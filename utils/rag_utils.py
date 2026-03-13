import os
import sys

# Add parent directory to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import PyPDF2 for PDF loading
import PyPDF2
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from config.config import KNOWLEDGE_BASE_DIR, VECTOR_STORE_PATH
from models.embeddings import get_embedding_model

# Simple text splitter
class SimpleTextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_documents(self, documents):
        texts = []
        for doc in documents:
            content = doc.page_content
            metadata = doc.metadata
            
            # Split by chunk_size with overlap
            for i in range(0, len(content), self.chunk_size - self.chunk_overlap):
                chunk = content[i:i + self.chunk_size]
                if chunk.strip():
                    texts.append(Document(page_content=chunk, metadata=metadata))
        return texts

def load_documents(directory_path=KNOWLEDGE_BASE_DIR):
    """Load PDF documents from the specified directory using PyPDF2"""
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            return []
        
        documents = []
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                filepath = os.path.join(directory_path, filename)
                try:
                    with open(filepath, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page_num, page in enumerate(pdf_reader.pages):
                            text = page.extract_text()
                            if text.strip():
                                doc = Document(
                                    page_content=text,
                                    metadata={"source": filepath, "page": page_num}
                                )
                                documents.append(doc)
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
        return documents
    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        return []

def process_uploaded_file(uploaded_file):
    """Process a single uploaded PDF file and return documents using PyPDF2"""
    try:
        # Read the uploaded file directly
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        documents = []
        
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if text.strip():
                doc = Document(
                    page_content=text,
                    metadata={"source": uploaded_file.name, "page": page_num}
                )
                documents.append(doc)
        
        return documents
    except Exception as e:
        print(f"Error processing uploaded file: {str(e)}")
        return []

def create_vector_store(documents):
    """Create a FAISS vector store from documents"""
    try:
        if not documents:
            return None
            
        text_splitter = SimpleTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        texts = text_splitter.split_documents(documents)
        
        embeddings = get_embedding_model()
        if not embeddings:
            return None
            
        vector_store = FAISS.from_documents(texts, embeddings)
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None

def get_retriever_response(vector_store, chat_model, query):
    """Get response from the RAG chain using latest langchain API"""
    try:
        if not vector_store or not chat_model:
            return None
        
        # Get retriever
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        # Retrieve relevant documents
        docs = retriever.invoke(query)
        
        if not docs:
            return None
        
        # Format context from documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create messages for the chat model
        messages = [
            {"role": "system", "content": "You are an expert ESG analyst. Use the provided context to answer questions accurately."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        # Get response from chat model
        response = chat_model.invoke(messages)
        
        # Return in the expected format
        return {
            "result": response,
            "source_documents": docs
        }
    except Exception as e:
        print(f"Error in RAG retrieval: {str(e)}")
        return None
