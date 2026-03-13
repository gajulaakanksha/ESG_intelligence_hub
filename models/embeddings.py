import os
import sys

# Add parent directory to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import EMBEDDING_MODEL_NAME

# Use a simple embedding model that doesn't require PyTorch
try:
    from sentence_transformers import SentenceTransformer
    from langchain_core.embeddings import Embeddings
    
    class SimpleSentenceTransformerEmbeddings(Embeddings):
        """Simple wrapper for sentence-transformers that avoids langchain-huggingface"""
        
        def __init__(self, model_name):
            self.model = SentenceTransformer(model_name)
        
        def embed_documents(self, texts):
            """Embed a list of documents"""
            return self.model.encode(texts, normalize_embeddings=True).tolist()
        
        def embed_query(self, text):
            """Embed a single query"""
            return self.model.encode([text], normalize_embeddings=True)[0].tolist()
    
    def get_embedding_model():
        """Initialize and return the embedding model using sentence-transformers directly"""
        try:
            embeddings = SimpleSentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
            return embeddings
        except Exception as e:
            print(f"Error initializing embedding model: {str(e)}")
            return None
            
except ImportError as e:
    print(f"Import error: {str(e)}")
    def get_embedding_model():
        return None
