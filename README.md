# AI-Powered ESG Intelligence Hub

A sophisticated Retrieval-Augmented Generation (RAG) system for analyzing ESG (Environmental, Social, and Governance) reports with real-time web search capabilities.

## Overview

This application combines local document analysis with live web search to provide comprehensive ESG insights. Built with Streamlit, LangChain, and Groq's LLM infrastructure.

## Features

- **Hybrid RAG System**: Pre-loaded knowledge base + custom document uploads
- **Real-Time Web Search**: Automatic fallback to live data when needed
- **Groq-Powered LLM**: Fast inference using Llama 3.1 8B Instant
- **Dual Response Modes**: Concise summaries or detailed analysis
- **Multi-Document Analysis**: Compare ESG metrics across companies
- **Source Attribution**: Transparent citation of information sources

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                      (Streamlit App)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Query Processing Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   RAG Path   │  │  Web Search  │  │  Response Generator  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │ 
└─────────┼──────────────────┼──────────────────────┼─────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────────────┐
│  Vector Store   │  │  Tavily API  │  │   Groq LLM API       │
│   (FAISS)       │  │ (Web Search) │  │ (Llama 3.1 8B)       │
└────────┬────────┘  └──────────────┘  └──────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Base                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Microsoft    │  │    Apple     │  │      Google          │   │
│  │ ESG Report   │  │  ESG Report  │  │    ESG Report        │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │ 
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           User-Uploaded Documents (PDF)                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## System Flow

```
User Query
    │
    ▼
┌───────────────────────┐
│  Query Analysis       │
│  - Intent detection   │
│  - Mode selection     │
└───────┬───────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  RAG Retrieval                        │
│  1. Embed query                       │
│  2. Search vector store               │
│  3. Retrieve relevant chunks          │
└───────┬───────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  Context Evaluation                   │
│  - Check context quality              │
│  - Detect "latest/news" keywords      │
└───────┬───────────────────────────────┘
        │
        ├─── Sufficient Context ──────┐
        │                             │
        └─── Weak/Missing Context     │
                    │                 │
                    ▼                 │
        ┌───────────────────────┐     │
        │  Web Search           │     │
        │  - Query Tavily API   │     │
        │  - Fetch live results │     │
        └───────┬───────────────┘     │
                │                     │
                └──────┬──────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  LLM Response Generation     │
        │  - Combine all context       │
        │  - Apply mode (concise/full) │
        │  - Generate answer           │
        │  - Add source citations      │
        └──────────┬───────────────────┘
               │
               ▼
        Display to User
```

## Project Structure

```
AI_UseCase/
├── app.py                      # Main Streamlit application
├── config/
│   └── config.py              # Configuration and API keys
├── models/
│   ├── embeddings.py          # Embedding model setup
│   └── llm.py                 # LLM initialization
├── utils/
│   ├── rag_utils.py           # RAG pipeline utilities
│   └── search_utils.py        # Web search integration
├── data/
│   ├── Apple-2024-ESG.pdf
│   ├── Google-2024-ESG.pdf
│   └── Microsoft-2024-ESG.pdf
├── requirements.txt           # Python dependencies
├── sample_questions.md        # Example queries
├── .env                       # API keys (not in git)
└── .gitignore                # Git ignore rules
```

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/gajulaakanksha/ESG_intelligence_hub.git
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API keys**

Create a `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional for web search
```

Get your API keys:
- Groq: https://console.groq.com/
- Tavily: https://tavily.com/

4. **Run the application**
```bash
streamlit run app.py
```

## Application Demo

!https://github.com/gajulaakanksha/ESG_intelligence_hub/blob/main/images/Screenshot_4.png

## Usage

### Basic Query
1. Navigate to the Chat page
2. Ask a question like: "Compare Microsoft and Apple's carbon goals"
3. View the response with source citations

### Upload Custom Documents
1. Use the sidebar file uploader
2. Select a PDF ESG/CSR report
3. Click "Index Document"
4. Query the newly added content

### Response Modes
- **Concise**: Quick facts and summaries
- **Detailed**: In-depth analysis with context

### Web Search Trigger
Include keywords like "latest", "news", or "recent" to automatically fetch live data.

## Technical Details

### Components

**1. Document Processing**
- PDF parsing with PyPDF2/LangChain
- Text chunking for optimal retrieval
- Metadata preservation for source tracking

**2. Embeddings**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Local inference (no API calls)
- 384-dimensional vectors

**3. Vector Store**
- FAISS for similarity search
- In-memory storage
- Fast retrieval (<100ms)

**4. LLM**
- Model: `llama-3.1-8b-instant`
- Provider: Groq
- Average latency: 200-500ms

**5. Web Search**
- Provider: Tavily API
- Fallback mechanism
- Real-time data integration

### Configuration Options

Edit `config/config.py` to customize:
- LLM model selection
- Embedding model
- System prompts
- File paths

## Performance

- **Initial Load**: 5-15 seconds (vector store creation)
- **Query Response**: 1-3 seconds (RAG only)
- **With Web Search**: 3-5 seconds
- **Document Upload**: 2-5 seconds per PDF

## Limitations

- PDF-only document support
- English language optimized
- Requires internet for LLM and web search
- Vector store recreated on restart (not persisted)

## Future Enhancements

- Persistent vector store (ChromaDB/Pinecone)
- Multi-language support
- Excel/CSV data integration
- Advanced analytics dashboard
- Conversation memory across sessions
- Export reports to PDF

## Troubleshooting

**App won't start:**
- Check API keys in `.env`
- Verify all dependencies installed
- Ensure PDFs exist in `data/` folder

**Slow responses:**
- Switch to faster model (llama-3.1-8b-instant)
- Reduce document size
- Check internet connection

**No results from RAG:**
- Verify vector store initialized
- Check document content relevance
- Try rephrasing query

## License

MIT License

