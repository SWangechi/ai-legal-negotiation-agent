import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import csv
import random
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = "data/raw/generated"
os.makedirs(BASE_DIR, exist_ok=True)

CONTRACT_TYPES = [
    "Employment Agreement", "Software Development Contract", "Consultancy Agreement",
    "Service Level Agreement", "Freelance Creative Contract", "Partnership Agreement",
    "Construction Contract", "Supply Agreement", "Non-Disclosure Agreement",
    "Lease Agreement", "Research Collaboration Agreement", "Franchise Agreement"
]

MEDIATION_TYPES = [
    "Workplace dispute mediation", "Tenant-landlord dispute mediation",
    "Business partnership dissolution mediation", "Customer complaint mediation",
    "Family business mediation", "Intellectual property dispute mediation",
    "Employer-employee grievance mediation", "Vendor contract breach mediation",
    "Startup co-founder conflict mediation", "Service dissatisfaction mediation",
    "Client payment dispute mediation", "Team conflict mediation"
]

NEGOTIATION_TYPES = [
    "Negotiation between startup and investor", "Salary negotiation between employer and employee",
    "Contract terms negotiation between supplier and retailer", "Settlement negotiation in civil dispute",
    "Freelancer rate negotiation", "Software licensing negotiation",
    "Business acquisition negotiation", "Partnership revenue sharing negotiation",
    "Government tender negotiation", "Product distribution negotiation", "Vendor service fee negotiation"
]

def generate_legal_doc(prompt, doc_type, idx):
    """Generate one realistic legal document under Kenyan law."""
    print(f"🧠 Generating {doc_type} document {idx}: {prompt}")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Kenyan legal expert drafting realistic legal agreements, mediation summaries, and negotiation dialogues for AI training."},
                {"role": "user", "content": f"Write a comprehensive {prompt} under Kenyan law. Include clear sections, proper formatting, and realistic context."}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        filename = f"{doc_type}_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(BASE_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Saved: {path}")
        time.sleep(random.uniform(1, 2))
        return filename

    except Exception as e:
        print(f"⚠️ Error generating {prompt}: {e}")
        return None


def generate_bulk_documents():
    """Generate a total of ~35 additional legal docs across categories."""
    generated_files = []

    
    for i, topic in enumerate(CONTRACT_TYPES, start=1):
        name = generate_legal_doc(topic, "contract", i)
        if name: generated_files.append(("contract", name))

    for i, topic in enumerate(MEDIATION_TYPES, start=1):
        name = generate_legal_doc(topic, "mediation", i)
        if name: generated_files.append(("mediation", name))

    for i, topic in enumerate(NEGOTIATION_TYPES, start=1):
        name = generate_legal_doc(topic, "negotiation", i)
        if name: generated_files.append(("negotiation", name))

    metadata_path = "data/metadata.csv"
    with open(metadata_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for idx, (doc_type, name) in enumerate(generated_files, start=1):
            writer.writerow([
                f"auto_{idx}",
                name.replace(".txt", ""),
                doc_type,
                "generated",
                datetime.now().strftime("%Y-%m-%d"),
                "Expanded synthetic document"
            ])

    print(f"📈 Added {len(generated_files)} new documents to metadata.")
    print(f"🎯 Total dataset now exceeds 50 documents ✅")


if __name__ == "__main__":
    print("🚀 Starting dataset expansion...")
    generate_bulk_documents()
    print("🎉 Dataset expansion complete! Check data/raw/generated/")
