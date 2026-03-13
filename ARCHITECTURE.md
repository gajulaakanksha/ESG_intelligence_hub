# System Architecture Documentation

## High-Level Architecture

The ESG Intelligence Hub follows a modular, layered architecture designed for scalability and maintainability.

## Architecture Layers

### 1. Presentation Layer
**Component**: Streamlit Web Interface (`app.py`)

**Responsibilities**:
- User interaction and input handling
- Response rendering and visualization
- Session state management
- File upload interface
- Navigation and routing

**Key Features**:
- Dark theme with custom CSS
- Real-time chat interface
- Sidebar controls for settings
- Multi-page navigation (Chat, About)

### 2. Application Layer
**Components**: 
- `utils/rag_utils.py` - RAG pipeline orchestration
- `utils/search_utils.py` - Web search integration

**Responsibilities**:
- Query processing and routing
- Context aggregation
- Response mode handling
- Source attribution

**Flow**:
```
User Query → RAG Retrieval → Context Evaluation → 
  ├─ Sufficient? → LLM Generation
  └─ Insufficient? → Web Search → LLM Generation
```

### 3. Model Layer
**Components**:
- `models/llm.py` - Language model interface
- `models/embeddings.py` - Embedding model setup

**Responsibilities**:
- LLM API communication (Groq)
- Embedding generation (local)
- Model configuration management
- Error handling and retries

### 4. Data Layer
**Components**:
- Vector Store (FAISS)
- Document Storage (`data/`)
- Configuration (`config/config.py`)

**Responsibilities**:
- Document persistence
- Vector indexing and retrieval
- Configuration management
- API key handling

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Streamlit UI  │
                    │   (app.py)     │
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
    ┌───────────────────┐     ┌──────────────────┐
    │  Document Upload  │     │   Chat Query     │
    └─────────┬─────────┘     └────────┬─────────┘
              │                        │
              ▼                        ▼
    ┌──────────────────┐     ┌─────────────────────┐
    │  PDF Processing  │     │  Query Processing   │
    │  - Parse PDF     │     │  - Intent detection │
    │  - Chunk text    │     │  - Mode selection   │
    │  - Generate IDs  │     └──────────┬──────────┘
    └─────────┬────────┘                │
              │                         ▼
              │              ┌────────────────────────┐
              │              │   Embedding Service    │
              │              │  (all-MiniLM-L6-v2)    │
              │              └──────────┬─────────────┘
              │                         │
              ▼                         ▼
    ┌──────────────────────────────────────────┐
    │         Vector Store (FAISS)              │
    │  - Store embeddings                       │
    │  - Similarity search                      │
    │  - Return top-k documents                 │
    └──────────────────┬───────────────────────┘
                       │
                       ▼
            ┌────────────────────┐
            │  Context Builder   │
            │  - Aggregate docs  │
            │  - Check quality   │
            └─────────┬──────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
┌─────────────────┐      ┌──────────────────┐
│  Sufficient     │      │  Insufficient    │
│  Context        │      │  Context         │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         │                        ▼
         │              ┌──────────────────┐
         │              │   Web Search     │
         │              │  (Tavily API)    │
         │              └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
          ┌────────────────────┐
          │   Context Merger   │
          │  - Combine sources │
          │  - Format context  │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │   LLM Generation   │
          │  (Groq/Llama 3.1)  │
          │  - Apply mode      │
          │  - Generate answer │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │  Response Builder  │
          │  - Add citations   │
          │  - Format output   │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │   Display Result   │
          └────────────────────┘
```

## Component Interactions

### RAG Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                      RAG PIPELINE                            │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │  Query   │───▶│  Embed   │───▶│  Search  │             │
│  └──────────┘    └──────────┘    └────┬─────┘             │
│                                        │                    │
│                                        ▼                    │
│                              ┌──────────────────┐          │
│                              │  Vector Store    │          │
│                              │  (FAISS Index)   │          │
│                              └────────┬─────────┘          │
│                                       │                    │
│                                       ▼                    │
│                              ┌──────────────────┐          │
│                              │  Top-K Docs      │          │
│                              │  (k=4 default)   │          │
│                              └────────┬─────────┘          │
│                                       │                    │
│                                       ▼                    │
│                              ┌──────────────────┐          │
│                              │  Rerank/Filter   │          │
│                              └────────┬─────────┘          │
│                                       │                    │
│                                       ▼                    │
│                              ┌──────────────────┐          │
│                              │  Context String  │          │
│                              └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Web Search Integration

```
┌─────────────────────────────────────────────────────────────┐
│                   WEB SEARCH FLOW                            │
│                                                              │
│  Trigger Conditions:                                         │
│  ├─ Keywords: "latest", "news", "recent"                    │
│  ├─ Weak RAG context (< 100 chars)                          │
│  └─ No RAG results                                           │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │  Query   │───▶│  Tavily  │───▶│  Parse   │             │
│  │  Format  │    │   API    │    │ Results  │             │
│  └──────────┘    └──────────┘    └────┬─────┘             │
│                                        │                    │
│                                        ▼                    │
│                              ┌──────────────────┐          │
│                              │  Extract:        │          │
│                              │  - Title         │          │
│                              │  - Snippet       │          │
│                              │  - URL           │          │
│                              │  - Date          │          │
│                              └────────┬─────────┘          │
│                                       │                    │
│                                       ▼                    │
│                              ┌──────────────────┐          │
│                              │  Format Context  │          │
│                              └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Streamlit**: Web framework
- **Custom CSS**: UI styling

### Backend
- **Python 3.11+**: Core language
- **LangChain**: LLM orchestration
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Local embeddings

### External Services
- **Groq API**: LLM inference
- **Tavily API**: Web search

### Data Processing
- **PyPDF2/LangChain**: PDF parsing
- **NumPy**: Vector operations

## Security Considerations

### API Key Management
- Environment variables via `.env`
- No hardcoded credentials
- `.gitignore` protection

### Data Privacy
- Local embedding generation
- No document data sent to embedding API
- Session-based storage (no persistence)

### Input Validation
- File type restrictions (PDF only)
- Query sanitization
- Error handling for malformed inputs

## Scalability Considerations

### Current Limitations
- In-memory vector store (RAM-bound)
- Single-user session state
- No caching layer
- Synchronous processing

### Scaling Strategies

**Horizontal Scaling**:
- Deploy multiple Streamlit instances
- Load balancer for distribution
- Shared vector store (Redis/Pinecone)

**Vertical Scaling**:
- Increase RAM for larger vector stores
- GPU acceleration for embeddings
- Faster storage (SSD/NVMe)

**Optimization**:
- Implement vector store persistence
- Add response caching (Redis)
- Batch embedding generation
- Async LLM calls

## Monitoring & Observability

### Logging
- Application logs via Python `logging`
- Streamlit debug mode
- Error tracking

### Metrics to Track
- Query latency
- RAG retrieval accuracy
- LLM token usage
- Web search frequency
- User session duration

### Recommended Tools
- **Logging**: Loguru, structlog
- **Monitoring**: Prometheus + Grafana
- **Tracing**: LangSmith, OpenTelemetry
- **Error Tracking**: Sentry

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTION DEPLOYMENT                    │
│                                                              │
│  ┌──────────────┐                                           │
│  │   Users      │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │ Load Balancer│                                           │
│  │  (Nginx)     │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│    ┌────┴────┐                                              │
│    │         │                                              │
│    ▼         ▼                                              │
│  ┌────┐   ┌────┐                                           │
│  │App1│   │App2│  Streamlit Instances                      │
│  └─┬──┘   └─┬──┘                                           │
│    │        │                                               │
│    └────┬───┘                                               │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │ Vector Store │                                           │
│  │  (Pinecone/  │                                           │
│  │   Weaviate)  │                                           │
│  └──────────────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐     ┌──────────────┐                     │
│  │  Groq API    │     │  Tavily API  │                     │
│  └──────────────┘     └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling Strategy

### Graceful Degradation
1. **LLM Failure**: Show cached response or error message
2. **Vector Store Failure**: Fall back to web search only
3. **Web Search Failure**: Use RAG results only
4. **Embedding Failure**: Retry with exponential backoff

### User Feedback
- Clear error messages
- Suggested actions
- Retry mechanisms
- Status indicators

## Future Architecture Enhancements

1. **Microservices**: Separate RAG, search, and LLM services
2. **Message Queue**: Async processing with Celery/RabbitMQ
3. **Caching Layer**: Redis for responses and embeddings
4. **Database**: PostgreSQL for user data and analytics
5. **API Gateway**: RESTful API for programmatic access
6. **Container Orchestration**: Kubernetes deployment
7. **CI/CD Pipeline**: Automated testing and deployment
