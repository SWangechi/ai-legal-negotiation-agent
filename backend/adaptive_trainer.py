import os
import sqlite3
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from textblob import TextBlob

load_dotenv()
CHROMA_PATH = os.getenv("CHROMA_MEMORY_PATH", "data/memory_store")

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
chroma_client = chromadb.Client(Settings(persist_directory=CHROMA_PATH))
feedback_memory = chroma_client.get_or_create_collection(
    "feedback_memory",
    embedding_function=embedding_fn
)

DB_PATH = "database/feedback.db"
if not os.path.exists(DB_PATH):
    print("❌ No feedback database found. Run your app and submit feedback first.")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        rating INTEGER,
        comments TEXT,
        timestamp TEXT
    )
""")

cursor.execute("SELECT id, username, rating, comments, timestamp FROM feedback")
rows = cursor.fetchall()
conn.close()

if not rows:
    print("⚠️ No feedback data found. Please collect some user feedback first.")
    exit()

def get_sentiment_label(comment: str):
    """Simple sentiment polarity using TextBlob."""
    polarity = TextBlob(comment).sentiment.polarity
    if polarity > 0.2:
        return "positive"
    elif polarity < -0.2:
        return "negative"
    else:
        return "neutral"

docs, metas, ids = [], [], []

for (fid, username, rating, comments, timestamp) in rows:
    sentiment = get_sentiment_label(comments or "")
    docs.append(comments or "")
    metas.append({
        "username": username or "anonymous",
        "rating": rating,
        "sentiment": sentiment,
        "timestamp": timestamp
    })
    ids.append(str(fid))

feedback_memory.upsert(documents=docs, metadatas=metas, ids=ids)

print(f"✅ Inserted {len(docs)} feedback items into ChromaDB memory.")
print("📦 Adaptive feedback memory successfully updated.")
