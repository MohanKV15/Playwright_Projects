# ==============================================================================
# Enterprise Senior QA RAG (Retrieval-Augmented Generation) Engine
# Framework: LangChain + ChromaDB + OpenAI Embeddings
# Workspace: All 4 NJDOT Playwright Projects
# ==============================================================================

import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger("QARagEngine")

class QARagEngine:
    """
    Enterprise RAG Engine designed for Playwright Automation Suites.
    Indexes Page Objects, test data schemas, and feature files across all 4 projects
    to provide AI-assisted failure diagnostics, self-healing insights, and script generation.
    """

    def __init__(self, workspace_root: Path = None):
        self.workspace_root = workspace_root or Path(__file__).resolve().parent.parent
        self.chroma_db_dir = self.workspace_root / "reports" / "chroma_db"
        try:
            from dotenv import load_dotenv
            load_dotenv(self.workspace_root / ".env")
        except Exception:
            pass
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.vector_store = None

    def is_available(self) -> bool:
        """Check if OpenAI API Key is configured and dependencies are loadable."""
        if not self.openai_api_key:
            return False
        try:
            import langchain_openai
            import chromadb
            return True
        except ImportError:
            return False

    def _get_embeddings_and_llm(self):
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=self.openai_api_key)
        llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=self.openai_api_key)
        return embeddings, llm

    def index_workspace(self) -> dict:
        """
        Scans and indexes all Page Objects (`pages/`), test data (`testdata/`),
        and feature files across all 4 sub-projects into ChromaDB.
        """
        if not self.is_available():
            logger.warning("OPENAI_API_KEY or RAG dependencies missing. Skipping workspace indexing.")
            return {"status": "skipped", "reason": "Missing OPENAI_API_KEY or dependencies"}

        from langchain_community.document_loaders import DirectoryLoader, TextLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import Chroma

        embeddings, _ = self._get_embeddings_and_llm()

        sub_projects = [
            "NJDOT_EPermitting_Customer_Portal",
            "NJDOT_EPermitting_Staff_Portal",
            "NJDOT_ODA_Customer_Portal",
            "NJDOT_ODA_Staff_Portal",
            "IDOT_ODA_Customer_Portal",
            "IDOT_ODA_Staff_Portal",
        ]

        documents = []
        indexed_files_count = 0

        for project in sub_projects:
            project_dir = self.workspace_root / project
            if not project_dir.exists():
                continue

            # Load Page Objects (.py)
            pages_dir = project_dir / "pages"
            if pages_dir.exists():
                loader = DirectoryLoader(str(pages_dir), glob="**/*.py", loader_cls=TextLoader, show_progress=False)
                try:
                    loaded = loader.load()
                    documents.extend(loaded)
                    indexed_files_count += len(loaded)
                except Exception as e:
                    logger.debug(f"Note loading {pages_dir}: {e}")

            # Load Test Data (.json)
            testdata_dir = project_dir / "testdata"
            if testdata_dir.exists():
                loader = DirectoryLoader(str(testdata_dir), glob="**/*.json", loader_cls=TextLoader, show_progress=False)
                try:
                    loaded = loader.load()
                    documents.extend(loaded)
                    indexed_files_count += len(loaded)
                except Exception as e:
                    logger.debug(f"Note loading {testdata_dir}: {e}")

        if not documents:
            return {"status": "empty", "files_indexed": 0}

        # Split documents into optimal RAG chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        splits = text_splitter.split_documents(documents)

        # Create or overwrite ChromaDB vector store
        self.chroma_db_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=str(self.chroma_db_dir)
        )

        logger.info(f"[RAG ENGINE] Indexed {indexed_files_count} files ({len(splits)} chunks) into ChromaDB.")
        return {"status": "success", "files_indexed": indexed_files_count, "chunks": len(splits)}

    def analyze_failure(self, test_name: str, failure_trace: str, page_url: str = None, dom_snippet: str = None) -> str:
        """
        Performs RAG-based root cause analysis on a Playwright test failure,
        retrieving relevant Page Object context to output exact solution suggestions.
        """
        if not self.is_available():
            return "RAG Diagnostics inactive (OPENAI_API_KEY not set)."

        from langchain_community.vectorstores import Chroma
        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate

        embeddings, llm = self._get_embeddings_and_llm()

        if not self.chroma_db_dir.exists():
            self.index_workspace()

        vector_store = Chroma(
            persist_directory=str(self.chroma_db_dir),
            embedding_function=embeddings
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": 4})

        system_prompt = (
            "You are a Senior Playwright SDET Architect analyzing a test failure.\n"
            "Use the retrieved Page Object context below to pinpoint the exact failure cause and recommend the exact line/locator fix.\n\n"
            "RETRIEVED PAGE OBJECT CONTEXT:\n{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Test Name: {test_name}\nTarget URL: {page_url}\nFailure Trace:\n{failure_trace}\n\nDOM Snippet:\n{dom_snippet}"),
        ])

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        try:
            response = rag_chain.invoke({
                "input": "Analyze Playwright test failure and suggest fix",
                "test_name": test_name,
                "page_url": page_url or "Unknown",
                "failure_trace": failure_trace[:3000],
                "dom_snippet": (dom_snippet or "")[:1500]
            })
            return response.get("answer", "No analysis generated.")
        except Exception as e:
            return f"RAG analysis error: {e}"

    def generate_test_script(self, requirement_prompt: str, target_project: str = "NJDOT_EPermitting_Customer_Portal") -> str:
        """
        Generates a complete Pytest + Playwright script using existing indexed Page Objects.
        """
        if not self.is_available():
            return "# Error: OPENAI_API_KEY not set. Cannot run RAG generation."

        from langchain_community.vectorstores import Chroma

        embeddings, llm = self._get_embeddings_and_llm()
        vector_store = Chroma(
            persist_directory=str(self.chroma_db_dir),
            embedding_function=embeddings
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        matching_docs = retriever.invoke(requirement_prompt)

        context_code = "\n\n".join([doc.page_content for doc in matching_docs])

        system_prompt = f"""
        You are an Expert Senior Playwright Python SDET Architect.
        Generate a production-grade Pytest + Playwright test script for target project '{target_project}'.
        Strictly use existing Page Object classes and method signatures from the context below. Do NOT invent raw locators.
        
        RETRIEVED CONTEXT PAGE OBJECTS:
        {context_code}
        
        USER TEST REQUIREMENT:
        {requirement_prompt}
        """

        response = llm.invoke(system_prompt)
        return response.content
