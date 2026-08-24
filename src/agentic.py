import re
import time
from typing import Any, Dict, List, TypedDict

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:  # Allows the app to run before requirements are installed.
    END = START = StateGraph = None

from .prompts import AGENTIC_RESPONSE_PROMPT, SYSTEM_PROMPT


OUT_OF_SCOPE_RESPONSE = (
    "I am unable to deliver an answer to this question. As Nyaya Sahayak, my expertise is strictly "
    "limited to issues of fundamental rights and matters directly governed by the Constitution of India."
)


OFF_TOPIC_KEYWORDS = {
    "ipl",
    "capital of france",
    "binary search",
    "python code",
    "weather",
    "recipe",
    "stock price",
}

GREETING_QUERIES = {
    "hi",
    "hii",
    "hiii",
    "hello",
    "hey",
    "namaste",
    "namaskar",
    "नमस्ते",
    "हाय",
}


def is_greeting_query(query: str) -> bool:
    normalized = re.sub(r"[^\w\s\u0900-\u097F]", "", query.strip().lower())
    normalized = re.sub(r"\s+", " ", normalized)
    if normalized in GREETING_QUERIES:
        return True
    return bool(re.fullmatch(r"h+i+", normalized))


def is_off_topic_query(query: str) -> bool:
    normalized = re.sub(r"[^\w\s\u0900-\u097F]", " ", query.strip().lower())
    normalized = re.sub(r"\s+", " ", normalized)
    constitutional_terms = {
        "article",
        "constitution",
        "constitutional",
        "fundamental right",
        "rights",
        "court",
        "writ",
        "police",
        "arrest",
        "detain",
        "detained",
        "discrimination",
        "equality",
        "liberty",
        "speech",
        "religion",
        "education",
    }
    if any(term in normalized for term in constitutional_terms):
        return False
    return any(keyword in normalized for keyword in OFF_TOPIC_KEYWORDS)


ARTICLE_HINTS = {
    "Article 14": ["equality", "equal protection", "arbitrary", "unfair treatment"],
    "Article 15": ["caste", "religion", "race", "sex", "gender", "discrimination", "admission"],
    "Article 19": ["speech", "expression", "assembly", "association", "movement"],
    "Article 20": ["conviction", "punishment", "criminal", "double jeopardy"],
    "Article 21": ["life", "liberty", "livelihood", "dignity", "salary", "wage"],
    "Article 21A": ["education", "school", "child", "admission"],
    "Article 22": ["police", "detained", "arrest", "custody", "magistrate", "24 hours", "judge"],
    "Article 23": ["forced labour", "forced labor", "begar", "salary", "wage", "unpaid"],
    "Article 24": ["child labour", "factory", "hazardous"],
    "Article 25": ["religion", "faith", "worship"],
    "Article 32": ["supreme court", "writ", "remedy"],
}


class AgentState(TypedDict, total=False):
    query: str
    language: str
    intent: str
    in_scope: bool
    is_greeting: bool
    plan: List[str]
    retrieved_docs: List[Any]
    sources: List[Dict[str, Any]]
    relevant_articles: List[str]
    analysis: str
    verification_result: str
    confidence: int
    final_response: str
    trace: List[Dict[str, str]]
    timings: Dict[str, float]
    progress_steps: List[Dict[str, Any]]


class NyayaAgentWorkflow:
    """Agent workflow around the existing NyayaAI RAG engine."""

    def __init__(self, engine):
        self.engine = engine
        self.graph = self._build_graph()

    def run(self, query: str, language: str = "English") -> Dict[str, Any]:
        initial_state: AgentState = {
            "query": query,
            "language": language,
            "trace": [],
            "timings": {},
        }
        started_at = time.perf_counter()

        if self.graph is not None:
            state = self.graph.invoke(initial_state)
        else:
            state = initial_state
            for step in (
                self.orchestrator_agent,
                self.planner_agent,
                self.retrieval_agent,
                self.rights_analysis_agent,
                self.verification_agent,
                self.response_agent,
            ):
                state = step(state)

        state["timings"]["total"] = round(time.perf_counter() - started_at, 3)
        return {
            "answer": state.get("final_response", ""),
            "sources": state.get("sources", []),
            "trace": state.get("trace", []),
            "intent": state.get("intent", "Unclassified"),
            "plan": state.get("plan", []),
            "articles": state.get("relevant_articles", []),
            "verification": state.get("verification_result", "Not verified"),
            "confidence": state.get("confidence", 0),
            "timings": state.get("timings", {}),
            "progress_steps": state.get("progress_steps", []),
        }

    def run_with_events(self, query: str, language: str = "English"):
        state: AgentState = {
            "query": query,
            "language": language,
            "trace": [],
            "timings": {},
        }
        started_at = time.perf_counter()
        steps = self._build_progress_steps(query)

        yield {
            "event": "agent:start",
            "steps": self._step_snapshot(steps),
            "state": state,
        }

        for step in steps:
            step["status"] = "active"
            step["started_at"] = time.perf_counter()
            yield {
                "event": "step:start",
                "step": step,
                "steps": self._step_snapshot(steps),
                "state": state,
            }

            try:
                state = step["runner"](state)
                step["status"] = "completed"
                step["duration"] = round(time.perf_counter() - step["started_at"], 3)
                step["description"] = self._progress_summary(step["id"], state)
            except Exception as exc:
                step["status"] = "error"
                step["duration"] = round(time.perf_counter() - step["started_at"], 3)
                step["description"] = str(exc)
                state["progress_steps"] = self._step_snapshot(steps)
                yield {
                    "event": "step:error",
                    "step": step,
                    "steps": self._step_snapshot(steps),
                    "state": state,
                    "error": str(exc),
                }
                raise

            yield {
                "event": "step:complete",
                "step": step,
                "steps": self._step_snapshot(steps),
                "state": state,
            }

        state["timings"]["total"] = round(time.perf_counter() - started_at, 3)
        state["progress_steps"] = self._step_snapshot(steps)
        yield {
            "event": "agent:complete",
            "steps": self._step_snapshot(steps),
            "state": state,
            "result": {
                "answer": state.get("final_response", ""),
                "sources": state.get("sources", []),
                "trace": state.get("trace", []),
                "intent": state.get("intent", "Unclassified"),
                "plan": state.get("plan", []),
                "articles": state.get("relevant_articles", []),
                "verification": state.get("verification_result", "Not verified"),
                "confidence": state.get("confidence", 0),
                "timings": state.get("timings", {}),
                "progress_steps": state.get("progress_steps", []),
            },
        }

    def evaluate_cases(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        rows = []
        started_at = time.perf_counter()

        for case in cases:
            query = case["query"]
            expected = case["expected"]
            state: AgentState = {
                "query": query,
                "language": "English",
                "trace": [],
                "timings": {},
            }
            state = self.orchestrator_agent(state)
            state = self.planner_agent(state)
            state = self.retrieval_agent(state)
            state = self.rights_analysis_agent(state)
            state = self.verification_agent(state)
            predicted = ["Reject"] if not state.get("in_scope") else state.get("relevant_articles", [])
            correct = self._case_matches(expected, predicted)
            rows.append(
                {
                    "Query": query,
                    "Expected": ", ".join(expected),
                    "Agent Result": ", ".join(predicted) if predicted else "No article found",
                    "Correct": "Yes" if correct else "No",
                    "Intent": state.get("intent", "Unclassified"),
                    "Verification": state.get("verification_result", "Not verified"),
                }
            )

        total = len(rows)
        correct_count = sum(1 for row in rows if row["Correct"] == "Yes")
        return {
            "rows": rows,
            "accuracy": round((correct_count / total) * 100, 1) if total else 0,
            "correct": correct_count,
            "total": total,
            "latency": round(time.perf_counter() - started_at, 3),
        }

    def orchestrator_agent(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        query = state["query"].strip().lower()
        is_greeting = is_greeting_query(query)
        off_topic = is_off_topic_query(query)
        in_scope = bool(query) and not off_topic and not is_greeting
        intent = "Greeting" if is_greeting else self._classify_intent(query) if in_scope else "Out of scope"

        state["intent"] = intent
        state["in_scope"] = in_scope
        state["is_greeting"] = is_greeting
        if is_greeting:
            self._record_timing(state, "orchestration", started_at)
            return state
        self._add_trace(
            state,
            "Orchestrator Agent",
            "Classify whether the user problem needs constitutional investigation.",
            f"Intent: {intent}; Scope: {'accepted' if in_scope else 'rejected'}",
            "Proceed to planning" if in_scope else "Return scope guardrail",
        )
        self._record_timing(state, "orchestration", started_at)
        return state

    def planner_agent(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        if state.get("is_greeting"):
            state["plan"] = ["Respond with a short welcome message"]
            self._record_timing(state, "planning", started_at)
            return state
        if not state.get("in_scope"):
            state["plan"] = ["Apply scope guardrail", "Do not retrieve unrelated documents"]
        else:
            state["plan"] = [
                "Identify the citizen grievance and likely right category",
                "Use the Constitution search tool",
                "Analyze retrieved Articles against the facts",
                "Verify that claims are supported by retrieved evidence",
                "Generate a plain-language educational response with citations",
            ]
        self._add_trace(
            state,
            "Planner Agent",
            "Create a short legal investigation plan.",
            " → ".join(state["plan"]),
            "Delegate to retrieval agent" if state.get("in_scope") else "Stop workflow early",
        )
        self._record_timing(state, "planning", started_at)
        return state

    def retrieval_agent(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        if state.get("is_greeting") or not state.get("in_scope"):
            state["retrieved_docs"] = []
            state["sources"] = []
            self._record_timing(state, "retrieval", started_at)
            return state

        retrieved_docs = self.engine.retriever.invoke(state["query"])
        state["retrieved_docs"] = retrieved_docs
        state["sources"] = self._format_sources(retrieved_docs)
        pages = [str(source["page"]) for source in state["sources"]]
        self._add_trace(
            state,
            "Constitutional Retrieval Agent",
            "Search Constitution vector store with ChromaDB.",
            f"Retrieved {len(retrieved_docs)} snippets from page(s): {', '.join(pages) or 'Unknown'}",
            "Send evidence to rights analysis agent",
        )
        self._record_timing(state, "retrieval", started_at)
        return state

    def rights_analysis_agent(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        if state.get("is_greeting"):
            state["relevant_articles"] = []
            state["analysis"] = "Greeting handled without legal retrieval."
            self._record_timing(state, "analysis", started_at)
            return state
        if not state.get("in_scope"):
            state["relevant_articles"] = ["Reject"]
            state["analysis"] = "The query is outside NyayaAI's constitutional scope."
            self._record_timing(state, "analysis", started_at)
            return state

        text = " ".join([doc.page_content for doc in state.get("retrieved_docs", [])])
        articles = self._extract_articles(text)
        hinted_articles = self._hint_articles(state["query"])
        merged_articles = self._merge_articles(hinted_articles + articles)
        state["relevant_articles"] = merged_articles[:5]
        state["analysis"] = (
            f"The query appears to involve {state.get('intent', 'constitutional rights')}. "
            f"Likely relevant Articles: {', '.join(state['relevant_articles']) or 'not clear from retrieval'}."
        )
        self._add_trace(
            state,
            "Rights Analysis Agent",
            "Map the problem facts to likely constitutional protections.",
            state["analysis"],
            "Send mapped claims to verification agent",
        )
        self._record_timing(state, "analysis", started_at)
        return state

    def verification_agent(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        if state.get("is_greeting"):
            state["verification_result"] = "No legal claim to verify."
            state["confidence"] = 100
            self._record_timing(state, "verification", started_at)
            return state
        if not state.get("in_scope"):
            state["verification_result"] = "Rejected by constitutional scope guardrail."
            state["confidence"] = 100
            self._record_timing(state, "verification", started_at)
            return state

        evidence_text = " ".join([source["content"] for source in state.get("sources", [])]).lower()
        supported_articles = [
            article
            for article in state.get("relevant_articles", [])
            if article.lower() in evidence_text or self._article_number(article) in evidence_text
        ]
        state["verification_result"] = (
            f"Evidence supported for: {', '.join(supported_articles)}"
            if supported_articles
            else "Retrieved evidence is related, but exact Article labels were not explicit in the snippets."
        )
        state["confidence"] = min(95, 55 + (len(supported_articles) * 12) + (len(state.get("sources", [])) * 4))
        self._add_trace(
            state,
            "Verification Agent",
            "Check whether generated legal claims are grounded in retrieved Constitution snippets.",
            state["verification_result"],
            "Generate final answer" if supported_articles else "Generate cautious answer with source caveat",
        )
        self._record_timing(state, "verification", started_at)
        return state

    def response_agent(self, state: AgentState) -> AgentState:
        started_at = time.perf_counter()
        if state.get("is_greeting"):
            state["final_response"] = (
                "Hello. I am NyayaAI, your Constitutional assistant. Tell me what happened, "
                "and I will help identify relevant rights, Articles, sources, and practical next steps."
            )
            self._record_timing(state, "generation", started_at)
            return state
        if not state.get("in_scope"):
            state["final_response"] = OUT_OF_SCOPE_RESPONSE
            self._record_timing(state, "generation", started_at)
            return state

        context = "\n\n".join([source["content"] for source in state.get("sources", [])])
        lang_instruction = ""
        if state.get("language") and state["language"] != "English":
            target_lang = state["language"].split(" ")[0]
            lang_instruction = (
                f"\n\nCRITICAL LANGUAGE MANDATE: You MUST write your ENTIRE final response (including all headings, bullet points, constitutional explanations, suggested actions, and legal disclaimers) strictly in {target_lang} ({state['language']}). "
                f"Do NOT output in Hindi or English if {target_lang} is requested! Use proper native {target_lang} vocabulary and script. Keep only official Article numbers (like 'Article 21') in English."
            )
        prompt = AGENTIC_RESPONSE_PROMPT.format(
            context=context,
            intent=state.get("intent", "Constitutional rights"),
            plan="\n".join([f"- {item}" for item in state.get("plan", [])]),
            articles=", ".join(state.get("relevant_articles", [])) or "Use only supported Articles from context",
            verification=state.get("verification_result", "Verification pending"),
        )
        if self.engine.llm is None:
            self.engine._init_llm()

        if self.engine.llm is None:
            state["final_response"] = self.engine._fallback_response(
                state["query"],
                state.get("sources", []),
                language=state.get("language", "English"),
                articles=state.get("relevant_articles", []),
                verification=state.get("verification_result"),
            )
        else:
            try:
                response = self.engine.llm.invoke(
                    [
                        ("system", SYSTEM_PROMPT.format(context=context) + lang_instruction),
                        ("human", prompt + f"\n\nUser problem: {state['query']}"),
                    ]
                )
                state["final_response"] = response.content
            except Exception:
                state["final_response"] = self.engine._fallback_response(
                    state["query"],
                    state.get("sources", []),
                    language=state.get("language", "English"),
                    articles=state.get("relevant_articles", []),
                    verification=state.get("verification_result"),
                )
        self._add_trace(
            state,
            "Response Agent",
            "Prepare the citizen-facing answer.",
            "Generated final response from verified retrieved evidence.",
            "Return answer, citations, metrics, and trace",
        )
        self._record_timing(state, "generation", started_at)
        return state

    def _build_progress_steps(self, query: str) -> List[Dict[str, Any]]:
        query_text = query.strip().lower()
        if is_greeting_query(query_text):
            return [
                {
                    "id": "understand",
                    "label": "Understanding request",
                    "status": "pending",
                    "runner": self.orchestrator_agent,
                },
                {
                    "id": "respond",
                    "label": "Preparing welcome",
                    "status": "pending",
                    "runner": self.response_agent,
                },
            ]

        if is_off_topic_query(query_text):
            return [
                {
                    "id": "understand",
                    "label": "Understanding request",
                    "status": "pending",
                    "runner": self.orchestrator_agent,
                },
                {
                    "id": "guardrail",
                    "label": "Checking scope",
                    "status": "pending",
                    "runner": self.planner_agent,
                },
                {
                    "id": "respond",
                    "label": "Preparing response",
                    "status": "pending",
                    "runner": self.response_agent,
                },
            ]

        return [
            {
                "id": "understand",
                "label": "Understanding request",
                "status": "pending",
                "runner": self.orchestrator_agent,
            },
            {
                "id": "plan",
                "label": "Planning approach",
                "status": "pending",
                "runner": self.planner_agent,
            },
            {
                "id": "retrieve",
                "label": "Searching the Constitution",
                "status": "pending",
                "runner": self.retrieval_agent,
            },
            {
                "id": "analyze",
                "label": "Analyzing rights",
                "status": "pending",
                "runner": self.rights_analysis_agent,
            },
            {
                "id": "verify",
                "label": "Verifying evidence",
                "status": "pending",
                "runner": self.verification_agent,
            },
            {
                "id": "respond",
                "label": "Creating response",
                "status": "pending",
                "runner": self.response_agent,
            },
        ]

    def _step_snapshot(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        visible_keys = ("id", "label", "description", "status", "duration", "metadata")
        return [{key: step[key] for key in visible_keys if key in step} for step in steps]

    def _progress_summary(self, step_id: str, state: AgentState) -> str:
        if step_id == "understand":
            return f"Intent: {state.get('intent', 'Unclassified')}"
        if step_id == "plan":
            return f"{len(state.get('plan', []))} action(s) planned"
        if step_id == "retrieve":
            return f"{len(state.get('sources', []))} source snippet(s) found"
        if step_id == "analyze":
            articles = state.get("relevant_articles", [])
            return ", ".join(articles) if articles else "No Article labels identified"
        if step_id == "verify":
            return state.get("verification_result", "Verification completed")
        if step_id == "guardrail":
            return "Scope decision completed"
        if step_id == "respond":
            return "Response ready"
        return "Completed"

    def _build_graph(self):
        if StateGraph is None:
            return None
        graph = StateGraph(AgentState)
        graph.add_node("orchestrator", self.orchestrator_agent)
        graph.add_node("planner", self.planner_agent)
        graph.add_node("retriever", self.retrieval_agent)
        graph.add_node("analyzer", self.rights_analysis_agent)
        graph.add_node("verifier", self.verification_agent)
        graph.add_node("responder", self.response_agent)
        graph.add_edge(START, "orchestrator")
        graph.add_edge("orchestrator", "planner")
        graph.add_edge("planner", "retriever")
        graph.add_edge("retriever", "analyzer")
        graph.add_edge("analyzer", "verifier")
        graph.add_edge("verifier", "responder")
        graph.add_edge("responder", END)
        return graph.compile()

    def _format_sources(self, docs) -> List[Dict[str, Any]]:
        sources = []
        for idx, doc in enumerate(docs):
            page_num = doc.metadata.get("page", 0) + 1 if "page" in doc.metadata else "Unknown"
            source_file = doc.metadata.get("source", "constitution.pdf").split("/")[-1]
            sources.append(
                {
                    "id": idx + 1,
                    "content": doc.page_content,
                    "source": source_file,
                    "page": page_num,
                }
            )
        return sources

    def _classify_intent(self, query: str) -> str:
        if any(word in query for word in ["police", "detained", "arrest", "custody", "magistrate"]):
            return "Police detention and personal liberty"
        if any(word in query for word in ["salary", "wage", "labour", "labor", "worker"]):
            return "Labour, livelihood, and forced work"
        if any(word in query for word in ["caste", "religion", "gender", "discrimination"]):
            return "Equality and discrimination"
        if any(word in query for word in ["school", "education", "admission"]):
            return "Education rights"
        if any(word in query for word in ["speech", "expression", "protest"]):
            return "Freedom of speech and expression"
        return "Constitutional rights inquiry"

    def _extract_articles(self, text: str) -> List[str]:
        matches = re.findall(r"\bArticle\s+([0-9]+[A-Z]?)\b", text, flags=re.IGNORECASE)
        return self._merge_articles([f"Article {match.upper()}" for match in matches])

    def _hint_articles(self, query: str) -> List[str]:
        query = query.lower()
        articles = []
        direct_mentions = re.findall(r"\barticle\s+([0-9]+[a-z]?)\b", query, flags=re.IGNORECASE)
        articles.extend([f"Article {mention.upper()}" for mention in direct_mentions])
        for article, hints in ARTICLE_HINTS.items():
            if any(hint in query for hint in hints):
                articles.append(article)
        return articles

    def _merge_articles(self, articles: List[str]) -> List[str]:
        seen = set()
        merged = []
        for article in articles:
            if article not in seen:
                seen.add(article)
                merged.append(article)
        return merged

    def _article_number(self, article: str) -> str:
        return article.lower().replace("article", "").strip()

    def _case_matches(self, expected: List[str], predicted: List[str]) -> bool:
        if expected == ["Reject"]:
            return predicted == ["Reject"]
        return any(article in predicted for article in expected)

    def _add_trace(self, state: AgentState, agent: str, action: str, observation: str, decision: str) -> None:
        state.setdefault("trace", []).append(
            {
                "agent": agent,
                "action": action,
                "observation": observation,
                "decision": decision,
            }
        )

    def _record_timing(self, state: AgentState, key: str, started_at: float) -> None:
        state.setdefault("timings", {})[key] = round(time.perf_counter() - started_at, 3)
