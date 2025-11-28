# import os
# import sqlite3
# import math
# from dotenv import load_dotenv
# from openai import OpenAI

# # Load .env file first
# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# DB_PATH = "vector_memory.db"

# # --- Create SQLite DB if not exists ---
# conn = sqlite3.connect(DB_PATH)
# c = conn.cursor()
# c.execute("""
# CREATE TABLE IF NOT EXISTS memory (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     text TEXT,
#     embedding BLOB
# )
# """)
# conn.commit()
# conn.close()


# def get_embedding(text: str):
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=text
#     )
#     return response.data[0].embedding


# def store_memory(text: str):
#     emb = get_embedding(text)
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute(
#         "INSERT INTO memory (text, embedding) VALUES (?, ?)",
#         (text, bytes(memoryview(bytearray(emb))))
#     )
#     conn.commit()
#     conn.close()


# def cosine_similarity(a, b):
#     dot = sum(x * y for x, y in zip(a, b))
#     mag_a = math.sqrt(sum(x * x for x in a))
#     mag_b = math.sqrt(sum(x * x for x in b))
#     return dot / (mag_a * mag_b + 1e-8)


# def search_memory(query: str, k=4):
#     query_emb = get_embedding(query)

#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT id, text, embedding FROM memory")
#     rows = c.fetchall()
#     conn.close()

#     results = []
#     for row in rows:
#         emb_list = list(row[2])
#         sim = cosine_similarity(query_emb, emb_list)
#         results.append({"id": row[0], "text": row[1], "score": sim})

#     results.sort(key=lambda x: x["score"], reverse=True)
#     return results[:k]
