import os
import time
import tempfile
import sqlite3
import requests
import streamlit as st
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


GROQ_API_KEY = "your key"

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

FAISS_PATH = "faiss_index"


api = FastAPI(
    title="Enterprise PDF RAG Chatbot"
)


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-MiniLM-L3-v2"
)


llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0
)


vectorstore = None

conn = sqlite3.connect(
    "chat_history.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)
""")

conn.commit()


def save_chat(question, answer):

    normalized_question = question.strip().lower()

    cursor.execute("""
        SELECT question
        FROM chats
        ORDER BY id DESC
        LIMIT 1
    """)

    last_row = cursor.fetchone()

    if last_row:

        last_question = last_row[0].strip().lower()

        if last_question == normalized_question:

            print("Duplicate question skipped")

            return False

    cursor.execute("""
        INSERT INTO chats(question, answer)
        VALUES (?, ?)
    """, (question, answer))

    conn.commit()

    return True



def load_chats():

    cursor.execute("""
        SELECT question, answer
        FROM chats
        ORDER BY id DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()

    chats = []

    for row in rows:

        chats.append({
            "question": row[0],
            "answer": row[1]
        })

    return chats


class QueryRequest(BaseModel):

    question: str


def process_pdf(pdf_path):

    global vectorstore

    start = time.time()

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    vectorstore = FAISS.from_documents(
        chunks,
        embedding_model
    )

    vectorstore.save_local(FAISS_PATH)

    end = time.time()

    print(f"PDF Processing Time: {end - start:.2f} sec")


if os.path.exists(FAISS_PATH):

    vectorstore = FAISS.load_local(
        FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True
    )

    print("FAISS loaded successfully")

@api.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:

        tmp.write(await file.read())

        temp_path = tmp.name

    process_pdf(temp_path)

    return {
        "message": "PDF uploaded successfully"
    }


@api.post("/query")
async def query_pdf(request: QueryRequest):

    global vectorstore

    if vectorstore is None:

        return {
            "error": "Upload a PDF first"
        }

    question = request.question.strip()

    corrected_question = question.lower()

    print("Question:", corrected_question)

    summary_questions = [
        "what is this pdf about",
        "what is pdf about",
        "summarize the pdf",
        "summary of pdf",
        "explain this pdf",
        "what was this pdf about"
    ]

    is_summary_query = corrected_question in summary_questions

   
    cursor.execute("""
        SELECT question
        FROM chats
        ORDER BY id DESC
        LIMIT 1
    """)

    last_row = cursor.fetchone()

    is_duplicate = False

    if last_row:

        last_question = last_row[0].strip().lower()

        if last_question == corrected_question:

            is_duplicate = True

    
    retrieval_start = time.time()

    k_value = 6 if is_summary_query else 3

    results = vectorstore.similarity_search_with_score(
        corrected_question,
        k=k_value
    )

    filtered_docs = []

    best_score = results[0][1]

    print("Best Score:", best_score)

    for doc, score in results:

        print("Similarity Score:", score)

        # Dynamic filtering
        if score <= best_score + 0.6:

            filtered_docs.append(doc)

    retrieval_end = time.time()

    retrieval_time = retrieval_end - retrieval_start

    print(f"Retrieval Time: {retrieval_time:.2f} sec")

   
    if len(filtered_docs) == 0:

        return {
            "question": question,
            "normalized_question": corrected_question,
            "answer": "Information not found in PDF.",
            "retrieval_time_sec": round(retrieval_time, 2),
            "duplicate_question": is_duplicate
        }

   
    context = "\n".join([
        doc.page_content
        for doc in filtered_docs
    ])

    context = context[:7000] if is_summary_query else context[:4000]

  
    history = load_chats()

    chat_context = ""

    for item in history:

        chat_context += (
            f"User: {item['question']}\n"
            f"Assistant: {item['answer']}\n"
        )


    final_prompt = f"""
You are an intelligent PDF question-answering assistant.

STRICT RULES:
1. Answer ONLY using the PDF context
2. Do NOT use outside knowledge
3. If answer is unavailable in context, reply exactly:
   "Information not found in PDF."
4. Do NOT hallucinate
5. Give meaningful explanations
6. Keep answers concise but informative
7. Avoid overly long answers
8. Use complete sentences

IMPORTANT:
- Explain concepts clearly using the PDF context
- Keep answers around 80-120 words
- Include only the most relevant details
- Avoid repetition

Previous Conversation:
{chat_context}

PDF Context:
{context}

Question:
{corrected_question}
"""

  
    llm_start = time.time()

    response = llm.invoke(final_prompt)

    llm_end = time.time()

    llm_time = llm_end - llm_start

    print(f"LLM Response Time: {llm_time:.2f} sec")

    answer = response.content.strip()

  
    invalid_responses = [
        "i don't know",
        "not sure",
        "cannot determine",
        "no information"
    ]

    for text in invalid_responses:

        if text in answer.lower():

            answer = "Information not found in PDF."

    if len(answer) < 5:

        answer = "Information not found in PDF."

 
    if not is_duplicate:

        save_chat(question, answer)


    return {
        "question": question,
        "normalized_question": corrected_question,
        "answer": answer,
        "retrieval_time_sec": round(retrieval_time, 2),
        "llm_response_time_sec": round(llm_time, 2),
        "duplicate_question": is_duplicate
    }


def streamlit_ui():

    st.set_page_config(
        page_title="Enterprise PDF RAG Chatbot",
        layout="wide"
    )

    st.title(" Enterprise PDF RAG Chatbot")

   
    if "pdf_uploaded" not in st.session_state:

        st.session_state.pdf_uploaded = False

  
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file and not st.session_state.pdf_uploaded:

        with st.spinner("Processing PDF..."):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    "application/pdf"
                )
            }

            response = requests.post(
                "http://127.0.0.1:8000/upload",
                files=files
            )

            if response.status_code == 200:

                st.session_state.pdf_uploaded = True

                st.success("PDF uploaded successfully")

            else:

                st.error("Upload failed")

    # QUESTION FORM

    with st.form("question_form", clear_on_submit=False):

        question = st.text_input(
            "Ask a question from PDF"
        )

        submit = st.form_submit_button("Ask")

    # QUERY

    if submit:

        if not question.strip():

            st.warning("Enter a question")

        elif not st.session_state.pdf_uploaded:

            st.warning("Upload a PDF first")

        else:

            with st.spinner("Generating answer..."):

                response = requests.post(
                    "http://127.0.0.1:8000/query",
                    json={
                        "question": question
                    }
                )

                result = response.json()

                if "answer" in result:

                    st.subheader(" Answer")

                    st.write(result["answer"])

                    st.info(
                        f"""
Normalized Question: {result.get('normalized_question', '')}

Retrieval Time: {result.get('retrieval_time_sec', 0)} sec

LLM Response Time: {result.get('llm_response_time_sec', 0)} sec
                        """
                    )

                    if result.get("duplicate_question"):

                        st.warning(
                            "Duplicate question detected. SQL insert skipped."
                        )

                else:

                    st.error(result)

    # CHAT HISTORY

    st.subheader(" Chat History")

    history = load_chats()

    for item in reversed(history):

        st.markdown("###  Question")
        st.write(item["question"])

        st.markdown("###  Answer")
        st.write(item["answer"])

# RUN STREAMLIT

if __name__ == "__main__":

    streamlit_ui()