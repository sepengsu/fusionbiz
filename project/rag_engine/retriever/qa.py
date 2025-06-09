from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_openai import ChatOpenAI
from collections import Counter
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import json

def get_qa_chunks(question: str, what: str = "sql", device=None) -> dict:
    db_dir = "data/manual" if what == "manual" else "data/sqlguide"
    vector_dir = f"{db_dir}/vector_store"

    try:
        with open(f"{vector_dir}/meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
    except FileNotFoundError:
        return {
            "question": question,
            "text": "벡터 스토어 메타 정보를 찾을 수 없습니다.",
            "retrieved_docs": []
        }

    try:
        source, model = meta["embedding_model"].split("/")
        if source == "openai":
            embeddings = OpenAIEmbeddings(model=model)
        elif source == "sentence-transformers":
            embeddings = HuggingFaceEmbeddings(model_name=model)
        else:
            raise ValueError(f"지원하지 않는 임베딩 모델: {source}")

        if meta["vector_type"] == "FAISS":
            vectordb = FAISS.load_local(vector_dir, embeddings)
        elif meta["vector_type"] == "Chroma":
            vectordb = Chroma(persist_directory=vector_dir, embedding_function=embeddings)
        else:
            raise ValueError(f"지원하지 않는 벡터 타입: {meta['vector_type']}")

        k = meta.get("top_k", 5)
        retriever = vectordb.as_retriever(search_type="similarity_score_threshold", search_kwargs={'k': k, 'score_threshold': 0.1})
        retrieved_docs = retriever.get_relevant_documents(question)

        print(f"[DEBUG] 📘 검색된 청크 개수: {len(retrieved_docs)}")

        if not retrieved_docs:
            return {
                "question": question,
                "text": "관련 컨텍스트가 없습니다.",
                "retrieved_docs": []
            }

        context = "\n".join([doc.page_content for doc in retrieved_docs])
        return {
            "question": question,
            "text": context,
            "retrieved_docs": retrieved_docs
        }

    except Exception as e:
        return {
            "question": question,
            "text": f"[ERROR] {str(e)}",
            "retrieved_docs": []
        }

