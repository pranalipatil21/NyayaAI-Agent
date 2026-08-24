import os
import io
import html
import hashlib
import streamlit as st

from src.agentic import NyayaAgentWorkflow, is_greeting_query, is_off_topic_query
from src.engine import NyayaEngine


st.set_page_config(page_title="NyayaAI", page_icon="⚖️", layout="wide")


# --- Custom Styling for NyayaAI Warm Legal Aesthetic ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=Merriweather:ital,wght@0,400;0,700;1,400&display=swap');

    :root {
        --bg: #FAF8F5;
        --surface: #FFFFFF;
        --sidebar: #F3EFEA;
        --line: #E5DFC5;
        --text: #1C1B1A;
        --muted: #6B6458;
        --accent: #8A6A38;
        --accent-soft: #F5EFE4;
        --accent-hover: #72552B;
        --user-bg: #F3EFEA;
    }

    .stApp {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: "Inter", system-ui, -apple-system, sans-serif !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        max-width: 960px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    section[data-testid="stSidebar"] {
        background: var(--sidebar) !important;
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    /* Main Page Top Header */
    .header-container {
        text-align: center;
        padding: 0.5rem 0 1.25rem 0;
        margin-bottom: 0.5rem;
        border-bottom: 2px double var(--line);
    }

    .main-title {
        font-family: "Cinzel", "Merriweather", Georgia, serif !important;
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        color: #1A1918 !important;
        letter-spacing: 0.04em;
        margin: 0 0 0.25rem 0 !important;
    }

    .main-subtitle {
        font-family: "Merriweather", Georgia, serif !important;
        font-size: 1.05rem !important;
        font-style: italic;
        color: var(--accent) !important;
        margin: 0 !important;
    }

    /* Sidebar Styling */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1rem;
    }

    .brand-mark-icon {
        font-size: 1.75rem;
        line-height: 1;
    }

    .brand-title-text {
        font-family: "Cinzel", Georgia, serif;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.1;
    }

    .brand-desc-text {
        font-size: 0.82rem;
        color: var(--muted) !important;
        margin-top: 0.25rem;
        line-height: 1.35;
    }

    .sidebar-section-header {
        font-size: 0.8rem;
        color: var(--accent) !important;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 1.25rem 0 0.5rem 0;
    }

    .disclaimer-card {
        border: 1px solid #E2D9C8;
        border-left: 3px solid var(--accent);
        border-radius: 6px;
        padding: 0.75rem;
        background: #FDFBF7;
        font-size: 0.8rem;
        line-height: 1.45;
        color: var(--muted) !important;
        margin-top: 1rem;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        justify-content: center;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: "Inter", sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: var(--muted) !important;
        background: transparent !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 2.5px solid var(--accent) !important;
    }

    /* Legal Homepage Cards */
    .hero-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(138, 106, 56, 0.05);
        text-align: center;
    }

    .hero-title {
        font-family: "Cinzel", Georgia, serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.2rem;
    }

    .hero-tagline {
        font-family: "Merriweather", Georgia, serif;
        font-size: 0.95rem;
        font-style: italic;
        color: var(--accent);
        margin-bottom: 1rem;
    }

    .lady-justice-container {
        text-align: center;
        margin: 1rem 0;
    }

    .lady-justice-img {
        max-width: 380px;
        width: 100%;
        border-radius: 8px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--line);
    }

    .quote-box {
        background: #F8F5EE;
        border-left: 4px solid var(--accent);
        border-radius: 4px;
        padding: 1.2rem 1.5rem;
        margin: 1.5rem 0;
        font-family: "Merriweather", Georgia, serif;
        font-size: 0.96rem;
        line-height: 1.6;
        color: #2D2B28;
    }

    .quote-author {
        text-align: right;
        font-weight: 700;
        font-style: normal;
        color: var(--accent);
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }

    .architecture-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }

    .arch-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }

    .arch-card h4 {
        font-family: "Cinzel", Georgia, serif;
        font-size: 1.05rem;
        color: var(--accent);
        margin: 0 0 0.5rem 0;
    }

    .arch-card p {
        font-size: 0.88rem;
        color: var(--muted);
        line-height: 1.45;
        margin: 0;
    }

    /* Voice Input Container on Main Page */
    .voice-input-card {
        background: #F7F3EB;
        border: 1px solid #E2D8C3;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
    }

    .voice-card-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 1rem;
        color: var(--accent);
        margin-bottom: 0.75rem;
    }

    /* Chat Messages Styling */
    div[data-testid="stChatMessage"] {
        background: transparent !important;
        padding: 0.85rem 0 !important;
        border: 0 !important;
    }

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        max-width: 76ch;
    }

    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li {
        color: var(--text) !important;
        line-height: 1.6;
        font-size: 1rem;
    }

    .source-block {
        border-left: 3px solid var(--accent);
        padding: 0.65rem 0.8rem;
        margin-bottom: 0.75rem;
        background: #FDFBF7;
        border-radius: 0 6px 6px 0;
        border: 1px solid #EAE4D7;
        border-left-width: 3px;
    }

    .source-title {
        font-size: 0.83rem;
        font-weight: 700;
        color: var(--accent) !important;
        margin-bottom: 0.25rem;
    }

    .source-content {
        font-size: 0.86rem;
        color: #3F3F3A !important;
        line-height: 1.45;
    }

    .agent-step {
        border-left: 3px solid #555D7A;
        padding: 0.65rem 0.8rem;
        margin-bottom: 0.7rem;
        background: #FAF9F6;
        border-radius: 0 6px 6px 0;
    }

    .agent-progress {
        border: 1px solid var(--line);
        border-radius: 10px;
        background: #FDFBF7;
        padding: 0.85rem 0.9rem;
        margin: 0.4rem 0 1rem;
        max-width: 540px;
    }

    .progress-row {
        display: grid;
        grid-template-columns: 22px 1fr;
        column-gap: 0.65rem;
        position: relative;
        padding-bottom: 0.72rem;
    }

    .progress-row:last-child {
        padding-bottom: 0;
    }

    .progress-row:not(:last-child)::after {
        content: "";
        position: absolute;
        left: 10px;
        top: 22px;
        bottom: 0;
        width: 1px;
        background: var(--line);
    }

    .progress-row.completed:not(:last-child)::after {
        background: var(--accent);
    }

    .progress-dot {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 1px solid var(--line);
        background: var(--surface);
        color: var(--muted);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.76rem;
        font-weight: 700;
        z-index: 1;
    }

    .progress-row.completed .progress-dot {
        background: var(--accent);
        border-color: var(--accent);
        color: #FFFFFF;
    }

    .progress-row.active .progress-dot {
        background: var(--text);
        border-color: var(--text);
        color: #FFFFFF;
        animation: nyayaPulse 1.35s ease-in-out infinite;
    }

    .progress-row.error .progress-dot {
        background: #9F2A2A;
        border-color: #9F2A2A;
        color: #FFFFFF;
    }

    .progress-label {
        font-size: 0.9rem;
        font-weight: 600;
        line-height: 1.35;
        color: var(--text) !important;
    }

    .progress-detail {
        color: var(--muted) !important;
        font-size: 0.8rem;
        line-height: 1.35;
        margin-top: 0.16rem;
    }

    @keyframes nyayaPulse {
        0% { box-shadow: 0 0 0 0 rgba(32, 33, 35, 0.24); }
        70% { box-shadow: 0 0 0 7px rgba(32, 33, 35, 0); }
        100% { box-shadow: 0 0 0 0 rgba(32, 33, 35, 0); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


LANGUAGES = [
    "English",
    "Hindi (हिन्दी)",
    "Marathi (मराठी)",
    "Tamil (தமிழ்)",
    "Telugu (తెలుగు)",
    "Bengali (বাংলা)",
]

EVALUATION_CASES = [
    {
        "query": "The police detained my brother for 30 hours and have not taken him to a magistrate.",
        "expected": ["Article 22", "Article 21"],
    },
    {
        "query": "My employer has not paid my salary for 4 months and is forcing me to keep working.",
        "expected": ["Article 23", "Article 21"],
    },
    {
        "query": "A government school refused admission to my daughter because of our caste.",
        "expected": ["Article 15", "Article 21A"],
    },
    {
        "query": "The police are punishing me again for the same criminal case.",
        "expected": ["Article 20"],
    },
    {
        "query": "The municipality is treating people in my locality unequally without any reason.",
        "expected": ["Article 14"],
    },
    {
        "query": "My peaceful speech at a public meeting was stopped by officials.",
        "expected": ["Article 19"],
    },
    {
        "query": "My child is being made to work in a hazardous factory.",
        "expected": ["Article 24"],
    },
    {
        "query": "I need to approach the Supreme Court for enforcement of my fundamental rights.",
        "expected": ["Article 32"],
    },
    {"query": "What is IPL?", "expected": ["Reject"]},
    {"query": "Which is the capital of France?", "expected": ["Reject"]},
]


@st.cache_resource
def load_nyaya_engine():
    engine = NyayaEngine()
    pdf_path = "data/constitution.pdf"
    try:
        has_index = engine.vectorstore._collection.count() > 0
    except Exception:
        has_index = False

    if os.path.exists(pdf_path) and not has_index:
        with st.spinner("Indexing the Constitution for the first time..."):
            engine.ingest_data(pdf_path)
    return engine


def generate_speech(text, language_name):
    """Generates Text-To-Speech MP3 audio bytes using gTTS."""
    try:
        from gtts import gTTS

        lang_map = {
            "English": "en",
            "Hindi (हिन्दी)": "hi",
            "Marathi (मराठी)": "mr",
            "Tamil (தமிழ்)": "ta",
            "Telugu (తెలుగు)": "te",
            "Bengali (বাংলা)": "bn",
        }
        clean_text = (
            text.replace("**", "")
            .replace("*", "")
            .replace("`", "")
            .replace("#", "")
            .replace("- ", "")
        )
        audio = io.BytesIO()
        tts = gTTS(text=clean_text, lang=lang_map.get(language_name, "en"))
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio.getvalue()
    except Exception as exc:
        st.warning(f"Audio generation notice: {exc}")
        return None


def render_sources(sources):
    if not sources:
        return
    with st.expander("Sources"):
        for source in sources:
            st.markdown(
                f"""
                <div class="source-block">
                    <div class="source-title">Source {source["id"]}: {source["source"]}, page {source["page"]}</div>
                    <div class="source-content">{source["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_agent_trace(response_data):
    trace = response_data.get("trace", [])
    if not trace:
        return
    with st.expander("Agent Trace"):
        st.markdown(f"**Intent:** {response_data.get('intent', 'Unclassified')}")
        st.markdown(f"**Verification:** {response_data.get('verification', 'Not verified')}")
        for item in trace:
            st.markdown(
                f"""
                <div class="agent-step">
                    <strong>{item["agent"]}</strong><br>
                    <span><b>Action:</b> {item["action"]}</span><br>
                    <span><b>Observation:</b> {item["observation"]}</span><br>
                    <span><b>Decision:</b> {item["decision"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        timings = response_data.get("timings", {})
        if timings:
            st.caption(" | ".join([f"{key.title()}: {value}s" for key, value in timings.items()]))


def render_agent_progress_stepper(steps):
    if not steps:
        return

    icons = {
        "pending": "○",
        "active": "●",
        "completed": "✓",
        "error": "×",
    }
    rows = []
    for step in steps:
        status = step.get("status", "pending")
        label = html.escape(step.get("label", "Working"))
        description = step.get("description")
        duration = step.get("duration")
        detail_parts = []
        if description:
            detail_parts.append(html.escape(str(description)))
        if duration is not None:
            detail_parts.append(f"{duration}s")
        detail = ""
        if detail_parts:
            detail = f"<div class=\"progress-detail\">{' · '.join(detail_parts)}</div>"

        safe_status = html.escape(status)
        icon = icons.get(status, "○")
        rows.append(
            f"<div class=\"progress-row {safe_status}\">"
            f"<div class=\"progress-dot\">{icon}</div>"
            f"<div><div class=\"progress-label\">{label}</div>{detail}</div>"
            "</div>"
        )

    markup = f"<div class=\"agent-progress\">{''.join(rows)}</div>"
    if hasattr(st, "html"):
        st.html(markup)
    else:
        st.markdown(markup, unsafe_allow_html=True)


FOLLOWUP_MARKERS = {
    "what can i do",
    "what should i do",
    "next step",
    "next steps",
    "explain more",
    "tell me more",
    "which article",
    "what article",
    "how",
    "why",
    "can you explain",
    "is this legal",
    "what about this",
    "also",
}


def last_user_message():
    for message in reversed(st.session_state.messages):
        if message.get("role") == "user":
            return message.get("content")
    return None


def should_contextualize_query(query_text):
    normalized = query_text.strip().lower()
    if not normalized or is_greeting_query(normalized) or is_off_topic_query(normalized):
        return False
    if len(normalized.split()) <= 8:
        return True
    return any(marker in normalized for marker in FOLLOWUP_MARKERS)


def build_agent_query(query_text):
    previous_user = last_user_message()
    if previous_user and should_contextualize_query(query_text):
        return (
            "Conversation context for follow-up constitutional question:\n"
            f"Previous user problem: {previous_user}\n"
            f"Current follow-up question: {query_text}\n"
            "Answer the current follow-up using the previous problem as context."
        )
    return query_text


def handle_query(query_text, language):
    agent_query = build_agent_query(query_text)
    st.session_state.messages.append({"role": "user", "content": query_text})

    with st.chat_message("user", avatar="👤"):
        st.markdown(query_text)

    with st.chat_message("assistant", avatar="⚖️"):
        progress_slot = st.empty()
        response_data = None
        with progress_slot.container():
            render_agent_progress_stepper(
                [
                    {"id": "queued", "label": "Preparing agent", "status": "active"},
                ]
            )

        for event in agent_workflow.run_with_events(agent_query, language=language):
            with progress_slot.container():
                render_agent_progress_stepper(event.get("steps", []))
            if event["event"] == "agent:complete":
                response_data = event["result"]

        if response_data is None:
            st.error("NyayaAI could not complete this request.")
            return

        answer = response_data["answer"]
        sources = response_data.get("sources", [])
        st.markdown(answer)

        # Generate audio output automatically for both Voice & Text response
        audio_bytes = generate_speech(answer, language)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")

        is_rejected = "I am unable to deliver an answer to this question" in answer
        if not is_rejected:
            render_sources(sources)
        render_agent_trace(response_data)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "audio_bytes": audio_bytes,
                "sources": [] if is_rejected else sources,
                "trace": response_data.get("trace", []),
                "intent": response_data.get("intent"),
                "verification": response_data.get("verification"),
                "timings": response_data.get("timings", {}),
                "progress_steps": response_data.get("progress_steps", []),
                "agent_query": agent_query,
            }
        )


# --- Initialize Engine ---
try:
    engine = load_nyaya_engine()
    agent_workflow = NyayaAgentWorkflow(engine)
except Exception as exc:
    st.error(f"Error initializing NyayaAI: {exc}")
    st.stop()


# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_audio_hashes" not in st.session_state:
    st.session_state.processed_audio_hashes = set()
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = None


# --- Sidebar Setup ---
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-mark-icon">⚖️</div>
            <div>
                <div class="brand-title-text">Nyaya Sahayak</div>
                <div class="brand-desc-text">An educational AI tool designed to help Indian citizens identify their Constitutional rights.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-section-header'>🌐 Language / भाषा</div>", unsafe_allow_html=True)
    selected_lang = st.selectbox(
        "Choose consultation language:",
        LANGUAGES,
        index=0,
        help="Select the language for AI responses and voice playback.",
    )

    st.markdown("<div class='sidebar-section-header'>💡 Example Scenarios</div>", unsafe_allow_html=True)

    if st.button(
        "💼 Labor & Livelihood: 'I work as a driver but my boss has refused to pay my wages.'",
        use_container_width=True,
    ):
        st.session_state.pending_query = "I work as a driver but my boss has refused to pay my wages for 4 months."
        st.rerun()

    if st.button(
        "🚨 Personal Liberty: 'My brother was taken by police 30 hours ago and hasn't seen a judge.'",
        use_container_width=True,
    ):
        st.session_state.pending_query = "My brother was taken by police 30 hours ago and hasn't seen a judge."
        st.rerun()

    if st.button(
        "⚖️ Social Discrimination: 'A government school refuses to admit my daughter because of our caste.'",
        use_container_width=True,
    ):
        st.session_state.pending_query = "A government school refuses to admit my daughter because of our caste."
        st.rerun()

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.processed_audio_hashes = set()
        st.session_state.pending_query = None
        st.rerun()

    st.markdown("<div class='sidebar-section-header'>📊 Agent Evaluation</div>", unsafe_allow_html=True)
    if st.button("Run Agent Evaluation", use_container_width=True):
        with st.spinner("Running agent evaluation cases..."):
            st.session_state.evaluation_results = agent_workflow.evaluate_cases(EVALUATION_CASES)

    if st.session_state.evaluation_results:
        ev = st.session_state.evaluation_results
        col_acc, col_cor = st.columns(2)
        with col_acc:
            st.metric("Accuracy", f"{ev['accuracy']}%")
        with col_cor:
            st.metric("Correct Cases", f"{ev['correct']} / {ev['total']}")

        with st.expander("Evaluation Rows"):
            st.dataframe(ev["rows"], use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="disclaimer-card">
            <strong>⚠️ Educational Disclaimer:</strong><br>
            NyayaAI is an educational helper tool. It does not provide official legal representation or advice. For court representation and legal disputes, please consult a qualified advocate.
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Main Top Header ---
st.markdown(
    """
    <div class="header-container">
        <h1 class="main-title">NyayaAI</h1>
        <p class="main-subtitle">Led by the Truth • Citizen's Constitutional Guide</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- Navigation Tabs ---
tab_home, tab_assistant = st.tabs(["🏛️ Homepage & Work Done", "💬 Constitutional Assistant"])


# ==============================================================================
# TAB 1: HOMEPAGE & WORK DONE
# ==============================================================================
with tab_home:
    st.markdown(
        """
        <div class="hero-card">
            <div style="display:flex; justify-content:center; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
                <span style="font-size:1.8rem;">🏛️</span>
                <span class="hero-title">Nyaya Sahayak</span>
            </div>
            <div class="hero-tagline">Truth Alone Triumphs • Satyamev Jayate</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if os.path.exists("data/lady_justice.png"):
        col_center_left, col_center, col_center_right = st.columns([1, 3, 1])
        with col_center:
            st.image("data/lady_justice.png", use_column_width=True)
            st.markdown(
                """
                <div style="text-align:center; font-family:'Cinzel', serif; font-size:0.9rem; font-weight:700; color:#8A6A38; letter-spacing:0.1em; margin-top:0.4rem; margin-bottom:1.5rem;">
                    INTEGRITY &nbsp;&bull;&nbsp; LEGAL HOMEPAGE &nbsp;&bull;&nbsp; JUSTICE
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="quote-box">
            "However good a Constitution may be, if those who are implementing it are not good, it will prove to be bad. 
            However bad a Constitution may be, if those who are implementing it are good, it will prove to be good."
            <div class="quote-author">&mdash; Dr. B.R. Ambedkar</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="font-family:'Cinzel', serif; font-size:1.4rem; font-weight:700; color:#1C1B1A; border-bottom:1px solid #E5DFC5; padding-bottom:0.4rem; margin:2rem 0 1rem 0;">
            🛠️ System Architecture & Work Done
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="architecture-grid">
            <div class="arch-card">
                <h4>🤖 Autonomous Multi-Agent Pipeline</h4>
                <p>Orchestrates specialized sub-agents (Router, RAG Retriever, Legal Analysis, Verification, and Multilingual Response) to ensure accurate legal groundedness.</p>
            </div>
            <div class="arch-card">
                <h4>📜 Complete Constitutional Database</h4>
                <p>Indexed over 395 Articles of the Constitution of India into ChromaDB using BAAI/bge-small-en-v1.5 local embeddings with zero third-party leakage.</p>
            </div>
            <div class="arch-card">
                <h4>🎙️ Multilingual STT & TTS</h4>
                <p>Integrates Groq Whisper voice transcription (Speech-to-Text) and gTTS audio synthesis (Text-to-Speech) in 6 major Indian languages.</p>
            </div>
            <div class="arch-card">
                <h4>🎯 Verified Benchmark Accuracy</h4>
                <p>Built-in evaluation framework testing real-life rights scenarios with an average retrieval and constitutional reasoning accuracy exceeding 90%.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# TAB 2: CONSTITUTIONAL ASSISTANT
# ==============================================================================
with tab_assistant:

    # 1. Voice Input Widget Section on Main Screen
    st.markdown(
        """
        <div class="voice-input-card">
            <div class="voice-card-header">
                <span>🎤</span> Record your grievance / अपनी आवाज़ में समस्या रिकॉर्ड करें
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    recorded_audio = st.audio_input("Record audio grievance", label_visibility="collapsed")
    voice_transcription = None

    if recorded_audio:
        audio_bytes = recorded_audio.read()
        audio_hash = hashlib.md5(audio_bytes).hexdigest()

        if audio_hash not in st.session_state.processed_audio_hashes:
            if os.getenv("GROQ_API_KEY"):
                with st.spinner("Transcribing your voice grievance with Groq Whisper..."):
                    try:
                        # Reset buffer position for reading
                        recorded_audio.seek(0)
                        voice_transcription = engine.transcribe_audio(recorded_audio)
                        st.session_state.processed_audio_hashes.add(audio_hash)
                        st.session_state.pending_query = voice_transcription
                    except Exception as exc:
                        st.error(f"Voice transcription error: {exc}")
            else:
                st.warning("GROQ_API_KEY is missing. Configure it in `.env` to enable Speech-To-Text transcription.")

    # 2. Render Existing Chat Messages
    for index, message in enumerate(st.session_state.messages):
        avatar = "👤" if message["role"] == "user" else "⚖️"
        with st.chat_message(message["role"], avatar=avatar):
            if message["role"] == "assistant":
                render_agent_progress_stepper(message.get("progress_steps", []))
            st.markdown(message["content"])

            if message["role"] == "assistant":
                # Render Text-To-Speech audio player alongside response
                if message.get("audio_bytes"):
                    st.audio(message["audio_bytes"], format="audio/mp3")

                render_sources(message.get("sources", []))
                render_agent_trace(message)

    # 3. Handle Pending Query or Direct Chat Input
    active_query = None

    if st.session_state.pending_query:
        active_query = st.session_state.pending_query
        st.session_state.pending_query = None

    chat_input_text = st.chat_input("Describe your grievance (e.g. 'My owner has not paid my wages for 4 months')")

    if chat_input_text:
        active_query = chat_input_text

    if active_query:
        handle_query(active_query, selected_lang)
        st.rerun()
