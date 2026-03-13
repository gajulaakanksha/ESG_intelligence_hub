import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Model Configurations
# Use a Groq-hosted open-source Llama 3 model for inference.
# You can change this to any supported model listed at https://groq.com/docs/models
GROQ_MODEL_NAME = "llama-3.1-8b-instant"  # Fast and efficient Llama 3.1 model on Groq

# Embeddings are produced locally using sentence-transformers + FAISS.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight local embedding model

# Path Configurations
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
VECTOR_STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vectorstore")

# App Settings
APP_TITLE = "AI-Powered ESG Intelligence Hub"
SYSTEM_PROMPT = """You are an expert ESG (Environmental, Social, and Governance) Analyst. 
Your goal is to help users analyze sustainability reports, track regulatory changes, and identify corporate red flags.
Use the provided context from documents and web search results to provide accurate, data-driven insights.
Always cite your sources (e.g., 'According to Microsoft 2024 ESG Report...')."""
