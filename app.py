import streamlit as st
import requests
import time
import base64
from io import BytesIO
from PyPDF2 import PdfReader

# ==============================
# ⚙️ Configuration
# ==============================
BACKEND_URL = "http://127.0.0.1:8000/analyze"
MAX_FILE_SIZE_MB = 200
TIMEOUT_SECONDS = 600

st.set_page_config(page_title="⚖️ AI Legal Negotiation & Mediation Agent", layout="wide")

# ==============================
# 📄 Helper Functions
# ==============================

def read_pdf(file):
    """Extract text from uploaded PDF file."""
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def analyze_contract(text, retries=3, delay=5):
    """Send contract text to backend with retry and timeout logic."""
    for attempt in range(retries):
        try:
            response = requests.post(
                BACKEND_URL,
                json={"text": text},
                timeout=TIMEOUT_SECONDS
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"⚠️ Backend returned HTTP {response.status_code}")
                return None
        except requests.exceptions.ConnectionError as e:
            st.warning(f"⚠️ Backend connection failed (attempt {attempt + 1}/{retries}). Retrying...")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                st.error("❌ Could not connect to backend. Please make sure it's running on port 8000.")
                return None
        except requests.exceptions.ReadTimeout:
            st.error("⏱️ Backend took too long to respond. Try again with a smaller document.")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None

# ==============================
# 🎨 UI Layout
# ==============================
st.title("⚖️ AI Legal Negotiation & Mediation Agent")
st.markdown("""
Upload a contract and let the AI analyze, detect issues, and propose fair alternatives based on **Kenyan law**.
""")

# ------------------------------
# Upload Contract Section
# ------------------------------
uploaded_file = st.file_uploader("📄 Upload Contract (.txt or .pdf)", type=["txt", "pdf"])
if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File too large! Limit is {MAX_FILE_SIZE_MB} MB.")
    else:
        st.success(f"✅ {uploaded_file.name} ({file_size_mb:.2f} MB) uploaded successfully!")

        # Extract text
        if uploaded_file.type == "application/pdf":
            contract_text = read_pdf(uploaded_file)
        else:
            contract_text = uploaded_file.read().decode("utf-8")

        if contract_text.strip() == "":
            st.error("⚠️ No readable text found in the uploaded document.")
        else:
            st.text_area("🧾 Contract Preview", contract_text[:2000], height=250)
            
            # Analyze Button
            if st.button("🔍 Analyze Contract"):
                with st.spinner("🧠 Analyzing contract clauses... Please wait."):
                    results = analyze_contract(contract_text)
                    if results:
                        st.success("✅ Negotiation analysis completed.")
                        
                        # Display results
                        for i, clause in enumerate(results.get("clauses", []), start=1):
                            st.markdown(f"### ⚖️ Clause {i}")
                            st.write(clause.get("text", ""))
                            
                            if "revised" in clause:
                                with st.expander("💡 Suggested Revision"):
                                    st.write(clause["revised"])
                            if "rationale" in clause:
                                st.info(f"🤝 Rationale: {clause['rationale']}")
                            if "legal_refs" in clause:
                                st.caption(f"📚 Legal References: {clause['legal_refs']}")
                        
                        st.download_button(
                            label="⬇️ Download Analysis Report",
                            data=str(results),
                            file_name="contract_analysis.txt",
                            mime="text/plain"
                        )

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.markdown(
    "🧠 Built with ❤️ by **Stella Gituire** | "
    "Powered by **AI Legal Negotiation & Mediation Agent (Kenyan Law Edition)**"
)
