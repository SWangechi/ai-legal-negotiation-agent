import os
import sqlite3
import uuid
import base64
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.memory_manager import upsert_documents, query_similar
from backend.pdf_utils import build_pdf_bytes

DB_DIR = Path(__file__).resolve().parents[1] / "database"
DB_DIR.mkdir(exist_ok=True, parents=True)

ANALYSIS_DB = DB_DIR / "analyses.db"
FEEDBACK_DB = DB_DIR / "feedback.db"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def init_analyses_db():
    conn = sqlite3.connect(ANALYSIS_DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        title TEXT,
        timestamp TEXT,
        payload TEXT,
        summary TEXT
    )""")
    conn.commit()
    conn.close()

def init_feedback_db():
    conn = sqlite3.connect(FEEDBACK_DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        rating INTEGER,
        comments TEXT,
        timestamp TEXT
    )""")
    conn.commit()
    conn.close()

init_analyses_db()
init_feedback_db()

class AnalyzeInput(BaseModel):
    text: str
    title: str = "Untitled"

class HistoryList(BaseModel):
    pass

@app.post("/analyze")
def analyze_endpoint(input: AnalyzeInput):
    res = analyze_text_with_llm(input.text)
    aid = str(uuid.uuid4())
    import datetime
    ts = datetime.datetime.utcnow().isoformat()
    summary = " ".join([ (c.get("analysis") or "")[:300] for c in res.get("clauses", []) ])
    conn = sqlite3.connect(ANALYSIS_DB)
    c = conn.cursor()
    c.execute("INSERT INTO analyses (id,title,timestamp,payload,summary) VALUES (?,?,?,?,?)",
              (aid, input.title, ts, json.dumps(res), summary))
    conn.commit()
    conn.close()
    docs = [{"id": f"{aid}_{i}", "text": (c.get("clause") or c.get("text") or ""), "meta": {"analysis_id": aid}} for i,c in enumerate(res.get("clauses", []))]
    if docs:
        upsert_documents(docs)
    res["id"] = aid
    return res

@app.get("/history")
def history_list():
    conn = sqlite3.connect(ANALYSIS_DB)
    c = conn.cursor()
    c.execute("SELECT id,title,timestamp,summary FROM analyses ORDER BY timestamp DESC LIMIT 200")
    rows = c.fetchall()
    conn.close()
    items = [{"id": r[0],"title": r[1],"timestamp": r[2],"summary": r[3]} for r in rows]
    return {"history": items}

@app.get("/history/{aid}")
def history_get(aid: str):
    conn = sqlite3.connect(ANALYSIS_DB)
    c = conn.cursor()
    c.execute("SELECT payload FROM analyses WHERE id=?", (aid,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return json.loads(row[0])

@app.post("/export_pdf")
def export_pdf(data: dict):
    aid = data.get("analysis_id")
    if not aid:
        raise HTTPException(status_code=400, detail="analysis_id required")
    conn = sqlite3.connect(ANALYSIS_DB)
    c = conn.cursor()
    c.execute("SELECT payload,title,timestamp FROM analyses WHERE id=?", (aid,))
    row = c.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Not found")
    payload = json.loads(row[0])
    title = row[1]
    ts = row[2]
    pdf_bytes = build_pdf_bytes(title, ts, payload)  # returns bytes
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    return {"pdf_base64": b64}

@app.post("/negotiate")
def negotiate(data: dict):
    clause = data.get("clause","")
    position = data.get("position","")
    out = analyze_text_with_llm(clause, mode="negotiate", extra={"position": position})
    return out

@app.post("/negotiate_chat")
def negotiate_chat(data: dict):
    history = data.get("history", [])
    out = analyze_text_with_llm("\n".join([f"{m['role']}: {m['text']}" for m in history]), mode="negotiation_chat", extra={"parties": data.get("parties", [])})
    return {"suggestion": out.get("suggestion", out)}

@app.post("/mediate")
def mediate(data: dict):
    a = data.get("a","")
    b = data.get("b","")
    ctx = data.get("context","")
    out = analyze_text_with_llm(f"Party A: {a}\n\nParty B: {b}\n\nContext: {ctx}", mode="mediate")
    return out

@app.post("/feedback")
def feedback(data: dict):
    import datetime
    conn = sqlite3.connect(FEEDBACK_DB)
    c = conn.cursor()
    ts = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT INTO feedback (username,rating,comments,timestamp) VALUES (?,?,?,?)",
              (data.get("username","Anonymous"), int(data.get("rating",0)), data.get("comments",""), ts))
    conn.commit()
    conn.close()
    return {"message":"ok"}
