import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import streamlit as st
import requests
import json
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI-Assisted Claim Description Generator – Insurance Description Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Merriweather:wght@400;700&display=swap');

/* Global */
html, body, [class*="css"] { font-family: 'Merriweather', Georgia, serif; }
.stApp { background-color: #e6f2ff; color: #0f172a; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #dbeafe !important;
    border-right: 1px solid #93c5fd;
    display: none !important;
}
            section[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Header */
.header-box {
    background: linear-gradient(135deg, #bfdbfe, #dbeafe);
    border: 1px solid #93c5fd;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 28px;
}
.header-box h1 { color: #1e3a8a; }
.header-box p  { color: #1d4ed8; }

/* Result Container */
.result-wrapper {
    background: #f0f9ff;
    border: 1px solid #93c5fd;
    border-radius: 12px;
    padding: 24px;
    margin-top: 20px;
}

/* Fields */
.field-box {
    background: #ffffff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.field-box.flagged {
    border-color: #f59e0b !important;
    background: #fef3c7 !important;
}
.field-label { color: #1d4ed8; }
.field-value { color: #0f172a; }

/* Badges */
.badge-blue  { background:#dbeafe; color:#1d4ed8; border:1px solid #93c5fd; }
.badge-green { background:#dcfce7; color:#15803d; border:1px solid #22c55e; }
.badge-amber { background:#fef3c7; color:#b45309; border:1px solid #f59e0b; }
.badge-red   { background:#fee2e2; color:#b91c1c; border:1px solid #ef4444; }

/* Chips */
.chip {
    background: #e0f2fe;
    color: #0369a1;
    border: 1px solid #7dd3fc;
}

/* Inputs */
div[data-baseweb="textarea"] textarea,
div[data-baseweb="input"] input {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border-color: #93c5fd !important;
}

/* Labels */
label {
    color: #1e3a8a !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #60a5fa) !important;
    color: white !important;
}

.stDownloadButton > button {
    background: #dbeafe !important;
    color: #1d4ed8 !important;
    border: 1px solid #93c5fd !important;
}

/* Divider */
hr { border-color: #93c5fd !important; }

</style>
""", unsafe_allow_html=True)

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert insurance claim description generator.
Take raw unstructured input from insurance adjusters and produce a clear, standardized,
professional claim description.

IMPORTANT: Respond ONLY with a valid JSON object. No markdown, no explanation, no backticks.

Output this exact JSON:
{
  "claimTitle": "Short title summarizing the claim",
  "claimType": "Auto / Property / Health / Liability / Other",
  "incidentDate": "Extracted date or Not specified",
  "partiesInvolved": "Names and roles mentioned or Not specified",
  "incidentSummary": "2-3 sentence factual summary of what happened",
  "damageDescription": "Detailed description of damages or injuries",
  "liabilityNotes": "Any noted liability, fault, or contributing factors",
  "recommendedActions": "Suggested next steps for the adjuster",
  "confidenceScore": "High or Medium or Low",
  "flaggedFields": ["list of field keys needing human review"]
}"""

# ─── Session State ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ LiteLLM Settings")
    st.markdown("---")
    api_base   = st.text_input("API Base URL",      value="inpt" )
    api_key    = st.text_input("API Key ",          value="inpit")
    model      = st.text_input("Model Name",        value="genailab-maas-gpt-4o")
    max_tokens = st.slider("Max Tokens", 500, 2000, 1000, 100)

    st.markdown("---")
    st.markdown("""
<div style='font-family:IBM Plex Mono,monospace;font-size:11px;color:#475569;line-height:1.9;'>
<b style='color:#3b82f6;'>TCS AI Fridays – Season 2</b><br>
AI-Assisted Claim Description<br>
Generator for Insurance Adjusters<br><br>
① Configure LiteLLM above<br>
② Paste raw claim data<br>
③ Click Generate<br>
④ Review &amp; export
</div>""", unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### 🕘 Recent Claims")
        for h in reversed(st.session_state.history[-6:]):
            st.markdown(f"""
<div class='hist-card'>
  <div class='hist-title'>{h['title'][:40]}{'…' if len(h['title'])>40 else ''}</div>
  <div class='hist-meta'>{h['type']} · {h['time']}</div>
</div>""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class='header-box'>
  <h1>⚖️ AI-Assisted Claim Description Generator</h1>
  <p>AI-Assisted Insurance Claim Description Generator · Powered by LiteLLM</p>
</div>
""", unsafe_allow_html=True)

# ─── Input ────────────────────────────────────────────────────────────────────
st.markdown("<span class='section-num'>01 &nbsp;</span>**Raw Claim Input**", unsafe_allow_html=True)
st.caption("Paste customer statements, incident notes, police reports, or any unstructured claim data below.")

raw_input = st.text_area(
    label="Raw Input",
    label_visibility="collapsed",
    height=200,
    placeholder=(
        "Example: Customer John Doe reported on March 5th that while parked on Oak Street, "
        "his 2019 Honda Civic was struck by an unidentified vehicle. "
        "Left rear bumper dented, tail light cracked. No witnesses. Police report #2024-1123."
    ),
)

col1, col2, _ = st.columns([2, 1, 3])
with col1:
    generate_btn = st.button("✦ Generate Claim Description", use_container_width=True)
with col2:
    if st.button("✕ Clear", use_container_width=True):
        st.session_state.result = None
        st.rerun()

# ─── API Call ─────────────────────────────────────────────────────────────────
def generate_pdf(result):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("INSURANCE CLAIM DESCRIPTION", styles["Title"]))
    content.append(Spacer(1, 10))

    fields = [
        ("Claim Title", result.get("claimTitle","")),
        ("Claim Type", result.get("claimType","")),
        ("Incident Date", result.get("incidentDate","")),
        ("Parties Involved", result.get("partiesInvolved","")),
        ("Incident Summary", result.get("incidentSummary","")),
        ("Damage Description", result.get("damageDescription","")),
        ("Liability Notes", result.get("liabilityNotes","")),
        ("Recommended Actions", result.get("recommendedActions","")),
        ("Confidence Score", result.get("confidenceScore","")),
        ("Flagged Fields", ", ".join(result.get("flaggedFields",[])) or "None"),
    ]

    for title, value in fields:
        content.append(Paragraph(f"<b>{title}:</b> {value}", styles["Normal"]))
        content.append(Spacer(1, 8))

    doc.build(content)
    buffer.seek(0)
    return buffer
####

def call_litellm(text):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Generate a standardized claim description from this raw input:\n\n{text}"},
        ],
    }
    resp = requests.post(
        f"{api_base.rstrip('/')}/chat/completions",
        headers=headers, json=payload, timeout=60,verify=False,
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(raw)


if generate_btn:
    if not raw_input.strip():
        st.warning("⚠️  Please enter some claim input data before generating.")
    else:
        with st.spinner("🔄  Analyzing claim data with LiteLLM..."):
            try:
                result = call_litellm(raw_input)
                st.session_state.result = result
                st.session_state.history.append({
                    "title":  result.get("claimTitle", "Untitled"),
                    "type":   result.get("claimType", "Unknown"),
                    "time":   datetime.now().strftime("%H:%M:%S"),
                    "result": result,
                })
                st.success("✅  Claim description generated successfully!")
            except requests.exceptions.ConnectionError:
                st.error(f"❌  Cannot connect to `{api_base}`. Is your LiteLLM proxy running?")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌  API Error {e.response.status_code}: {e.response.text[:400]}")
            except json.JSONDecodeError:
                st.error("❌  Model response was not valid JSON. Try a different model or check SYSTEM_PROMPT.")
            except Exception as e:
                st.error(f"❌  Unexpected error: {e}")

# ─── Results ──────────────────────────────────────────────────────────────────
result = st.session_state.result

if result:
    st.markdown("---")
    st.markdown("<span class='section-num'>02 &nbsp;</span>**Generated Claim Description**", unsafe_allow_html=True)
    st.caption("Structured output from the AI. Review flagged fields before exporting.")

    conf        = result.get("confidenceScore", "Medium")
    ctype       = result.get("claimType", "Unknown")
    flags       = result.get("flaggedFields", [])
    badge_conf  = {"High": "badge-green", "Low": "badge-red"}.get(conf, "badge-amber")
    flag_html   = "".join(f"<span class='chip'>⚑ {f}</span>" for f in flags) \
                  if flags else "<span style='color:#475569;font-size:12px;font-family:IBM Plex Mono,monospace;'>None — no fields need review</span>"

    def fb(key):
        return "flagged" if key in flags else ""

    st.markdown(f"""
<div class='result-wrapper'>

  <!-- Top bar -->
  <div style='display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:20px;'>
    <span class='badge badge-blue'>📋 {ctype}</span>
    <span class='badge {badge_conf}'>● {conf} Confidence</span>
    <span style='font-family:IBM Plex Mono,monospace;font-size:11px;color:#475569;margin-left:auto;'>
      {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </span>
  </div>

  <!-- Title -->
  <div class='field-box'>
    <div class='field-label'>Claim Title</div>
    <div class='field-value' style='font-size:18px;font-weight:700;color:#1e3a8a;'>
      {result.get("claimTitle","—")}
    </div>
  </div>

  <!-- Date + Parties row -->
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;'>
    <div class='field-box {fb("incidentDate")}'>
      <div class='field-label'>📅 Incident Date {"⚑" if "incidentDate" in flags else ""}</div>
      <div class='field-value'>{result.get("incidentDate","—")}</div>
    </div>
    <div class='field-box {fb("partiesInvolved")}'>
      <div class='field-label'>👥 Parties Involved {"⚑" if "partiesInvolved" in flags else ""}</div>
      <div class='field-value'>{result.get("partiesInvolved","—")}</div>
    </div>
  </div>

  <!-- Summary -->
  <div class='field-box {fb("incidentSummary")}'>
    <div class='field-label'>📝 Incident Summary {"⚑" if "incidentSummary" in flags else ""}</div>
    <div class='field-value'>{result.get("incidentSummary","—")}</div>
  </div>

  <!-- Damage -->
  <div class='field-box {fb("damageDescription")}'>
    <div class='field-label'>🔧 Damage Description {"⚑" if "damageDescription" in flags else ""}</div>
    <div class='field-value'>{result.get("damageDescription","—")}</div>
  </div>

  <!-- Liability + Actions row -->
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>
    <div class='field-box {fb("liabilityNotes")}'>
      <div class='field-label'>⚖️ Liability Notes {"⚑" if "liabilityNotes" in flags else ""}</div>
      <div class='field-value'>{result.get("liabilityNotes","—")}</div>
    </div>
    <div class='field-box {fb("recommendedActions")}'>
      <div class='field-label'>✅ Recommended Actions {"⚑" if "recommendedActions" in flags else ""}</div>
      <div class='field-value'>{result.get("recommendedActions","—")}</div>
    </div>
  </div>

  <!-- Flagged fields -->
  <div class='field-box' style='margin-top:12px;'>
    <div class='field-label'>⚑ Fields Flagged for Human Review</div>
    <div style='margin-top:6px;'>{flag_html}</div>
  </div>

</div>
""", unsafe_allow_html=True)

    # ─── Export ───────────────────────────────────────────────────────────────
    st.markdown("#### 📤 Export")
    ##ec1, ec2, _ = st.columns([1, 1, 2])
    ec1, ec2, ec3 = st.columns([1, 1, 1])


    plain = "\n".join([
        "=" * 60,
        "INSURANCE CLAIM DESCRIPTION",
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        f"Claim Title       : {result.get('claimTitle','')}",
        f"Claim Type        : {result.get('claimType','')}",
        f"Incident Date     : {result.get('incidentDate','')}",
        f"Parties Involved  : {result.get('partiesInvolved','')}",
        "-" * 60,
        f"INCIDENT SUMMARY\n{result.get('incidentSummary','')}",
        "-" * 60,
        f"DAMAGE DESCRIPTION\n{result.get('damageDescription','')}",
        "-" * 60,
        f"LIABILITY NOTES\n{result.get('liabilityNotes','')}",
        "-" * 60,
        f"RECOMMENDED ACTIONS\n{result.get('recommendedActions','')}",
        "-" * 60,
        f"Confidence Score  : {result.get('confidenceScore','')}",
        f"Flagged Fields    : {', '.join(result.get('flaggedFields',[])) or 'None'}",
        "=" * 60,
    ])
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    with ec1:
        st.download_button("⬇️ Download .txt",  plain,
                           file_name=f"claim_{ts}.txt", mime="text/plain",
                           use_container_width=True)
    with ec2:
        st.download_button("⬇️ Download .json", json.dumps(result, indent=2),
                           file_name=f"claim_{ts}.json", mime="application/json",
                           use_container_width=True)
    
        use_container_width=True
        pdf_file = generate_pdf(result)

    with ec3:
        st.download_button(
            "⬇️ Download PDF",
            pdf_file,
            file_name=f"claim_{ts}.pdf",
            mime="application/pdf",
            use_container_width=True
    )
    with st.expander("🔍 View Raw JSON"):
        st.json(result)

else:
    if not generate_btn:
        st.markdown("""
<div style='text-align:center;padding:70px 0;'>
  <div style='font-size:52px;margin-bottom:16px;'>⚖️</div>
  <div style='font-family:IBM Plex Mono,monospace;font-size:12px;
              color:#334155;letter-spacing:0.12em;'>
    CONFIGURE LITELLM · PASTE CLAIM DATA · CLICK GENERATE
  </div>
</div>""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;font-family:IBM Plex Mono,monospace;
            font-size:11px;color:#1e2d3d;letter-spacing:0.1em;padding:6px 0;'>
  TCS AI FRIDAYS SEASON 2 · AI-Assisted Claim Description Generator · POWERED BY LITELLM
</div>""", unsafe_allow_html=True)
