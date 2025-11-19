"""
Streamlit UI for AI Legal Negotiation & Mediation Agent (Kenya edition)
Polished frontend: navigation, Kenyan branding, dark-mode, contract upload/preview,
robust backend calls, clause extraction preview, chat-style negotiation UI,
mediation, feedback, past analyses, PDF export (if reportlab).
"""

import streamlit as st
import requests
import time
import io
import base64
from datetime import datetime
from PyPDF2 import PdfReader

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


API_BASE = "https://YOUR_BACKEND_URL"   # No trailing slash
NEGOTIATE_ENDPOINT = f"{API_BASE}/negotiate"
MEDIATE_ENDPOINT    = f"{API_BASE}/mediate"
ANALYZE_ENDPOINT    = f"{API_BASE}/analyze"
FEEDBACK_ENDPOINT   = f"{API_BASE}/feedback"

TIMEOUT_SECONDS = 60  

PRIMARY = "#0b2545"  
ACCENT = "#d4af37"   
APP_BG = "#0f1720"
PANEL_BG = "#15181b"
SIDEBAR_BG = "#1f2933"
TEXT = "#e6eef8"
MUTED = "#9aa7b7"

st.set_page_config(
    page_title="⚖️ AI Legal Negotiation & Mediation Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    :root {{ --primary: {PRIMARY}; --accent: {ACCENT}; --app-bg: {APP_BG}; --panel-bg: {PANEL_BG}; --sidebar-bg: {SIDEBAR_BG}; --text: {TEXT}; --muted: {MUTED}; }}
    .stApp {{
        background-color: var(--app-bg);
        color: var(--text);
    }}
    .sidebar .sidebar-content {{
        background-color: var(--sidebar-bg);
    }}
    .title {{
        font-size:40px; font-weight:700; color:var(--text);
    }}
    .brand {{
        color: var(--accent); font-weight:700; font-size:18px;
    }}
    .contract-box {{
        background: var(--panel-bg); padding:12px; border-radius:8px; color:var(--text);
    }}
    .muted {{ color:var(--muted) }}
    .gold-btn {{
        background: linear-gradient(90deg, {ACCENT}, #f2d07b); color:black; border-radius:8px; padding:8px 12px; text-decoration:none;
    }}
    .clause-card {{
        background: rgba(255,255,255,0.02); padding:14px; border-radius:8px; margin-bottom:8px;
    }}
    .footer {{ text-align:center; color: #2b3b53; margin-top:30px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def read_pdf(file) -> str:
    """Extract text from uploaded PDF file using PyPDF2"""
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""

def robust_post_json(url: str, payload: dict, timeout=TIMEOUT_SECONDS):
    """
    POST JSON to backend. Return (ok: bool, parsed_json or raw_text_or_error)
    If backend returns non-JSON, return False and raw text for debugging.
    """
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, timeout=timeout, headers=headers)
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"

    if resp.status_code != 200:
        return False, f"HTTP {resp.status_code}: {resp.text}"

    try:
        return True, resp.json()
    except Exception:
        return False, resp.text

def extract_clauses_simple(text: str, min_len=40):
    """
    Lightweight clause splitter for UI preview: split by numbered lines and blank lines.
    Not perfect but good for highlights in UI.
    """
    lines = [l.rstrip() for l in text.splitlines()]
    joined = "\n".join(lines)
    import re
    pieces = re.split(r"\n\s*\d+\.\s+|\n\s*\d+\)\s+|\n\s*\n\s*", joined)
    clauses = [p.strip() for p in pieces if len(p.strip()) >= min_len]
    return clauses

def export_analysis_pdf(title: str, contract_text: str, clauses_analysis: list):
    """Export a simple PDF report using reportlab (if available). Returns bytes"""
    if not REPORTLAB_AVAILABLE:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, title[:80])
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Generated: {datetime.utcnow().isoformat()} UTC")
    y -= 30

    # Contract snippet
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Contract preview (first 800 chars):")
    y -= 16
    c.setFont("Helvetica", 9)
    contract_preview = contract_text[:800].replace("\n", " ")
    for chunk in [contract_preview[i:i+140] for i in range(0, len(contract_preview), 140)]:
        c.drawString(margin, y, chunk)
        y -= 12
        if y < margin + 80:
            c.showPage()
            y = height - margin

    for i, ca in enumerate(clauses_analysis, start=1):
        if y < margin + 120:
            c.showPage()
            y = height - margin
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, f"Clause {i}:")
        y -= 14
        c.setFont("Helvetica", 9)
        clause_text = ca.get("clause", "")[:600].replace("\n", " ")
        for chunk in [clause_text[j:j+140] for j in range(0, len(clause_text), 140)]:
            c.drawString(margin, y, chunk)
            y -= 12
        y -= 6
        analysis_text = ""
        analysis = ca.get("analysis") or ca
        if isinstance(analysis, dict):
            parts = []
            for k in ("issue", "risk", "revision", "rationale", "legal_refs"):
                if k in analysis:
                    parts.append(f"{k.capitalize()}: {str(analysis[k])}")
            analysis_text = " | ".join(parts)[:1200].replace("\n", " ")
        else:
            analysis_text = str(analysis)[:1200].replace("\n", " ")
        for chunk in [analysis_text[j:j+140] for j in range(0, len(analysis_text), 140)]:
            c.drawString(margin+10, y, chunk)
            y -= 12
            if y < margin + 60:
                c.showPage()
                y = height - margin
        y -= 10

    c.save()
    buf.seek(0)
    return buf.read()

def make_download_button(data_bytes: bytes, filename: str, mime: str):
    """Return an HTML download link for bytes"""
    b64 = base64.b64encode(data_bytes).decode()
    href = f'<a href="data:{mime};base64,{b64}" download="{filename}" class="gold-btn">⬇️ Download {filename}</a>'
    return href

if "past_analyses" not in st.session_state:
    st.session_state.past_analyses = []
if "negotiation_history" not in st.session_state:
    st.session_state.negotiation_history = []  

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


with st.sidebar:
    st.markdown(f"<div style='padding:6px 0'><span class='brand'>⚖️ Legal AI Agent</span></div>", unsafe_allow_html=True)
    st.caption("Kenyan Contract Law")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ("Contract Analysis", "Negotiation Simulator", "Mediation Agent", "Past Analyses", "Feedback", "Settings"),
        index=0,
    )
    st.markdown("---")
    st.markdown("Toggle Dark Mode")
    dm = st.checkbox("Enable Dark Mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dm

    st.markdown("---")
    st.markdown("<small>© 2025 AI Legal Negotiation & Mediation Agent • Stella Gituire</small>", unsafe_allow_html=True)

st.markdown("<div class='title'>⚖️ Contract Legal AI — Kenya Edition</div>", unsafe_allow_html=True)
st.markdown(f"<div class='muted'>Automated clause review, negotiation simulation & mediation grounded in Kenyan law</div>", unsafe_allow_html=True)
st.markdown("----")

if page == "Contract Analysis":
    st.header("📄 Contract Analysis (Kenyan Law)")
    col1, col2 = st.columns([2, 3])
    with col1:
        uploaded_file = st.file_uploader("Upload Contract (PDF or TXT) — max 200MB", type=["pdf", "txt"])
        contract_text = ""
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.success(f"{uploaded_file.name} uploaded ({file_size_mb:.2f} MB)")
            if uploaded_file.type == "application/pdf":
                contract_text = read_pdf(uploaded_file)
            else:
                try:
                    contract_text = uploaded_file.read().decode("utf-8")
                except Exception:
                    contract_text = uploaded_file.read().decode("latin-1")
            st.markdown("**Preview**")
            st.text_area("Contract Preview", contract_text[:4000], height=240, key="contract_preview")
        else:
            st.info("Upload a PDF or TXT file to begin analysis.")

        analyze_btn = st.button("Analyze Contract", help="Extract clauses and run legal reasoning (backend)")
        if analyze_btn and not contract_text:
            st.error("Please upload a contract first.")

    with col2:
        st.markdown("### Clause extraction preview")
        if contract_text:
            with st.spinner("Extracting clauses..."):
                clauses = extract_clauses_simple(contract_text)
                st.write(f"Found **{len(clauses)}** candidate clauses (simple heuristic).")
                for i, c in enumerate(clauses[:8], start=1):
                    st.markdown(f"**Clause {i}**")
                    st.write(c[:500] + ("..." if len(c) > 500 else ""))
        else:
            st.info("Clause preview will appear once a contract is uploaded.")

    if analyze_btn and contract_text:
        with st.spinner("Clause analysis loading..."):
            ok, resp = robust_post_json(ANALYZE_ENDPOINT, {"text": contract_text}, timeout=120)
            if not ok:
                st.error("Contract analysis failed or returned non-JSON response.")
                st.code(str(resp))
            else:
                results = resp
                st.success("Contract analysis completed.")
                entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "filename": uploaded_file.name if uploaded_file else "pasted_text",
                    "results": results,
                    "contract_text": contract_text
                }
                st.session_state.past_analyses.insert(0, entry)

                clauses_list = results.get("clauses") or []
                for i, cl in enumerate(clauses_list, start=1):
                    with st.expander(f"⚖️ Clause {i} — preview & analysis", expanded=(i <= 3)):
                        st.markdown("**Clause text**")
                        st.write(cl.get("clause") if isinstance(cl, dict) else str(cl)[:2000])
                        st.markdown("**AI Reasoning**")
                        
                        analysis = cl.get("analysis") if isinstance(cl, dict) else cl
                        if isinstance(analysis, dict):
                            for key in ("issue", "risk", "revision", "rationale", "legal_refs"):
                                if key in analysis:
                                    st.markdown(f"**{key.capitalize()}**")
                                    st.write(analysis.get(key))
                            leftover = {k: v for k, v in analysis.items() if k not in ("issue","risk","revision","rationale","legal_refs")}
                            if leftover:
                                st.markdown("**Other reasoning data**")
                                st.json(leftover)
                        else:
                            st.write(analysis)

                        srcs = cl.get("sources") if isinstance(cl, dict) else None
                        if srcs:
                            st.markdown("**Sources / Supporting docs**")
                            for s in srcs[:6]:
                                if isinstance(s, dict):
                                    meta = s.get("meta") or s.get("meta", s.get("text", "")) or ""
                                    text_snip = (s.get("text") or "")[:240]
                                    st.caption(meta if meta else text_snip)
                                else:
                                    st.caption(str(s)[:240])

                if REPORTLAB_AVAILABLE:
                    pdf_bytes = export_analysis_pdf(f"Contract Analysis - {entry['filename']}", contract_text, clauses_list)
                    if pdf_bytes:
                        st.markdown(make_download_button(pdf_bytes, f"analysis_{entry['filename']}.pdf", "application/pdf"), unsafe_allow_html=True)

                st.download_button(
                    "Download Raw Analysis (JSON)",
                    data=str(results),
                    file_name=f"analysis_{entry['filename']}.json",
                    mime="application/json"
                )

if page == "Negotiation Simulator":
    st.header("Negotiation Simulator")
    st.markdown("Simulate a negotiation for a clause. Uses backend `/negotiate` endpoint to produce a structured result.")

    col_a, col_b = st.columns([1, 2])
    with col_a:
        clause_in = st.text_area("Clause (brief)", height=80, key="neg_clause")
        counter_pos = st.text_area("Counterparty Position", height=120, key="neg_position")
        simulate = st.button("Simulate Negotiation")

        if st.button("Clear Negotiation History"):
            st.session_state.negotiation_history = []
            st.success("History cleared.")

        st.markdown("---")
        st.markdown("Save / Export")

        if st.session_state.negotiation_history:
            latest = st.session_state.negotiation_history[0]
            st.download_button(
                "Download Latest Negotiation (txt)",
                data=str(latest["result"]),
                file_name=f"negotiation_{int(time.time())}.txt",
                mime="text/plain"
            )

    # --------------------
    # Right panel
    # --------------------
    with col_b:

        if simulate:
            if not clause_in.strip() or not counter_pos.strip():
                st.error("Please supply both the clause and counterparty position.")
            else:
                with st.spinner("Simulating negotiation..."):
                    ok, resp = robust_post_json(
                        NEGOTIATE_ENDPOINT,
                        {"clause": clause_in, "position": counter_pos},
                        timeout=90
                    )

                    if not ok:
                        st.error("Negotiation failed.")
                        st.code(str(resp))
                    else:
                        payload = resp.get("result", resp)

                        st.session_state.negotiation_history.insert(0, {
                            "role": "system",
                            "time": datetime.utcnow().isoformat(),
                            "clause": clause_in,
                            "position": counter_pos,
                            "result": payload
                        })
                        st.success("Negotiation simulated.")

        st.markdown("###Latest Negotiation Results")

        if not st.session_state.negotiation_history:
            st.info("No negotiation runs yet.")
            st.stop()

        latest = st.session_state.negotiation_history[0]
        payload = latest["result"]

        st.markdown("**Context**")
        st.write(f"- **Clause:** {latest['clause']}")
        st.write(f"- **Counterparty:** {latest['position']}")
        st.markdown("---")

        if isinstance(payload, dict):
            dialogue = payload.get("dialogue")
            revision = payload.get("mutually_beneficial_revision")
            tradeoffs = payload.get("tradeoffs")
            winwin = payload.get("win_win_justification") or payload.get("win-win") or payload.get("justification")

            if dialogue:
                st.markdown("### Simulated Negotiation:")
                for turn in dialogue:
                    speaker = turn.get("party", "").upper()
                    text = turn.get("text", "")
                    st.markdown(f"- **Party {speaker}:** {text}")

            if revision:
                st.markdown("### Mutually Beneficial Revision (Draft Clause):")
                st.markdown(revision)

            if tradeoffs:
                st.markdown("### Trade-offs:")
                for t in tradeoffs:
                    st.markdown(f"- {t}")

            if winwin:
                st.markdown("### Win–Win Justification:")
                st.markdown(winwin)

            st.stop()

        
        text = str(payload).strip()

        if text.startswith("[") and "party" in text.lower():
            st.markdown("### Simulated Negotiation:")

            import re
            matches = re.findall(r'\{([^}]+)\}', text)

            for m in matches:
                p = re.search(r'"party"\s*:\s*"(.+?)"', m)
                t = re.search(r'"text"\s*:\s*"(.+?)"', m)

                if p and t:
                    st.markdown(f"- **Party {p.group(1).upper()}:** {t.group(1)}")

        else:
            st.markdown("### Negotiation Output")
            st.markdown(text)

if page == "Mediation Agent":
    st.header("Mediation Agent")
    st.markdown("Enter both parties' statements and get a neutral summary, interests, objective evaluation and fair compromise grounded in Kenyan ADR principles.")

    a = st.text_area("Party A statement", height=150)
    b = st.text_area("Party B statement", height=150)

    if st.button("Mediate"):
        if not a.strip() or not b.strip():
            st.error("Please provide both Party A and Party B statements.")
        else:
            with st.spinner("Running mediation..."):
                ok, resp = robust_post_json(MEDIATE_ENDPOINT, {"a": a, "b": b}, timeout=90)
                if not ok:
                    st.error("Mediation failed or backend non-JSON response.")
                    st.code(str(resp))
                else:
                    st.success("Mediation result")

                    payload = resp.get("result")

                    if isinstance(payload, dict) and "result" in payload:
                        payload = payload["result"]

                    st.markdown(payload)


if page == "Past Analyses":
    st.header("Past Analyses")
    if not st.session_state.past_analyses:
        st.info("No past analyses saved in this session. Analyses are stored to session state after running /analyze.")
    else:
        for idx, entry in enumerate(st.session_state.past_analyses):
            with st.expander(f"{idx+1}. {entry['filename']} • {entry['timestamp']}", expanded=(idx==0)):
                st.write("Contract preview (first 800 chars):")
                st.write(entry["contract_text"][:800])
                st.write("Results:")
                st.json(entry["results"])
                st.download_button(
                    "Download analysis JSON",
                    data=str(entry["results"]),
                    file_name=f"past_analysis_{idx+1}.json",
                    mime="application/json"
                )

if page == "Feedback":
    st.header("Feedback")
    st.markdown("Help us improve the adaptive reasoning engine — your comments will be stored and (optionally) added to memory.")
    username = st.text_input("Your name (optional)")
    rating = st.slider("Rating", min_value=1, max_value=5, value=5)
    comments = st.text_area("Comments / Suggestions", height=140)
    if st.button("Submit Feedback"):
        if not comments.strip():
            st.error("Please provide feedback comments.")
        else:
            with st.spinner("Submitting feedback..."):
                ok, resp = robust_post_json(FEEDBACK_ENDPOINT, {"username": username or "Anonymous", "rating": rating, "comments": comments}, timeout=30)
                if not ok:
                    st.error("Failed to send feedback.")
                    st.code(str(resp))
                else:
                    st.success("Thank you! Your feedback has been recorded.")
                    st.balloons()

if page == "Settings":
    st.header("⚙️ Settings")
    st.markdown("- Backend URL: " + BACKEND_URL)
    st.markdown(f"- ReportLab available for PDF export: **{REPORTLAB_AVAILABLE}**")
    st.markdown("Tip: run `streamlit run ui.py` from the repository root so `backend/` imports resolve correctly.")
    st.markdown("More features coming soon...")

# footer / small print
st.markdown("---")
st.markdown("<small style='color:#9aa7b7'>Built with ❤️ by Stella Gituire • AI Legal Negotiation & Mediation Agent (Kenya edition)</small>", unsafe_allow_html=True)
