import sqlite3

conn = sqlite3.connect("chat_history.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)
""")

conn.commit()


# SAVE CHAT (NO DUPLICATES)

def save_chat(question, answer):

    chats = load_chats()

    # Remove extra spaces + lowercase
    normalized_question = question.strip().lower()

    # Check last 5 questions
    for item in chats[-5:]:

        old_question = item["question"].strip().lower()

        # Skip if same question already exists
        if old_question == normalized_question:
            return

    # Save only if unique
    chats.append({
        "question": question,
        "answer": answer
    })

    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=4)

def load_chats():
    cursor.execute(
        "SELECT question, answer FROM chats ORDER BY id DESC LIMIT 5"
    )
    return cursor.fetchall()