import os
import logging
import warnings
from dataclasses import dataclass

# --- PyTorch & Hugging Face CPU/Noise Optimizations ---
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

# Suppress Hugging Face download telemetry & rate limit warning logs
warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
except (ImportError, RuntimeError):
    pass

try:
    from transformers.utils import logging as transformers_logging
    transformers_logging.set_verbosity_error()
except ImportError:
    pass

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
# -----------------------------------------------------

from dotenv import load_dotenv
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from .prompts import SYSTEM_PROMPT

load_dotenv(override=True)


@dataclass
class ChatResponse:
    content: str


class OpenRouterChat:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        self.model = model or os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")

    def invoke(self, messages):
        payload_messages = []
        for role, content in messages:
            payload_messages.append({"role": role, "content": content})

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "NyayaAI",
            },
            json={
                "model": self.model,
                "messages": payload_messages,
                "temperature": 0.1,
            },
            timeout=60,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"OpenRouter request failed: {response.status_code} {response.text}")

        data = response.json()
        return ChatResponse(content=data["choices"][0]["message"]["content"])


class NyayaEngine:
    def __init__(self):
        # 1. Initialize Local Embeddings (No more 429 Errors!)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'}
        )
        
        self.llm = None
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        if groq_key.startswith("ygsk_"):
            groq_key = groq_key[1:]

        if os.getenv("OPENROUTER_API_KEY"):
            self.llm = OpenRouterChat(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                model=os.getenv("OPENROUTER_MODEL")
            )
        elif groq_key:
            self.llm = ChatGroq(
                api_key=groq_key,
                model=os.getenv("GROQ_MODEL", "groq/compound"),
                temperature=0.1
            )
        
        # 2. Setup Storage
        self.vectorstore = Chroma(
            collection_name="nyaya_legal_db",
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )
        
        # 3. Setup Splitters
        self.parent_splitter = RecursiveCharacterTextSplitter(
            separators=["\nArticle ", "\nPART ", "\n\n"],
            chunk_size=2000,
            chunk_overlap=0
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})

    def ingest_data(self, pdf_path):
        """Loads and indexes the PDF as searchable chunks."""
        if not os.path.exists(pdf_path):
            return False
        
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        parent_docs = self.parent_splitter.split_documents(docs)
        child_docs = self.child_splitter.split_documents(parent_docs)

        if child_docs:
            self.vectorstore.add_documents(child_docs)
        return True

    def get_response(self, query, language="English"):
        """Retrieves context and generates legal advice in the specified language, alongside cited sources."""
        retrieved_docs = self.retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Append language instruction to LLM prompt
        lang_instruction = ""
        if language and language != "English":
            target_lang = language.split(" ")[0]
            lang_instruction = f"\n\nCRITICAL LANGUAGE MANDATE: You MUST write your ENTIRE final response (including all headings, bullet points, rights descriptions, action steps, and disclaimers) strictly in {target_lang} ({language}). Do NOT output in Hindi or English if {target_lang} is requested! Use native {target_lang} vocabulary and script. Keep official Article numbers (like 'Article 21') in English."
            
        formatted_prompt = SYSTEM_PROMPT.format(context=context) + lang_instruction
        
        # Structure source documents for the UI to display explainability information
        sources = []
        for idx, doc in enumerate(retrieved_docs):
            page_num = doc.metadata.get("page", 0) + 1 if "page" in doc.metadata else "Unknown"
            source_file = os.path.basename(doc.metadata.get("source", "constitution.pdf"))
            sources.append({
                "id": idx + 1,
                "content": doc.page_content,
                "source": source_file,
                "page": page_num
            })

        response_content = self._fallback_response(query, sources=sources, language=language)
        if self.llm is not None:
            try:
                response = self.llm.invoke([
                    ("system", formatted_prompt),
                    ("human", query)
                ])
                response_content = response.content
            except Exception as exc:
                logging.warning("Hosted LLM request failed; using grounded fallback: %s", exc)

        return {
            "answer": response_content,
            "sources": sources
        }

    def _fallback_response(self, query, sources, language="English", articles=None, verification=None):
        """Builds a grounded response when no hosted LLM API key is configured."""
        if language and language != "English":
            return (
                "No hosted LLM API key is configured, so NyayaAI cannot generate multilingual LLM responses yet. "
                "Please configure OPENROUTER_API_KEY or GROQ_API_KEY to enable full multilingual response generation."
            )

        articles = articles or []
        article_text = ", ".join(articles) if articles else "the retrieved Constitutional provisions"
        verification_text = verification or "The answer is based on retrieved Constitution snippets."
        source_lines = []
        for source in sources[:3]:
            source_lines.append(f"- Source {source['id']}: {source['source']}, page {source['page']}")

        return (
            "**Constitutional Protection**\n\n"
            f"Your problem may relate to {article_text}. {verification_text}\n\n"
            "**Your Rights**\n\n"
            "NyayaAI found relevant Constitutional context and is presenting a cautious, source-grounded summary. "
            "Review the source snippets below before relying on any conclusion.\n\n"
            "**Suggested Action**\n\n"
            "1. Write down the facts, dates, names, and any documents or witnesses.\n"
            "2. Contact the nearest District Legal Services Authority or a legal aid clinic.\n"
            "3. For urgent police, detention, violence, or safety issues, contact a qualified advocate immediately.\n\n"
            "**Sources Checked**\n\n"
            f"{chr(10).join(source_lines) if source_lines else '- No matching source snippets were retrieved.'}\n\n"
            "**Disclaimer**\n\n"
            "This is educational information, not a substitute for advice from a qualified lawyer."
        )

    def transcribe_audio(self, audio_file):
        """Transcribes audio using Groq's Whisper API in a multilingual-aware manner."""
        try:
            from groq import Groq
            raw_key = os.getenv("GROQ_API_KEY", "").strip()
            if raw_key.startswith("ygsk_"):
                raw_key = raw_key[1:]
            if not raw_key:
                raise RuntimeError("GROQ_API_KEY is not configured.")
            client = Groq(api_key=raw_key)
            
            # Read recorded audio bytes
            audio_bytes = audio_file.read()
            
            # Send to Groq's transcription endpoint
            transcription = client.audio.transcriptions.create(
                file=("recorded_audio.wav", audio_bytes),
                model="whisper-large-v3",
                prompt="Indian legal grievance, Indian names, Constitution of India, Hindi, Marathi, Tamil, Telugu, Bengali",
                response_format="verbose_json"
            )
            text = getattr(transcription, "text", str(transcription))
            detected_lang = getattr(transcription, "language", "english")
            return {"text": text, "language": str(detected_lang)}
        except Exception as e:
            raise RuntimeError(f"Voice transcription failed: {str(e)}")
