import streamlit as st
import requests

st.set_page_config(page_title="PDF RAG Chatbot", page_icon="📄", layout="centered")

st.title("📄 PDF RAG Chatbot")
st.caption("Upload a PDF and ask questions based on its content.")

st.divider()

# --- PDF UPLOAD ---
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file and not st.session_state.pdf_uploaded:
    with st.spinner("Processing PDF..."):
        response = requests.post(
            "http://127.0.0.1:8000/upload",
            files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        )
    if response.status_code == 200 and "message" in response.json():
        st.session_state.pdf_uploaded = True
        st.success(f"✅ {response.json()['message']}")
    else:
        st.error(f"❌ {response.json().get('error', 'Upload failed')}")

st.divider()

# --- CHAT HISTORY ---
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["question"])
    with st.chat_message("assistant"):
        st.write(chat["answer"])
        st.caption(f"⏱ Retrieval: {chat['retrieval_time_sec']}s | LLM: {chat['llm_response_time_sec']}s")

# --- QUESTION INPUT ---
question = st.chat_input("Ask a question about the PDF...")

if question:
    if not st.session_state.pdf_uploaded:
        st.warning("⚠️ Please upload a PDF first.")
    else:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    "http://127.0.0.1:8000/query",
                    json={"question": question}
                )
                result = response.json()

            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                answer = result.get("answer", "No answer found.")

                if answer == "Information not found in PDF.":
                    st.warning("⚠️ " + answer)
                else:
                    st.write(answer)

                retrieval = result.get("retrieval_time_sec", 0)
                llm = result.get("llm_response_time_sec", 0)
                duplicate = result.get("duplicate_question", False)

                st.caption(f"⏱ Retrieval: {retrieval}s | LLM: {llm}s" + (" | 🔁 Duplicate question" if duplicate else ""))

                if answer != "Information not found in PDF.":
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "retrieval_time_sec": retrieval,
                        "llm_response_time_sec": llm
                    })
