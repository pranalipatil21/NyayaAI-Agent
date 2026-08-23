import os
import io
import html

import streamlit as st

from src.agentic import NyayaAgentWorkflow, is_greeting_query, is_off_topic_query
from src.engine import NyayaEngine


st.set_page_config(page_title="NyayaAI", page_icon="⚖️", layout="wide")


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #F7F7F4;
        --surface: #FFFFFF;
        --sidebar: #EFEDE7;
        --line: #DCD8CD;
        --text: #202123;
        --muted: #6F6A61;
        --accent: #8A6A38;
        --accent-soft: #F3EBDD;
        --user: #ECECEC;
    }

    .stApp {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        max-width: 920px;
        padding-top: 1.25rem;
        padding-bottom: 7rem;
    }

    section[data-testid="stSidebar"] {
        background: var(--sidebar) !important;
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    .app-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.25rem 0 1rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1rem;
    }

    .brand-mark {
        width: 36px;
        height: 36px;
        border-radius: 9px;
        background: var(--text);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
    }

    .brand-copy {
        line-height: 1.2;
    }

    .brand-name {
        font-size: 1rem;
        font-weight: 700;
        margin: 0;
    }

    .brand-subtitle {
        color: var(--muted) !important;
        font-size: 0.82rem;
        margin: 0.15rem 0 0;
    }

    .chat-heading {
        text-align: center;
        margin: 9vh auto 2rem;
        max-width: 640px;
    }

    .chat-heading h1 {
        font-size: 2rem;
        line-height: 1.2;
        letter-spacing: 0;
        margin-bottom: 0.55rem;
        color: var(--text) !important;
    }

    .chat-heading p {
        color: var(--muted) !important;
        font-size: 1rem;
        line-height: 1.45;
        margin: 0 auto;
        max-width: 58ch;
    }

    div[data-testid="stChatMessage"] {
        background: transparent !important;
        padding: 0.75rem 0 !important;
        border: 0 !important;
        box-shadow: none !important;
    }

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        max-width: 74ch;
    }

    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stMarkdownContainer"] {
        color: var(--text) !important;
        line-height: 1.55;
    }

    div[data-testid="stChatMessageAvatarUser"] {
        background: var(--user) !important;
    }

    div[data-testid="stChatMessageAvatarAssistant"] {
        background: var(--accent-soft) !important;
    }

    div[data-testid="stChatInput"] {
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: 22px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08) !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: var(--text) !important;
        font-size: 1rem !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: var(--muted) !important;
    }

    .stButton > button {
        border-radius: 8px !important;
        border: 1px solid var(--line) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        background: var(--surface) !important;
        margin-top: 0.75rem !important;
    }

    div[data-testid="stExpander"] summary {
        color: var(--text) !important;
        font-weight: 600 !important;
    }

    .source-block {
        border-left: 3px solid var(--accent);
        padding: 0.65rem 0 0.65rem 0.8rem;
        margin-bottom: 0.75rem;
        background: #FAFAF8;
        border-radius: 0 6px 6px 0;
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
        padding: 0.65rem 0 0.65rem 0.8rem;
        margin-bottom: 0.7rem;
        background: #FAFAF8;
        border-radius: 0 6px 6px 0;
    }

    .helper-text {
        color: var(--muted) !important;
        font-size: 0.86rem;
        line-height: 1.45;
    }

    .sidebar-label {
        font-size: 0.78rem;
        color: var(--muted) !important;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin: 1.1rem 0 0.45rem;
    }

    .disclaimer {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.55);
        font-size: 0.82rem;
        line-height: 1.45;
        color: var(--muted) !important;
    }

    .agent-progress {
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.72);
        padding: 0.85rem 0.9rem;
        margin: 0.4rem 0 1rem;
        max-width: 520px;
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
        font-size: 0.92rem;
        font-weight: 600;
        line-height: 1.35;
        color: var(--text) !important;
        transition: color 160ms ease;
    }

    .progress-row.pending .progress-label {
        color: var(--muted) !important;
        font-weight: 500;
    }

    .progress-row.active .progress-label {
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
    from gtts import gTTS

    lang_map = {
        "English": "en",
        "Hindi (हिन्दी)": "hi",
        "Marathi (मराठी)": "mr",
        "Tamil (தமிழ்)": "ta",
        "Telugu (తెలుగు)": "te",
        "Bengali (বাংলা)": "bn",
    }
    clean_text = text.replace("**", "").replace("*", "").replace("`", "").replace("#", "").replace("- ", "")
    audio = io.BytesIO()
    tts = gTTS(text=clean_text, lang=lang_map.get(language_name, "en"))
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio


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

        col_audio, _ = st.columns([1, 5])
        with col_audio:
            if st.button("Play", key=f"play_latest_{len(st.session_state.messages)}"):
                with st.spinner("Preparing audio..."):
                    st.audio(generate_speech(answer, language), format="audio/mp3")

        is_rejected = "I am unable to deliver an answer to this question" in answer
        if not is_rejected:
            render_sources(sources)
        render_agent_trace(response_data)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": [] if is_rejected else sources,
                "trace": response_data.get("trace", []),
                "intent": response_data.get("intent"),
                "verification": response_data.get("verification"),
                "timings": response_data.get("timings", {}),
                "progress_steps": response_data.get("progress_steps", []),
                "agent_query": agent_query,
            }
        )


try:
    engine = load_nyaya_engine()
    agent_workflow = NyayaAgentWorkflow(engine)
except Exception as exc:
    st.error(f"Error initializing NyayaAI: {exc}")
    st.stop()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_voice_id" not in st.session_state:
    st.session_state.last_voice_id = None
if "voice_prompt" not in st.session_state:
    st.session_state.voice_prompt = None


with st.sidebar:
    st.markdown(
        """
        <div class="app-title">
            <div class="brand-mark">N</div>
            <div class="brand-copy">
                <p class="brand-name">NyayaAI</p>
                <p class="brand-subtitle">Constitutional assistant</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_voice_id = None
        st.session_state.voice_prompt = None
        st.rerun()

    st.markdown("<div class='sidebar-label'>Language</div>", unsafe_allow_html=True)
    selected_lang = st.selectbox("Choose consultation language", LANGUAGES, label_visibility="collapsed")

    st.markdown("<div class='sidebar-label'>Voice Input</div>", unsafe_allow_html=True)
    voice_query_ready = False
    if os.getenv("GROQ_API_KEY"):
        audio_file = st.audio_input("Record your grievance", label_visibility="collapsed")
        if audio_file:
            voice_id = f"{audio_file.size}_{audio_file.name}"
            if st.session_state.last_voice_id != voice_id:
                with st.spinner("Transcribing..."):
                    try:
                        st.session_state.voice_prompt = engine.transcribe_audio(audio_file)
                        st.session_state.last_voice_id = voice_id
                    except Exception as exc:
                        st.error(f"Transcription error: {exc}")
            if st.session_state.voice_prompt:
                st.info(st.session_state.voice_prompt)
                voice_query_ready = st.button("Send Voice Query", use_container_width=True)
    else:
        st.caption("Voice transcription is disabled. Add `GROQ_API_KEY` to enable microphone input.")

    st.markdown("<div class='sidebar-label'>Evaluation</div>", unsafe_allow_html=True)
    if st.button("Run Agent Evaluation", use_container_width=True):
        with st.spinner("Running checks..."):
            evaluation = agent_workflow.evaluate_cases(EVALUATION_CASES)
        st.metric("Accuracy", f"{evaluation['accuracy']}%")
        st.metric("Correct Cases", f"{evaluation['correct']} / {evaluation['total']}")
        with st.expander("Evaluation Rows"):
            st.dataframe(evaluation["rows"], use_container_width=True, hide_index=True)

    st.markdown("<div class='sidebar-label'>Notice</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="disclaimer">
            NyayaAI is an educational tool. It does not provide official legal representation or legal advice.
            For active disputes, consult a qualified advocate.
        </div>
        """,
        unsafe_allow_html=True,
    )


if not st.session_state.messages:
    st.markdown(
        """
        <div class="chat-heading">
            <h1>How can NyayaAI help?</h1>
            <p>Describe a real-life rights issue. NyayaAI searches the Constitution of India, checks the evidence, and gives a grounded explanation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

for index, message in enumerate(st.session_state.messages):
    avatar = "👤" if message["role"] == "user" else "⚖️"
    with st.chat_message(message["role"], avatar=avatar):
        if message["role"] == "assistant":
            render_agent_progress_stepper(message.get("progress_steps", []))
        st.markdown(message["content"])
        if message["role"] == "assistant":
            col_audio, _ = st.columns([1, 5])
            with col_audio:
                if st.button("Play", key=f"play_{index}"):
                    with st.spinner("Preparing audio..."):
                        st.audio(generate_speech(message["content"], selected_lang), format="audio/mp3")
            render_sources(message.get("sources", []))
            render_agent_trace(message)

query_text = None
if voice_query_ready and st.session_state.voice_prompt:
    query_text = st.session_state.voice_prompt
    st.session_state.voice_prompt = None
    st.session_state.last_voice_id = None

text_prompt = st.chat_input("Message NyayaAI")
if text_prompt:
    query_text = text_prompt

if query_text:
    handle_query(query_text, selected_lang)
    st.rerun()
