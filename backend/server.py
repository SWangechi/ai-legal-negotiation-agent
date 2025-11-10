from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

if __name__ == "__main__":
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, reload=True)
