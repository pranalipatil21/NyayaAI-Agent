# ⚖️ NyayaAI — Constitutional Problem Solver (India)

NyayaAI is an agentic Retrieval-Augmented Generation (RAG) system designed to empower Indian citizens by providing actionable legal guidance grounded in the **Constitution of India (1950)**.

Most citizens find legal language intimidating. NyayaAI bridges this gap by allowing users to describe real-life problems (like unpaid wages, police misconduct, or discrimination) in plain English or multiple Indian languages, receive responses mapped to relevant Constitutional Articles, and listen to the advice spoken out loud.

---

## 🚀 Project Overview

NyayaAI helps users:
* **Explain problems in simple language** (via keyboard text or microphone voice recording)
* **Translate queries and responses** across major Indian languages
* **Automatically map scenarios** to relevant Constitutional Articles
* **Generate structured response plans** containing:
  * Article citations
  * Simple legal rights explanations
  * Actionable next steps
  * Listen to responses spoken out loud in the selected language
* **Verify legal context** through an interactive explainability drawer showing exact source snippets and page numbers
* **Inspect a sanitized agent decision trace** showing Plan → Tool → Observation → Decision
* **Evaluate the agent workflow** with built-in benchmark scenarios for article mapping and scope filtering

> [!WARNING]
> **Disclaimer:** NyayaAI is an educational and informational tool. It does not provide formal legal representation or legal advice. For active proceedings, consult a registered advocate.

---

## 🧠 Core Features

* **✅ Multilingual UI & Output**
  Choose from **English, Hindi (हिन्दी), Marathi (मराठी), Tamil (தமிழ்), Telugu (తెలుగు), and Bengali (বাংলা)**. The chatbot dynamically writes the full structured legal advice in your chosen language.
* **✅ Voice Input (Speech-to-Text Microphone)**
  Record your grievance using an in-app microphone widget. Speech is transcribed instantly with high-speed accuracy.
* **✅ Voice Output (Text-to-Speech Playback)**
  Listen to your legal advice read out loud. Next to each chatbot response, a playback button synthesizes a clean, natural-sounding voice stream in the selected language.
* **✅ Scenario-Based Reasoning & Scope Filtering**
  Understands complex real-life grievances and maps them to specific Articles. Employs strict anti-hallucination guardrails to block off-topic general knowledge queries (like sports, coding, math, or trivia).
* **✅ Article Integrity (Parent Document Retrieval)**
  Uses advanced chunking to ensure Articles are not cut in half, preserving complete, legally sound context.
* **✅ Agentic Legal Workflow**
  Adds an Orchestrator Agent, Planner Agent, Constitutional Retrieval Agent, Rights Analysis Agent, Verification Agent, and Response Agent around the existing RAG system.
* **✅ ReAct-Style Explainability**
  Displays a sanitized decision trace that demonstrates tool use without exposing hidden chain-of-thought.
* **✅ Benchmark Evaluation Tab**
  Runs representative test cases for article-mapping accuracy, rejection accuracy, intent classification, and workflow latency.
* **✅ Silent, Optimized CPU Embedding Inference**
  Optimized PyTorch threads to prevent CPU spikes and eliminate noisy laptop fan buzzing during query calculations.

---

## 🛠️ Tech Stack (Free Power Stack)

| Component | Technology | Description |
| :--- | :--- | :--- |
| **UI Framework** | **Streamlit** | Interactive interface with tabs and voice recorders |
| **Orchestration** | **LangChain + LangGraph** | Document loading, chunking, RAG pipelines, and multi-agent workflow state |
| **Reasoning Model** | **Groq LPU (Llama-3.3-70b-versatile)** | Sub-second reasoning and high-fidelity translations |
| **Speech-to-Text** | **Groq Whisper API (whisper-large-v3)** | High-accuracy multilingual speech transcription |
| **Text-to-Speech** | **gTTS (Google Text-to-Speech)** | Dynamic, zero-cost voice audio synthesis |
| **Embeddings** | **Hugging Face (BAAI/bge-small-en-v1.5)** | CPU-optimized local embeddings |
| **Vector Store** | **ChromaDB** | Local persistent vector storage |

---

## ⚙️ Deep-Dive: Frameworks, Libraries & Functions

Below is a detailed breakdown of the specific libraries, class APIs, and functions utilized to build the NyayaAI backend and frontend architecture.

### 1. RAG vector Database & Retrieval (Core Pipeline)
* **Document Loading**: 
  * **Library**: `langchain-community`
  * **Class**: `PyPDFLoader`
  * **Function**: `loader.load()` loads and parses the official Constitution PDF into separate page document models.
* **Text Splitting & Chunking**:
  * **Library**: `langchain-text-splitters`
  * **Class**: `RecursiveCharacterTextSplitter`
  * **Implementation**: We define a `parent_splitter` (chunk size 2000, 0 overlap) with custom separators `["\nArticle ", "\nPART ", "\n\n"]` to maintain legal boundaries, and a `child_splitter` (chunk size 400, overlap 50) to create granular semantic contexts.
  * **Functions**: `parent_splitter.split_documents()` and `child_splitter.split_documents()` process parent documents into searchable child slices.
* **Semantic Embeddings**:
  * **Library**: `langchain-huggingface`
  * **Class**: `HuggingFaceEmbeddings`
  * **Implementation**: Loads the lightweight, state-of-the-art `BAAI/bge-small-en-v1.5` model (120MB) mapped to CPU inference (`model_kwargs={'device': 'cpu'}`).
* **Vector Store Database**:
  * **Library**: `langchain-chroma`
  * **Class**: `Chroma`
  * **Functions**:
    * `Chroma(collection_name, embedding_function, persist_directory)` initializes the DB client.
    * `vectorstore.add_documents()` writes ingested document chunks to the local DB file.
    * `vectorstore.as_retriever(search_kwargs={"k": 4})` turns the database into a standard LangChain query-retriever object.
    * `retriever.invoke(query)` performs vector similarity search to fetch the top 4 matching document chunks.

### 1.1 Agentic Workflow Layer
* **Framework**:
  * **Library**: `langgraph`
  * **Class**: `StateGraph`
  * **Implementation**: NyayaAI wraps the RAG pipeline in a shared `AgentState` containing `query`, `language`, `intent`, `plan`, `retrieved_documents`, `relevant_articles`, `verification_result`, `confidence`, `final_response`, `trace`, and `timings`.
* **Agents**:
  * **Orchestrator Agent** classifies the user's intent and applies constitutional scope guardrails.
  * **Planner Agent** creates a short investigation plan.
  * **Constitutional Retrieval Agent** uses ChromaDB as an explicit search tool.
  * **Rights Analysis Agent** maps facts to likely Constitutional Articles.
  * **Verification Agent** checks whether the retrieved evidence supports the mapped Articles.
  * **Response Agent** produces the final citizen-friendly explanation with citations and disclaimer.
* **Explainability**:
  * The UI shows a sanitized Plan → Tool → Observation → Decision trace, source snippets, page numbers, confidence, and timing metrics.

### 2. Large Language Model (Groq Reasoning Engine)
* **LLM Client Orchestration**:
  * **Library**: `langchain-groq`
  * **Class**: `ChatGroq`
  * **Functions**: `llm.invoke(list_of_messages)` triggers Groq's low-latency inference. Passes system persona instructions and context retrieved from Chroma alongside the user's grievance.
  * **Model**: `llama-3.3-70b-versatile`

### 3. Voice Input (Speech-to-Text Transcription)
* **Frontend Recording Component**:
  * **Library**: `streamlit`
  * **Function**: `st.audio_input(label)` displays the native microphone widget, managing browser audio recording, file size buffering, and playback.
* **Transcription API**:
  * **Library**: `groq` (Standard Groq Cloud client SDK)
  * **Class**: `Groq(api_key)`
  * **Function**: `client.audio.transcriptions.create()`
    * **Parameters**: `file`, `model="whisper-large-v3"`, `prompt`, `response_format="text"`.
    * **Model**: Groq-hosted Whisper API which accepts recorded wav/mp3 bytes and outputs translated transcription string.
* **Redundant API Call Caching**:
  * **Mechanism**: Streamlit's stateful dictionary `st.session_state` stores `last_voice_id` (a hash of the recorded file's name and size). The engine only queries Groq Whisper when a *new* recording file is detected, preventing redundant network calls on browser reruns.

### 4. Voice Output (Text-to-Speech Playback)
* **Audio Synthesis Engine**:
  * **Library**: `gtts` (Google Text-to-Speech API wrapper)
  * **Class**: `gTTS(text, lang)`
  * **Implementation**: Converts text string to vocalized speech bytes. Translates to corresponding language codes (e.g. `hi` for Hindi, `mr` for Marathi, `ta` for Tamil, etc.).
* **In-Memory Streaming Buffer**:
  * **Library**: `io` (Standard Python library)
  * **Class**: `io.BytesIO()`
  * **Function**: `tts.write_to_fp(fp)` streams gTTS audio chunks directly into an in-memory byte buffer, eliminating disk write latencies.
* **Frontend Audio Playback**:
  * **Library**: `streamlit`
  * **Function**: `st.audio(audio_fp, format="audio/mp3")` streams the byte buffer from the server to play in the user's web browser.

### 5. CPU Thread & Performance Throttling
* **Thread Throttling**:
  * **Library**: `torch` (PyTorch)
  * **Functions**:
    * `torch.set_num_threads(1)` limits PyTorch intra-op threads.
    * `torch.set_num_interop_threads(1)` limits PyTorch inter-op threads.
  * **Environment Variables**: `os.environ["OMP_NUM_THREADS"] = "1"`, `os.environ["MKL_NUM_THREADS"] = "1"`, etc. limit PyTorch thread pools globally. This optimization stops laptop fans from buzzing by capping CPU usage during vector searches.
  * **Fail-safe wrap**: Thread settings are enclosed in `try-except RuntimeError` blocks to safely handle Streamlit module hot-reloading.

---

## 📁 Folder Structure

```
NyayaAI/
│
├── .streamlit/
│   └── config.toml         # Legal styling custom theme configurations
│
├── app.py                  # Streamlit tabbed UI (Homepage & Chat Assistant)
│
├── src/
│   ├── agentic.py          # LangGraph agent workflow + evaluation helpers
│   ├── engine.py           # RAG search + Whisper STT + PyTorch thread configs
│   └── prompts.py          # Legal persona prompt + anti-hallucination guardrails
│
├── data/
│   ├── constitution.pdf    # Source PDF of the Constitution of India
│   ├── lady_justice.png    # Homepage hero graphic
│   └── justice_logo.png    # Homepage Scales emblem
│
├── requirements.txt        # Project dependencies (langchain, gtts, groq, etc.)
└── README.md               # Documentation
```

---

## 🧪 Strategic Test Scenarios (Lawyer Thinking Test)

These scenario-based questions verify that NyayaAI maps real-life grievances to the correct Constitutional Articles, and successfully filters out general knowledge queries:

### 1) Labor & Wages (Economic Justice)
* **Question**: *"I have been working as a driver for 4 months, but my owner has not paid my salary and is threatening to fire me. Does the Constitution protect me?"*
* **Expected Mapping**: 
  * **Article 23** — Prohibition of forced labour (*begar*)
  * **Article 21** — Right to livelihood (part of Right to Life)

### 2) Police & Liberty (Personal Freedom)
* **Question**: *"The police took my brother to the station 30 hours ago without telling us why, and they haven't taken him to a judge. Is this legal?"*
* **Expected Mapping**:
  * **Article 22** — Must be produced before a magistrate within 24 hours
  * **Article 21** — Protection of life and personal liberty

### 3) Discrimination (Social Equality)
* **Question**: *"A local government school is refusing to admit my daughter because of our caste. What can I do?"*
* **Expected Mapping**:
  * **Article 15** — Prohibition of discrimination
  * **Article 21A** — Right to education (6–14 years)

### 4) Scope Filter & Anti-Hallucination (General Trivia)
* **Question**: *"What is IPL?"* or *"Which is the capital of France?"*
* **Expected Mapping**: Declines to answer with the formal scope fallback text:
  > *"I am unable to deliver an answer to this question. As Nyaya Sahayak, my expertise is strictly limited to issues of fundamental rights and matters directly governed by the Constitution of India."*
