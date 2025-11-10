from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import datetime
import uvicorn
from backend.negotiation_engine import analyze_contract


app = FastAPI(title="AI Legal Negotiation & Mediation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running"}

class ContractInput(BaseModel):
    text: str

@app.post("/analyze")
async def analyze_contract_endpoint(data: ContractInput, request: Request):
    try:
        result = analyze_contract(data.text)
        return {"clauses": result}
    except Exception as e:
        return {"error": str(e)}
    
class Feedback(BaseModel):
    username: str
    rating: int
    comments: str
    
@app.post("/api/feedback")
def receive_feedback(feedback: Feedback):
    """Receive and store user feedback"""
    conn = sqlite3.connect("database/feedback.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            rating INTEGER,
            comments TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO feedback (username, rating, comments, timestamp) VALUES (?, ?, ?, ?)",
              (feedback.username, feedback.rating, feedback.comments, timestamp))
    conn.commit()
    conn.close()
    return {"message": "Feedback received successfully!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
