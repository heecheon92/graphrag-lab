import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.documents import DOCUMENTS


load_dotenv(PROJECT_ROOT / ".env")


def require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"{key} is missing. Add it to .env or your shell environment.")
    return val

# 1. 문서 분할 및 벡터 저장소 구축
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30,
)

chunks = []
for doc in DOCUMENTS:
    chunks.extend(text_splitter.split_text(doc))

embeddings = OpenAIEmbeddings(model=require_env("OPENAI_DEFAULT_EMBEDDING_MODEL"))
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_texts(chunks)

# 2. 검색기 생성
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 3. 프롬프트 템플릿
template = """다음 컨텍스트를 바탕으로 질문에 답해주세요.
컨텍스트에 없는 내용은 "해당 정보를 찾을 수 없습니다"라고 답하세요.

컨텍스트:
{context}

질문: {question}

답변:"""

prompt = ChatPromptTemplate.from_template(template)

# 4. LLM 설정
llm = ChatOpenAI(model=require_env("OPENAI_DEFAULT_LLM_MODEL"), temperature=0)

# 5. RAG 체인 구성
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 6. 질문하기
questions = [
    "세종대왕이 발명한 것들은 무엇인가요?",
    "정조는 어떤 정책을 실시했나요?",
    "이순신 장군의 명량해전에 대해 알려주세요.",
]

print("=" * 60)
print("RAG 시스템 테스트")
print("=" * 60)

for q in questions:
    print(f"\n질문: {q}")
    answer = rag_chain.invoke(q)
    print(f"답변: {answer}")
    print("-" * 60)
