"""
Streamlit UI for AI Legal Negotiation & Mediation Agent (Kenya Edition)
Modern dark premium look (gold + navy), with:
- Contract analysis (clause-by-clause)
- Negotiation simulator
- Mediation agent
- Session-based past analyses
- Feedback
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

BACKEND_URL = "http://127.0.0.1:8000"
ANALYZE_ENDPOINT = f"{BACKEND_URL}/analyze"
NEGOTIATE_ENDPOINT = f"{BACKEND_URL}/negotiate"
MEDIATE_ENDPOINT = f"{BACKEND_URL}/mediate"
FEEDBACK_ENDPOINT = f"{BACKEND_URL}/feedback"

TIMEOUT_SECONDS = 600

PRIMARY = "#0B5D1E"      # Deep Kenyan Green
ACCENT = "#CFAA4A"       # Gold trim (premium)
APP_BG = "#F4F3EF"       # Light legal parchment
PANEL_BG = "#FFFFFF"     # White panels
SIDEBAR_BG = "#E3EFE7"   # Soft green sidebar
TEXT = "#1A1A1A"         # Deep charcoal text
MUTED = "#6E7A73"        # Muted grey-green
DANGER = "#B51F1F"       # Legal flag red
SUCCESS = "#0E8A39"      # Bright but professional green



st.set_page_config(
    page_title="⚖️ AI Legal Negotiation & Mediation Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
<style>
:root {{
  --primary: {PRIMARY};
  --accent: {ACCENT};
  --app-bg: {APP_BG};
  --panel-bg: {PANEL_BG};
  --sidebar-bg: {SIDEBAR_BG};
  --text: {TEXT};
  --muted: {MUTED};
}}

html, body, .stApp {{
  background-color: var(--app-bg);
  color: var(--text);
}}

section.main > div {{
  padding-top: 0.5rem;
}}

.sidebar .sidebar-content, .stSidebar, div[data-testid="stSidebar"] {{
  background-color: var(--sidebar-bg) !important;
}}

h1, h2, h3, h4, h5, h6 {{
  color: var(--text);
}}

a, a:visited {{
  color: var(--accent);
}}

.block-container {{
  padding-top: 1.5rem;
}}

.title-main {{
  font-size: 2.3rem;
  font-weight: 800;
  letter-spacing: 0.03em;
  color: var(--text);
}}

.subtitle-main {{
  color: var(--muted);
  font-size: 0.95rem;
  margin-top: 0.25rem;
}}

.badge-pill {{
  display: inline-flex;
  align-items: center;
  padding: 0.1rem 0.55rem;
  border-radius: 999px;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: rgba(255,255,255,0.03);
  color: var(--muted);
  border: 1px solid rgba(255,255,255,0.06);
}}

.card-panel {{
  background-color: var(--panel-bg);
  padding: 1.0rem 1.2rem;
  border-radius: 0.85rem;
  border: 1px solid rgba(255,255,255,0.06);
}}

.clause-card {{
  background: rgba(11,37,69,0.55);
  padding: 0.9rem 1.0rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(212,175,55,0.35);
  margin-bottom: 0.5rem;
}}

.clause-title {{
  font-weight: 600;
  font-size: 0.95rem;
  color: {ACCENT};
}}

.clause-chip {{
  display: inline-block;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  border: 1px solid rgba(255,255,255,0.08);
  margin-left: 0.25rem;
}}

.label-muted {{
  font-size: 0.8rem;
  color: var(--muted);
}}

.hr-soft {{
  border: none;
  border-top: 1px solid rgba(255,255,255,0.08);
  margin: 0.5rem 0 0.8rem 0;
}}

.gold-btn {{
  background: linear-gradient(90deg, {ACCENT}, #f3d58a);
  color: #1a1305 !important;
  font-weight: 600;
  padding: 0.5rem 0.9rem;
  border-radius: 0.6rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
}}

.gold-btn:hover {{
  filter: brightness(1.03);
}}

.footer-text {{
  text-align:center;
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 2.0rem;
  padding-bottom: 0.7rem;
}}

small.muted {{
  color: var(--muted);
  font-size: 0.75rem;
}}
</style>
""",
    unsafe_allow_html=True,
)

def read_pdf(file) -> str:
    """Extract text from uploaded PDF using PyPDF2."""
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
    POST JSON to backend.
    Returns (ok: bool, result: dict|str).
    If non-200 or non-JSON, returns False and raw body/error.
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
    Lightweight heuristic clause splitter:
    - Splits by numbered items & blank lines.
    """
    import re

    lines = [l.rstrip() for l in text.splitlines()]
    joined = "\n".join(lines)
    pieces = re.split(
        r"\n\s*\d+\.\s+|\n\s*\d+\)\s+|\n\s*[A-Za-z]\)\s+|\n\s*\n\s*", joined
    )
    clauses = [p.strip() for p in pieces if len(p.strip()) >= min_len]
    return clauses


def export_analysis_pdf(title: str, contract_text: str, clauses_analysis: list):
    """Export a simple PDF report using reportlab (if available). Returns bytes or None."""
    if not REPORTLAB_AVAILABLE:
        return None

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    margin = 48
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, title[:80])
    y -= 30
    c.setFont("Helvetica", 9)
    c.drawString(margin, y, f"Generated: {datetime.utcnow().isoformat()} UTC")
    y -= 24

    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Contract preview:")
    y -= 16
    c.setFont("Helvetica", 9)
    preview = contract_text[:800].replace("\n", " ")
    for chunk in [preview[i : i + 110] for i in range(0, len(preview), 110)]:
        c.drawString(margin, y, chunk)
        y -= 12
        if y < margin + 80:
            c.showPage()
            y = height - margin

    for idx, ca in enumerate(clauses_analysis, start=1):
        if y < margin + 120:
            c.showPage()
            y = height - margin

        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, f"Clause {idx}")
        y -= 14

        c.setFont("Helvetica", 9)
        clause_text = (ca.get("clause") or "")[:550].replace("\n", " ")
        for chunk in [clause_text[i : i + 110] for i in range(0, len(clause_text), 110)]:
            c.drawString(margin, y, chunk)
            y -= 12
            if y < margin + 60:
                c.showPage()
                y = height - margin

        y -= 6
        analysis = ca.get("analysis") or {}
        if isinstance(analysis, dict):
            summary = (
                analysis.get("clause_summary")
                or analysis.get("summary")
                or analysis.get("issue")
                or ""
            )
            revision = (
                analysis.get("suggested_revision")
                or analysis.get("revision")
                or analysis.get("recommendation")
                or ""
            )
            line = f"Summary: {summary} | Suggested: {revision}"
        else:
            line = str(analysis)[:400]

        for chunk in [line[i : i + 110] for i in range(0, len(line), 110)]:
            c.drawString(margin + 10, y, chunk)
            y -= 12
            if y < margin + 60:
                c.showPage()
                y = height - margin
        y -= 10

    c.save()
    buf.seek(0)
    return buf.read()


def make_download_button(data_bytes: bytes, filename: str, mime: str):
    """Return an HTML download link for bytes."""
    b64 = base64.b64encode(data_bytes).decode()
    href = (
        f'<a href="data:{mime};base64,{b64}" download="{filename}" class="gold-btn">'
        f"⬇️ Download {filename}</a>"
    )
    return href


def _maybe_to_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _pretty_dict_like_string(value: str):
    """
    If value looks like a dict JSON string, try to pretty them as bullet lines.
    Otherwise return value.
    """
    import json

    v = str(value).strip()
    if not v.startswith("{"):
        return None
    try:
        obj = json.loads(v)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    lines = []
    for k, val in obj.items():
        lines.append(f"- **{k.replace('_', ' ').title()}**: {val}")
    return "\n".join(lines)


def render_clause_analysis_block(analysis: dict):
    """
    Render a single clause's analysis in a user-friendly, Kenyan-law oriented format.
    Handles:
    - clause_summary / summary
    - issues / risks
    - compliance_notes
    - suggested_revision / revision / recommendation
    """

    if not isinstance(analysis, dict):
        st.write(str(analysis))
        return

    summary = (
        analysis.get("clause_summary")
        or analysis.get("summary")
        or analysis.get("issue")
        or analysis.get("analysis")
    )

    if summary:
        st.markdown("**Summary**")
        if isinstance(summary, dict):
            for k, v in summary.items():
                st.markdown(f"- **{k.replace('_', ' ').title()}**: {v}")
        else:
            pretty = _pretty_dict_like_string(str(summary))
            if pretty:
                st.markdown(pretty, unsafe_allow_html=True)
            else:
                st.write(summary)

    issues = analysis.get("issues") or analysis.get("risks") or analysis.get("risk")
    issues_list = _maybe_to_list(issues)
    if issues_list:
        st.markdown("**Issues / Risks**")
        for item in issues_list:
            if isinstance(item, dict):
                section = item.get("section") or item.get("area") or ""
                concern = item.get("concern") or item.get("detail") or str(item)
                if section:
                    st.markdown(f"- **{section}** — {concern}")
                else:
                    st.markdown(f"- {concern}")
            else:
                st.markdown(f"- {item}")

    compliance = (
        analysis.get("compliance_notes")
        or analysis.get("legal_refs")
        or analysis.get("law_notes")
    )
    comp_list = _maybe_to_list(compliance)
    if comp_list:
        st.markdown("**Compliance Notes (Kenyan law focus)**")
        for note in comp_list:
            st.markdown(f"- {note}")

    suggested = (
        analysis.get("suggested_revision")
        or analysis.get("revision")
        or analysis.get("recommendation")
    )
    if suggested:
        st.markdown("**Suggested Revision**")
        if isinstance(suggested, dict):
            for k, v in suggested.items():
                st.markdown(f"- **{k.replace('_', ' ').title()}**: {v}")
        else:
            pretty = _pretty_dict_like_string(str(suggested))
            if pretty:
                st.markdown(pretty, unsafe_allow_html=True)
            else:
                st.write(suggested)


if "past_analyses" not in st.session_state:
    st.session_state.past_analyses = []
if "negotiation_history" not in st.session_state:
    st.session_state.negotiation_history = []

with st.sidebar:
    st.markdown(
        f"""
<div style="padding:0.5rem 0 0.4rem 0;">
  <span style="font-weight:700; font-size:1.1rem; color:{TEXT};">
    ⚖️ Legal AI Agent
  </span>
</div>
<small class="muted">Kenyan Contract Law · Negotiation · Mediation</small>
""",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    page = st.radio(
        "Navigation",
        (
            "Contract Analysis",
            "Negotiation Simulator",
            "Mediation Agent",
            "Past Analyses",
            "Feedback",
            "Settings",
        ),
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<small class='muted'>© 2025 AI Legal Negotiation & Mediation Agent • Stella Gituire</small>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="badge-pill">KENYA · AI · CONTRACTS</div>
<div class="title-main">⚖️ Contract Legal AI — Kenya Edition</div>
<div class="subtitle-main">
Automated clause review, risk flags, negotiation simulation & mediation grounded in Kenyan law.
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("")

if page == "Contract Analysis":
    st.header("📄 Contract Analysis (Kenyan Law)")

    col_left, col_right = st.columns([1.8, 2.2], gap="large")

    contract_text = ""

    with col_left:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.subheader("Upload Contract")
        uploaded_file = st.file_uploader(
            "PDF or TXT (max 200MB)", type=["pdf", "txt"], label_visibility="collapsed"
        )

        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.markdown(
                f"<small class='muted'>{uploaded_file.name} • {file_size_mb:.2f} MB</small>",
                unsafe_allow_html=True,
            )
            if uploaded_file.type == "application/pdf":
                contract_text = read_pdf(uploaded_file)
            else:
                try:
                    contract_text = uploaded_file.read().decode("utf-8")
                except Exception:
                    contract_text = uploaded_file.read().decode("latin-1")

            st.markdown("<hr class='hr-soft'/>", unsafe_allow_html=True)
            st.markdown("**Contract preview** (first 4000 characters)")
            st.text_area(
                "Preview",
                contract_text[:4000],
                height=260,
                label_visibility="collapsed",
            )
        else:
            st.markdown(
                "<span class='label-muted'>Upload a contract to begin analysis.</span>",
                unsafe_allow_html=True,
            )

        st.markdown("<hr class='hr-soft'/>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze Contract", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)  # end card-panel

    with col_right:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.subheader("Clause Extraction Preview")

        if contract_text:
            with st.spinner("Detecting clauses from your contract..."):
                clauses = extract_clauses_simple(contract_text)
                st.markdown(
                    f"Detected **{len(clauses)}** potential clauses "
                    "(simple heuristic: numbered items + paragraphs)."
                )
                st.markdown("<br/>", unsafe_allow_html=True)

                max_preview = min(12, len(clauses))
                for i, c in enumerate(clauses[:max_preview], start=1):
                    snippet = c[:260] + ("..." if len(c) > 260 else "")
                    st.markdown(
                        f"""
<div class="clause-card">
  <div class="clause-title">Clause {i}
    <span class="clause-chip">preview</span>
  </div>
  <div style="font-size:0.85rem; margin-top:0.35rem;">{snippet}</div>
</div>
""",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Clause preview will appear once a contract is uploaded.")
        st.markdown("</div>", unsafe_allow_html=True)

    if analyze_btn:
        if not contract_text.strip():
            st.error("Please upload a contract first.")
        else:
            st.markdown("----")
            with st.spinner("Running clause-by-clause legal analysis…"):
                ok, resp = robust_post_json(
                    ANALYZE_ENDPOINT, {"text": contract_text}, timeout=600
                )

            if not ok:
                st.error("Contract analysis failed or backend returned non-JSON.")
                st.code(str(resp))
            else:
                st.success("Analysis complete.")

                entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "filename": uploaded_file.name if uploaded_file else "pasted_text",
                    "results": resp,
                    "contract_text": contract_text,
                }
                st.session_state.past_analyses.insert(0, entry)

                clauses_list = resp.get("clauses") or []
                st.subheader("📑 Clause Analyses")

                for i, cl in enumerate(clauses_list, start=1):
                    clause_text = (
                        cl.get("clause")
                        if isinstance(cl, dict)
                        else str(cl)
                    )
                    analysis = (
                        cl.get("analysis")
                        if isinstance(cl, dict)
                        else {}
                    )

                    short_snip = clause_text[:120].replace("\n", " ")
                    st.markdown(
                        f"**Clause {i}** &nbsp;&nbsp;"
                        f"<span class='label-muted'>{short_snip}...</span>",
                        unsafe_allow_html=True,
                    )

                    with st.expander("View clause & AI reasoning", expanded=(i <= 2)):
                        st.markdown("**Clause text**")
                        st.write(clause_text)

                        st.markdown("---")
                        st.markdown("**AI Reasoning (Kenyan law)**")
                        render_clause_analysis_block(analysis)

                if REPORTLAB_AVAILABLE and clauses_list:
                    pdf_bytes = export_analysis_pdf(
                        f"Contract Analysis - {entry['filename']}",
                        contract_text,
                        clauses_list,
                    )
                    if pdf_bytes:
                        st.markdown(
                            make_download_button(
                                pdf_bytes,
                                f"analysis_{entry['filename']}.pdf",
                                "application/pdf",
                            ),
                            unsafe_allow_html=True,
                        )

                st.download_button(
                    "Download Raw Analysis (JSON)",
                    data=str(resp),
                    file_name=f"analysis_{entry['filename']}.json",
                    mime="application/json",
                )

elif page == "Negotiation Simulator":
    st.header("🤝 Negotiation Simulator")

    st.markdown(
        "<span class='label-muted'>Simulate a negotiation around a specific clause and a counterparty position.</span>",
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([1.4, 2.0], gap="large")

    with col_a:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)

        clause_in = st.text_area(
            "Clause (brief)",
            height=110,
            key="neg_clause",
        )
        counter_pos = st.text_area(
            "Counterparty Position",
            height=140,
            key="neg_position",
        )

        simulate = st.button("🤝 Simulate Negotiation", use_container_width=True)

        if st.button("🧹 Clear Negotiation History", use_container_width=True):
            st.session_state.negotiation_history = []
            st.success("History cleared.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Export Latest Negotiation")

        if st.session_state.negotiation_history:
            latest = st.session_state.negotiation_history[0]
            st.download_button(
                "Download Latest Negotiation (txt)",
                data=str(latest["result"]),
                file_name=f"negotiation_{int(time.time())}.txt",
                mime="text/plain",
            )
        else:
            st.caption("Run a negotiation first to enable export.")

    with col_b:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.subheader("Negotiation Output")

        if simulate:
            if not clause_in.strip() or not counter_pos.strip():
                st.error("Please fill in both the clause and counterparty position.")
            else:
                with st.spinner("Simulating negotiation via backend…"):
                    ok, resp = robust_post_json(
                        NEGOTIATE_ENDPOINT,
                        {"clause": clause_in, "position": counter_pos},
                        timeout=90,
                    )
                if not ok:
                    st.error("Negotiation failed.")
                    st.code(str(resp))
                else:
                    payload = resp.get("result", resp)
                    st.session_state.negotiation_history.insert(
                        0,
                        {
                            "time": datetime.utcnow().isoformat(),
                            "clause": clause_in,
                            "position": counter_pos,
                            "result": payload,
                        },
                    )
                    st.success("Negotiation simulated successfully.")

        if not st.session_state.negotiation_history:
            st.info("No negotiation runs yet. Fill in details and click *Simulate Negotiation*.")
        else:
            latest = st.session_state.negotiation_history[0]
            payload = latest["result"]

            st.markdown("**Context**")
            st.write(f"- **Clause:** {latest['clause']}")
            st.write(f"- **Counterparty position:** {latest['position']}")
            st.markdown("---")

            if isinstance(payload, dict):
                dialogue = payload.get("negotiation") or payload.get("dialogue")
                revision = payload.get("revised_clause") or payload.get(
                    "mutually_beneficial_revision"
                )
                justification = (
                    payload.get("justification")
                    or payload.get("win_win_justification")
                    or payload.get("win-win")
                )

                if dialogue:
                    st.markdown("### Simulated Negotiation")
                    for turn in dialogue:
                        st.markdown(f"- {turn}")

                if revision:
                    st.markdown("### Proposed Revised Clause")
                    st.markdown(revision)

                if justification:
                    st.markdown("### Justification (Win–Win Rationale)")
                    st.markdown(justification)
            else:
                st.markdown("### Negotiation Output")
                st.markdown(str(payload))

        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Mediation Agent":
    st.header("🕊️ Mediation Agent")
    st.markdown(
        "<span class='label-muted'>Enter both parties’ statements and get a neutral summary, interests, evaluation and compromise, inspired by Kenyan ADR practice.</span>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        a = st.text_area("Party A statement", height=180)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        b = st.text_area("Party B statement", height=180)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    mediate_btn = st.button("🕊️ Run Mediation")

    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    if mediate_btn:
        if not a.strip() or not b.strip():
            st.error("Please provide both Party A and Party B statements.")
        else:
            with st.spinner("Running mediation via backend…"):
                ok, resp = robust_post_json(MEDIATE_ENDPOINT, {"a": a, "b": b}, timeout=90)
            if not ok:
                st.error("Mediation failed or backend non-JSON response.")
                st.code(str(resp))
            else:
                st.success("Mediation result")
                payload = resp.get("result", resp)

                if isinstance(payload, dict) and "result" in payload:
                    payload = payload["result"]

                import json

                if isinstance(payload, str):
                    try:
                        parsed = json.loads(payload)
                        payload = parsed
                    except Exception:
                        pass

                if isinstance(payload, dict):
                    neutral = payload.get("neutral_summary")
                    int_a = payload.get("interests_party_a")
                    int_b = payload.get("interests_party_b")
                    evaluation = payload.get("evaluation")
                    compromise = payload.get("proposed_compromise")

                    if neutral:
                        st.markdown("**Neutral Summary**")
                        st.markdown(neutral)

                    if int_a:
                        st.markdown("**Interests — Party A**")
                        for x in _maybe_to_list(int_a):
                            st.markdown(f"- {x}")

                    if int_b:
                        st.markdown("**Interests — Party B**")
                        for x in _maybe_to_list(int_b):
                            st.markdown(f"- {x}")

                    if evaluation:
                        st.markdown("**Objective Evaluation**")
                        st.markdown(evaluation)

                    if compromise:
                        st.markdown("**Proposed Compromise**")
                        st.markdown(compromise)
                else:
                    st.markdown(str(payload))
    else:
        st.caption("Mediation result will appear here after you click *Run Mediation*.")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Past Analyses":
    st.header("📚 Past Analyses (this session)")
    if not st.session_state.past_analyses:
        st.info("No past analyses saved in this session. Run a contract analysis first.")
    else:
        for idx, entry in enumerate(st.session_state.past_analyses):
            with st.expander(
                f"{idx+1}. {entry['filename']} • {entry['timestamp']}",
                expanded=(idx == 0),
            ):
                st.markdown("**Contract preview (first 800 chars)**")
                st.write(entry["contract_text"][:800])
                st.markdown("---")
                st.markdown("**Full JSON result**")
                st.json(entry["results"])
                st.download_button(
                    "Download analysis JSON",
                    data=str(entry["results"]),
                    file_name=f"past_analysis_{idx+1}.json",
                    mime="application/json",
                )

elif page == "Feedback":
    st.header("💬 Feedback")
    st.markdown(
        "<span class='label-muted'>Help improve the Kenyan contract reasoning engine. Your feedback is stored via the backend.</span>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    username = st.text_input("Your name (optional)")
    rating = st.slider("Rating", min_value=1, max_value=5, value=5)
    comments = st.text_area("Comments / Suggestions", height=160)

    if st.button("📨 Submit Feedback", type="primary"):
        if not comments.strip():
            st.error("Please add some feedback text.")
        else:
            with st.spinner("Submitting feedback to backend…"):
                ok, resp = robust_post_json(
                    FEEDBACK_ENDPOINT,
                    {
                        "username": username or "Anonymous",
                        "rating": rating,
                        "comments": comments,
                    },
                    timeout=30,
                )
            if not ok:
                st.error("Failed to send feedback.")
                st.code(str(resp))
            else:
                st.success("Thank you! Your feedback has been recorded.")
                st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Settings":
    st.header("⚙️ Settings & Diagnostics")
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.markdown(f"- **Backend URL:** `{BACKEND_URL}`")
    st.markdown(
        f"- **ReportLab available for PDF export:** "
        f"{'✅ Yes' if REPORTLAB_AVAILABLE else '❌ No'}"
    )
    st.markdown(
        "- **Tip:** Run `streamlit run frontend/ui.py` from your repo root so imports resolve correctly."
    )
    st.markdown(
        "- **Note:** This UI expects the FastAPI backend to be running with `uvicorn backend.server:app --reload`."
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='footer-text'>Built with ❤️ by Stella Gituire • AI Legal Negotiation & Mediation Agent (Kenya Edition)</div>",
    unsafe_allow_html=True,
)
