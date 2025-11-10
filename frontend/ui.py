import streamlit as st
import requests
import time
from PyPDF2 import PdfReader

BACKEND_ANALYZE_URL = "http://127.0.0.1:8000/analyze"
BACKEND_FEEDBACK_URL = "http://127.0.0.1:8000/api/feedback"
TIMEOUT_SECONDS = 600
MAX_FILE_SIZE_MB = 200

# ----------------------------
# 📘 HELPER FUNCTIONS
# ----------------------------
def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()


def analyze_contract(text, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.post(
                BACKEND_ANALYZE_URL, json={"text": text}, timeout=TIMEOUT_SECONDS
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"⚠️ Backend returned HTTP {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            st.warning(
                f"⚠️ Backend connection failed (attempt {attempt + 1}/{retries}). Retrying..."
            )
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                st.error(
                    "❌ Could not connect to backend. Please make sure it's running on port 8000."
                )
                return None
        except requests.exceptions.ReadTimeout:
            st.error("⏱️ Backend took too long to respond.")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None


# ----------------------------
# 🎨 UI SECTIONS
# ----------------------------
def render_contract_analysis_ui():
    """Main Contract Upload and Analysis Section"""
    st.title("⚖️ AI Legal Negotiation & Mediation Agent")
    st.markdown(
        "Upload a contract and let the AI analyze, detect issues, and propose fair alternatives based on **Kenyan law**."
    )

    uploaded_file = st.file_uploader("📄 Upload Contract (.txt or .pdf)", type=["txt", "pdf"])

    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"❌ File too large! Limit is {MAX_FILE_SIZE_MB} MB.")
            return

        st.success(f"✅ {uploaded_file.name} ({file_size_mb:.2f} MB) uploaded successfully!")

        # Extract text
        if uploaded_file.type == "application/pdf":
            contract_text = read_pdf(uploaded_file)
        else:
            contract_text = uploaded_file.read().decode("utf-8")

        if not contract_text.strip():
            st.error("⚠️ No readable text found in the uploaded document.")
            return

        st.text_area("🧾 Contract Preview", contract_text[:2000], height=250)

        if st.button("🔍 Analyze Contract"):
            with st.spinner("🧠 Analyzing contract clauses... Please wait."):
                results = analyze_contract(contract_text)
                if results:
                    st.success("✅ Negotiation analysis completed.")

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
                        mime="text/plain",
                    )


def render_feedback_section():
    """Feedback Form Section"""
    st.markdown("---")
    st.subheader("💬 Share Your Feedback")

    with st.form("feedback_form"):
        username = st.text_input("Your Name (optional)", "")
        rating = st.slider("Rate your experience", 1, 5, 5)
        comments = st.text_area("Your feedback")

        submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            payload = {
                "username": username or "Anonymous",
                "rating": rating,
                "comments": comments,
            }

            try:
                response = requests.post(BACKEND_FEEDBACK_URL, json=payload)
                if response.status_code == 200:
                    st.success("✅ Thank you! Your feedback has been recorded.")
                else:
                    st.error(
                        f"❌ Failed to send feedback (Error {response.status_code})"
                    )
            except Exception as e:
                st.error(f"❌ Could not connect to backend: {e}")


def render_footer():
    st.markdown("---")
    st.markdown(
        "🧠 Built with ❤️ by **Stella Gituire** | Powered by **AI Legal Negotiation & Mediation Agent (Kenyan Law Edition)**"
    )


# ----------------------------
# 🚀 MAIN ENTRY POINT
# ----------------------------
def run_ui():
    render_contract_analysis_ui()
    render_feedback_section()
    render_footer()
