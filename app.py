import streamlit as st
import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logger.info("Starting ESG Intelligence Assistant...")

from models.llm import get_chatgroq_model
from config.config import APP_TITLE, SYSTEM_PROMPT
from utils.rag_utils import load_documents, process_uploaded_file, create_vector_store, get_retriever_response
from utils.search_utils import perform_web_search

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #4CAF50;
        background-color: transparent;
        color: white;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4CAF50;
        color: black;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7d32, #1b5e20);
    }
    .stChatMessage {
        border-radius: 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

def get_chat_response(chat_model, messages, mode="Detailed", context=""):
    """Get response from the chat model with mode-specific prompting"""
    try:
        if not chat_model:
            return "Chat model not initialized. Please check API key or dependencies."

        # Base system prompt adjusted for mode
        mode_instruction = "Provide a brief, direct, and summarized answer." if mode == "Concise" else "Provide a detailed, comprehensive, and in-depth analysis."

        full_system_prompt = f"{SYSTEM_PROMPT}\n\nMODE: {mode_instruction}\n\nCONTEXT FROM DOCUMENTS:\n{context}"

        formatted_messages = [
            {"role": "system", "content": full_system_prompt}
        ]

        # Add conversation history
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        # Groq client returns the generated response text
        response_text = chat_model.invoke(formatted_messages)
        return response_text

    except Exception as e:
        return f"Error getting response: {str(e)}"

def initialize_kb():
    """Initializes the vector store with local documents"""
    if "vector_store" not in st.session_state:
        logger.info("Initializing Knowledge Base...")
        with st.spinner("Initializing ESG Knowledge Base..."):
            logger.info("Loading documents from data/ folder...")
            docs = load_documents()
            if docs:
                logger.info(f"Loaded {len(docs)} document pages")
                logger.info("Creating vector store (this may take a moment)...")
                st.session_state.vector_store = create_vector_store(docs)
                logger.info("Vector store created successfully")
                st.success(f"Knowledge Base Loaded ({len(docs)} pages)")
            else:
                logger.warning("No documents found in data/ folder")
                st.session_state.vector_store = None
                st.warning("No local documents found in 'data/' folder.")

def instructions_page():
    """Instructions and setup page"""
    st.title(f"ℹ️ About {APP_TITLE}")
    
    st.markdown(f"""
    ## 🎯 Purpose
    The **{APP_TITLE}** is a sophisticated tool designed for ESG Analysts and Sustainability Professionals. 
    It bridges the gap between static corporate reports and real-time global events.
    
    ## 🛠️ Features
    1. **Hybrid RAG**: Combines a pre-loaded knowledge base of major ESG reports (Microsoft, Apple, Google) with your own uploaded documents.
    2. **Live Web Search**: Automatically fetches real-time news and regulations if local knowledge is insufficient.
    3. **Groq Acceleration**: Powered by Llama 3.1 70B on Groq for near-instant responses.
    4. **Response Modes**: Switch between 'Concise' for quick facts and 'Detailed' for deep analysis.
    
    ## 🚀 How to Start
    1. Ensure your `GROQ_API_KEY` is set in `config/config.py` or as an environment variable.
    2. Go to the **Chat** page.
    3. Ask a question like *"Compare the water stewardship goals of Microsoft and Google"* or *"What are the latest ISSB disclosure rules?"*
    """)

def chat_page():
    """Main chat interface page"""
    st.title(f"🌍 {APP_TITLE}")
    
    # Initialize KB on first load
    initialize_kb()
    
    # Sidebar features
    with st.sidebar:
        st.header("⚙️ Intelligence Settings")
        
        # Response Mode
        resp_mode = st.radio("Response Mode:", ["Detailed", "Concise"], index=0)
        
        st.divider()
        
        # File Upload
        st.header("📄 Add to Knowledge Base")
        uploaded_file = st.file_uploader("Upload ESG/CSR Report (PDF)", type="pdf")
        if uploaded_file and st.button("Index Document"):
            with st.spinner(f"Indexing {uploaded_file.name}..."):
                new_docs = process_uploaded_file(uploaded_file)
                if new_docs:
                    if st.session_state.vector_store:
                        # Add to existing (Note: For simplicity in this demo, recreating. 
                        # In production, use .add_documents)
                        all_docs = load_documents() + new_docs
                        st.session_state.vector_store = create_vector_store(all_docs)
                    else:
                        st.session_state.vector_store = create_vector_store(new_docs)
                    st.success(f"Successfully added {uploaded_file.name}")
        
        st.divider()
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Chat model
    logger.info("Initializing Groq chat model...")
    chat_model = get_chatgroq_model()
    
    if not chat_model:
        logger.error("Failed to initialize Groq model")
        st.warning(
            "⚠️ Unable to initialize Groq model. "
            "Please ensure your `GROQ_API_KEY` is set and all dependencies (e.g., PyTorch / langchain-groq) are installed correctly."
        )
        return

    # Initialize messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask an ESG question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Analyzing ESG Data..."):
                # 1. Try RAG first
                context = ""
                sources = []
                if st.session_state.vector_store:
                    rag_result = get_retriever_response(st.session_state.vector_store, chat_model, prompt)
                    if rag_result:
                        context = rag_result["result"]
                        sources = [doc.metadata.get('source', 'Unknown') for doc in rag_result.get('source_documents', [])]
                
                # 2. If RAG context is weak or user asks for "news/latest", try Web Search
                if "latest" in prompt.lower() or "news" in prompt.lower() or not context or len(context) < 100:
                    with st.status("Searching live web for latest info...", expanded=False):
                        search_results = perform_web_search(prompt)
                        context += f"\n\nLATEST WEB SEARCH RESULTS:\n{search_results}"
                
                # 3. Generate final response
                response = get_chat_response(chat_model, st.session_state.messages, mode=resp_mode, context=context)
                
                # Append sources if available
                if sources:
                    unique_sources = list(set([os.path.basename(s) for s in sources]))
                    response += f"\n\n**Sources Analyzed:** {', '.join(unique_sources)}"
                
                response_placeholder.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🌍",
        layout="wide"
    )
    
    # Navigation
    with st.sidebar:
        st.title("🛡️ ESG Nav")
        page = st.radio("Go to:", ["Chat", "About"], index=0)
        st.divider()

    if page == "About":
        instructions_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()