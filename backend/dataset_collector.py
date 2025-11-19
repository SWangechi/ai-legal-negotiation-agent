import os
import requests
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = "data/raw"
SOURCES = {
    "kenya_law": "https://kenyalaw.org/caselaw/",
    "un_peacemaker": "https://peacemaker.un.org/document-search",
    "law_insider": "https://www.lawinsider.com/contracts"
}

os.makedirs(f"{BASE_DIR}/contracts", exist_ok=True)
os.makedirs(f"{BASE_DIR}/mediation_cases", exist_ok=True)
os.makedirs(f"{BASE_DIR}/negotiation_samples", exist_ok=True)
os.makedirs(f"{BASE_DIR}/generated", exist_ok=True)

def fetch_text_from_url(url, selector=None, limit=5):
    """Fetch a few legal docs or excerpts from public pages."""
    try:
        print(f"🌍 Crawling: {url}")
        res = requests.get(url, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        texts = []
        if selector:
            for i, tag in enumerate(soup.select(selector)):
                if i >= limit:
                    break
                texts.append(tag.get_text(separator="\n").strip())
        else:
            texts.append(soup.get_text())
        return texts
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return []

def generate_legal_docs():
    """Generate synthetic Kenyan legal docs via OpenAI."""
    prompt_types = [
        ("Consultancy Agreement under Kenyan law", "contracts"),
        ("Mediation agreement resolving a business dispute under Kenyan law", "mediation_cases"),
        ("Negotiation dialogue between two companies under Kenyan contract law", "negotiation_samples"),
    ]
    for i, (prompt, folder) in enumerate(prompt_types * 7, start=1):
        print(f"🧠 Generating document {i}: {prompt}")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Kenyan legal expert creating example documents for AI training."},
                    {"role": "user", "content": f"Generate a realistic, full-length {prompt}. Include clear section headings and proper structure."}
                ]
            )
            content = response.choices[0].message.content.strip()
            path = f"{BASE_DIR}/generated/{folder}_{i}.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"⚠️ Generation failed: {e}")

def collect_real_docs():
    """Collect short excerpts or metadata from real pages."""
    kenya_cases = fetch_text_from_url(SOURCES["kenya_law"], "p", limit=5)
    un_cases = fetch_text_from_url(SOURCES["un_peacemaker"], "p", limit=5)
    law_insider_samples = fetch_text_from_url(SOURCES["law_insider"], "p", limit=5)

    for idx, text in enumerate(kenya_cases):
        with open(f"{BASE_DIR}/mediation_cases/kenya_case_{idx+1}.txt", "w", encoding="utf-8") as f:
            f.write(text)

    for idx, text in enumerate(un_cases):
        with open(f"{BASE_DIR}/mediation_cases/un_case_{idx+1}.txt", "w", encoding="utf-8") as f:
            f.write(text)

    for idx, text in enumerate(law_insider_samples):
        with open(f"{BASE_DIR}/contracts/law_insider_contract_{idx+1}.txt", "w", encoding="utf-8") as f:
            f.write(text)

def build_metadata():
    """Create metadata.csv summarizing all collected files."""
    csv_path = "data/metadata.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "title", "type", "source", "date_collected", "notes"])
        idx = 1
        for folder, doc_type in [
            ("contracts", "contract"),
            ("mediation_cases", "mediation"),
            ("negotiation_samples", "negotiation"),
            ("generated", "synthetic")
        ]:
            folder_path = f"{BASE_DIR}/{folder}"
            for filename in os.listdir(folder_path):
                if filename.endswith(".txt"):
                    writer.writerow([
                        idx,
                        filename.replace(".txt", ""),
                        doc_type,
                        folder,
                        datetime.now().strftime("%Y-%m-%d"),
                        "Auto-collected"
                    ])
                    idx += 1
    print(f"✅ Metadata saved at {csv_path}")

if __name__ == "__main__":
    print("🚀 Starting dataset collection process...")
    collect_real_docs()
    generate_legal_docs()
    build_metadata()
    print("🎯 Dataset collection complete! Check the /data folder.")
