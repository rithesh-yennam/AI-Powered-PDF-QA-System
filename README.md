📄 AI-Powered PDF Question Answering System using RAG
<p align="center"> <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python"> <img src="https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi"> <img src="https://img.shields.io/badge/Streamlit-Frontend-red?logo=streamlit"> <img src="https://img.shields.io/badge/LangChain-RAG-blueviolet"> <img src="https://img.shields.io/badge/FAISS-VectorDB-orange"> <img src="https://img.shields.io/badge/Groq-LLM-black"> <img src="https://img.shields.io/badge/License-MIT-green"> </p>
An AI-powered document assistant that allows users to upload PDF files and ask questions in natural language. The system uses Retrieval-Augmented Generation (RAG) architecture to retrieve relevant information from documents and generate context-aware answers using Large Language Models (LLMs).

🧠 What is RAG?
Retrieval-Augmented Generation (RAG) is an AI architecture that combines:

Retrieval → Finds relevant information from documents
Generation → Uses an LLM to generate accurate answers based on retrieved content
This approach improves answer accuracy and reduces hallucinations by ensuring the model responds only from document context.

🚀 Features
| Feature | Description | | ---------------------------- | --------------------------------------------------------- | | 📤 PDF Upload | Upload and process PDF documents instantly | | 🔍 Semantic Search | Retrieves relevant content using vector similarity search | | 🤖 AI-Powered Answers | Generates context-aware responses using Groq LLM | | 💬 Conversational Memory | Maintains recent chat history for multi-turn interactions | | ⚡ Performance Metrics | Displays retrieval and response timings | | 🛡️ Hallucination Protection | Restricts answers strictly to document content | | 🔁 Duplicate Detection | Avoids storing repeated questions | | 📚 Vector Retrieval | Uses FAISS for efficient semantic search |

🛠️ Tech Stack
| Technology | Purpose | | ---------------------- | ------------------------------- | | Python 3.11 | Core programming language | | FastAPI | Backend REST API | | Streamlit | Frontend user interface | | LangChain | RAG pipeline orchestration | | FAISS | Local vector database | | HuggingFace Embeddings | Text-to-vector conversion | | Groq API | LLM inference | | SQLite | Chat history storage | | python-dotenv | Environment variable management |

📂 Project Structure
RAG/
│
├── app.py                  # FastAPI backend
├── streamlit_app.py        # Streamlit frontend
├── requirements.txt        # Dependencies
├── .env                    # API keys
├── .gitignore
├── faiss_index/            # Vector database
└── chat_history.db         # SQLite database
⚙️ Installation & Setup
Step 1 — Clone Repository
git clone https://github.com/rithesh-yennam/AI-Powered-PDF-QA-System.git
cd AI-Powered-PDF-QA-System
Step 2 — Create Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
Linux / Mac
python3 -m venv venv
source venv/bin/activate
Step 3 — Install Dependencies
pip install -r requirements.txt
Step 4 — Add Groq API Key
Create a .env file in the root directory:

GROQ_API_KEY=your_actual_api_key
Get your API key from:

https://console.groq.com

Step 5 — Run Backend
uvicorn app:api --reload
Step 6 — Run Frontend
streamlit run streamlit_app.py
🌐 Application Access
| Interface | URL | | -------------------- | -------------------------- | | Streamlit UI | http://localhost:8501 | | FastAPI Swagger Docs | http://127.0.0.1:8000/docs |

📤 How to Use
Open the Streamlit application
Upload a PDF document
Ask questions related to the uploaded PDF
The system retrieves relevant chunks and generates answers
🔌 API Endpoints
Upload PDF
POST /upload
Processes uploaded PDF documents and stores embeddings in FAISS.

Ask Questions
POST /query
Request
{
  "question": "What are the candidate's technical skills?"
}
Response
{
  "question": "What are the candidate's technical skills?",
  "answer": "The candidate has skills in Python, SQL, Pandas...",
  "retrieval_time_sec": 0.02,
  "llm_response_time_sec": 1.71,
  "duplicate_question": false
}
🔍 RAG Pipeline Workflow
PDF Upload
    ↓
Text Extraction
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
FAISS Vector Storage
    ↓
User Question
    ↓
Semantic Retrieval
    ↓
Relevant Context Selection
    ↓
LLM Response Generation
    ↓
Answer Display
🧩 Core Components
PDF Processing
Extracts text content from uploaded PDF documents.

Text Chunking
Splits large documents into smaller overlapping chunks for better retrieval accuracy.

Embeddings
Converts text into numerical vector representations for semantic similarity search.

Vector Database
FAISS stores embeddings and retrieves semantically relevant chunks efficiently.

Retrieval-Augmented Generation
Combines semantic retrieval with LLM generation for accurate responses.

🛡️ Hallucination Prevention
The system is designed to:

Answer strictly from uploaded PDF content
Avoid external knowledge usage
Return fallback responses when information is unavailable
Example fallback:

Information not found in PDF.
💾 Database Schema
CREATE TABLE chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)
The last 5 conversations are used as contextual memory.

⚡ Performance Optimization
FAISS enables fast local vector retrieval
Lightweight embedding models improve speed
Dynamic chunk filtering reduces irrelevant context
Duplicate detection minimizes redundant operations
📚 Example Use Cases
Resume Question Answering
Research Paper Analysis
AI Document Assistant
Knowledge Base Search
Academic PDF Analysis
Enterprise Document Retrieval
🔮 Future Enhancements
Multi-PDF support
OCR support for scanned PDFs
Cloud deployment
User authentication
Persistent vector storage
Multi-user chat sessions
👨‍💻 Developed By
Rithesh Yennam
B.Tech – Computer Science Engineering (AI & ML)

📧 Email: riteshyennam@gmail.com

📄 License
This project is licensed under the MIT License.