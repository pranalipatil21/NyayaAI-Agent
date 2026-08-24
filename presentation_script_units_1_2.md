# Presentation Script & Concept Mapping: Units I & II

**Project:** NyayaAI — Constitutional Problem Solver (India)  
**Scope:** Unit I (Foundations of Agentic AI) & Unit II (Architecture & Frameworks for Agents)

---

## Part 1: Unit I — Foundations of Agentic AI

### 🎤 Spoken Presentation Script (Unit I)

> **"Respected Professor and Evaluators, good morning/afternoon.**
>
> Today, we present **NyayaAI**, an agentic Retrieval-Augmented Generation (RAG) system designed to deliver legal advice grounded in the Constitution of India.
>
> **1. Evolution to Agentic Systems:**
> Traditional AI systems rely on static rules or basic classifiers. Generative AI brought powerful single-turn response generation, but struggles with multi-step reasoning and hallucination. **Agentic AI** goes beyond passive text generation—it operates autonomously with planning, tool invocation, self-reflection, and decision routing.
>
> **2. Role of LLMs, Embeddings, and Retrieval:**
> In NyayaAI, the Large Language Model acts as the reasoning engine (`llama-3.3-70b-versatile` via Groq LPU). Rather than relying on memorized parameters, NyayaAI uses a local CPU-optimized Hugging Face embedding model (`BAAI/bge-small-en-v1.5`) to convert the Constitution into dense vector representations. These are retrieved from ChromaDB based on semantic similarity.
>
> **3. ReAct & Chain-of-Thought (CoT) Frameworks:**
> Rather than jumping straight to an answer, NyayaAI implements the **ReAct (Reasoning + Acting)** framework. The system explicitly plans its investigation, queries its vector search tool, observes the retrieved constitutional articles, reflects on factual alignment, and then generates structured legal advice. The user can inspect this exact step-by-step decision trace in the application UI.
>
> **4. Prompt Engineering Techniques:**
> We applied several advanced prompt engineering strategies:
> - **Persona Prompting:** Enforcing the role of *Nyaya Sahayak*, a compassionate legal assistant.
> - **Guardrail Fallbacks:** Directing the model to reject off-topic questions (like sports or math) with a predefined formal boundary message.
> - **Dynamic Language Injection:** Appending strict translation directives to force output generation in regional Indian languages."

---

### 📚 Detailed Concept Explanation & Project Mapping (Unit I)

| Concept from Syllabus | Theoretical Definition | Technical Implementation in NyayaAI Codebase |
| :--- | :--- | :--- |
| **Traditional vs Generative vs Agentic AI** | Traditional AI uses rule-based logic; Generative AI outputs text probabilistically; Agentic AI uses loops, state memory, tool access, and goal-directed autonomy. | In [`app.py`](file:///d:/Pranali/projects/NyayaAI-main/app.py), NyayaAI does not perform a single LLM API call. It executes a state graph (`app.py` / `src/agentic.py`) that classifies intent, plans steps, searches a DB tool, verifies facts, and formats outputs. |
| **Embeddings & Vector Retrieval** | Converting text into dense numerical vectors to measure semantic similarity via vector distance. | `HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5", model_kwargs={'device': 'cpu'})` in [`src/engine.py`](file:///d:/Pranali/projects/NyayaAI-main/src/engine.py#L89-L92) creates 384-dimensional vector representations stored in ChromaDB. |
| **ReAct (Reasoning + Acting)** | Interleaving thought generation (Reasoning) with tool execution (Acting) to solve complex tasks. | Interleaved steps in [`src/agentic.py`](file:///d:/Pranali/projects/NyayaAI-main/src/agentic.py): <br>1. **Plan** (`planner_node`) <br>2. **Act** (`retrieval_node` calls ChromaDB tool) <br>3. **Observe** (reads retrieved context) <br>4. **Decide** (`verification_node` & `response_node`). |
| **Chain-of-Thought (CoT)** | Breaking down complex problems into intermediate step-by-step reasoning paths before answering. | Displayed live in the Streamlit UI tab under **"Agent Decision Trace"**, logging `Plan → Tool → Observation → Decision`. |
| **Prompt Engineering** | Structuring inputs to steer LLMs towards precise, constrained, and formatted outputs. | Persona, context grounding, and anti-hallucination constraints defined in [`src/prompts.py`](file:///d:/Pranali/projects/NyayaAI-main/src/prompts.py#L1-L25). Dynamic language injection appended in [`src/engine.py`](file:///d:/Pranali/projects/NyayaAI-main/src/engine.py#L146-L150). |

---

## Part 2: Unit II — Architecture & Frameworks for Agents

### 🎤 Spoken Presentation Script (Unit II)

> **"Moving to Unit II: Agent Architectures and Frameworks.**
>
> **1. Single-Agent vs Multi-Agent Architecture:**
> A single-agent RAG system tries to perform retrieval, reasoning, verification, and translation in a single monolithic prompt, which frequently leads to confusion and hallucination. NyayaAI uses a **Multi-Agent Architecture** powered by **LangGraph**, where specialized agents handle distinct sub-tasks.
>
> **2. Core Design Patterns Implemented:**
> We incorporated five fundamental agent design patterns:
> - **Planning Pattern:** The *Planner Agent* analyzes the user's grievance and creates an investigation roadmap before searching.
> - **Tool-Use Pattern:** The *Constitutional Retrieval Agent* treats ChromaDB as an external tool, invoking vector similarity search to gather evidence.
> - **Reflection Pattern:** The *Verification Agent* acts as a critic, cross-referencing the proposed constitutional articles against the retrieved document chunks to ensure factual support.
> - **ReAct Pattern:** Orchestrates thought-action-observation cycles across the execution pipeline.
> - **Multi-Agent Orchestration:** Controlled via a state machine DAG (Directed Acyclic Graph) in LangGraph.
>
> **3. Framework Overview (LangChain, LangGraph, ChromaDB):**
> - **LangChain:** Handles document loading (`PyPDFLoader`), parent-child text splitting (`RecursiveCharacterTextSplitter`), and prompt templating.
> - **LangGraph:** Coordinates state transitions, node execution, and control flow branching.
> - **ChromaDB:** Operates as our local persistent vector database storing indexed chunks of the Constitution of India."

---

### 📚 Detailed Concept Explanation & Project Mapping (Unit II)

| Concept from Syllabus | Theoretical Definition | Technical Implementation in NyayaAI Codebase |
| :--- | :--- | :--- |
| **Single-Agent vs Multi-Agent Architecture** | Single-agent uses one loop; Multi-agent divides responsibilities across specialized, state-sharing nodes. | Implemented via `StateGraph(AgentState)` in [`src/agentic.py`](file:///d:/Pranali/projects/NyayaAI-main/src/agentic.py). Six distinct nodes handle Orchestration, Planning, Retrieval, Analysis, Verification, and Response. |
| **Planning Design Pattern** | Generating an explicit sequence of steps before calling execution tools. | `planner_node` in [`src/agentic.py`](file:///d:/Pranali/projects/NyayaAI-main/src/agentic.py) receives the query and intent, then populates `state["plan"]` with legal investigation steps. |
| **Tool-Use Design Pattern** | Equipping LLMs with external tools (APIs, DBs, calculators) to perform actions outside their parameter weights. | `retrieval_node` in [`src/agentic.py`](file:///d:/Pranali/projects/NyayaAI-main/src/agentic.py) invokes `NyayaEngine.retriever.invoke(query)` as an explicit search tool against ChromaDB. |
| **Reflection Design Pattern** | A secondary agent reviewing, critiquing, and validating the primary agent's output for correctness. | `verification_node` in [`src/agentic.py`](file:///d:/Pranali/projects/NyayaAI-main/src/agentic.py) compares identified articles against retrieved context and sets `verification_result` to PASS or FAIL. |
| **Multi-Agent Orchestration** | Managing execution order, conditional branching, and state synchronization across multiple agents. | `workflow.add_edge()` and `workflow.add_conditional_edges()` in [`src/agentic.py`](file:///d:/Pranali/projects/NyayaAI-main/src/agentic.py) define the control flow DAG. |
| **Vector DB (ChromaDB)** | High-performance database optimized for storing and searching high-dimensional vector embeddings. | `Chroma(collection_name="nyaya_legal_db", embedding_function=..., persist_directory="./chroma_db")` in [`src/engine.py`](file:///d:/Pranali/projects/NyayaAI-main/src/engine.py#L107-L111). |







<!-- cd D:\Pranali\projects\NyayaAI-main

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

# Configure your API key
"GROQ_API_KEY=your_groq_api_key_here" | Set-Content .env

streamlit run app.py -->