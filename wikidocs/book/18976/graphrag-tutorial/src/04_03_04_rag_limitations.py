from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from util import (
    default_embedding_model,
    default_llm_model,
    ensure_project_root_on_path,
    format_docs,
    split_texts,
)

ensure_project_root_on_path()

from data.documents import DOCUMENTS

# RAG 시스템 구축 (위와 동일)
chunks = split_texts(DOCUMENTS, chunk_size=150, chunk_overlap=30)

embeddings = OpenAIEmbeddings(model=default_embedding_model())
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_texts(chunks)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

template = """컨텍스트를 바탕으로 질문에 답하세요.

컨텍스트:
{context}

질문: {question}

답변:"""

prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model=default_llm_model(), temperature=0)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 한계를 보여주는 질문들
difficult_questions = [
    # 관계 추론 필요
    "세종대왕과 집현전의 관계는 무엇인가요?",

    # 다단계 추론 필요
    "세종대왕이 설치한 기관에서 누가 활동했나요?",

    # 비교 질문
    "세종대왕과 정조의 공통점은 무엇인가요?",

    # 시간순 나열
    "조선의 왕들을 시대순으로 나열해주세요.",
]

print("=" * 60)
print("전통 RAG의 한계 테스트")
print("=" * 60)

for q in difficult_questions:
    print(f"\n질문: {q}")

    # 검색된 문서 확인
    docs = retriever.invoke(q)
    print("\n[검색된 문서]")
    for i, doc in enumerate(docs, 1):
        print(f"  {i}. {doc.page_content[:50]}...")

    # 답변 생성
    answer = rag_chain.invoke(q)
    print(f"\n[답변]\n{answer}")
    print("-" * 60)
