import sys
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.documents import DOCUMENTS

# 텍스트 분할기 생성
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,        # 청크 최대 크기
    chunk_overlap=20,      # 청크 간 겹침
    length_function=len,
)

# 문서 분할
all_chunks = []
for doc in DOCUMENTS:
    chunks = text_splitter.split_text(doc)
    all_chunks.extend(chunks)

print(f"원본 문서 수: {len(DOCUMENTS)}")
print(f"분할된 청크 수: {len(all_chunks)}")
print("\n처음 3개 청크:")
for i, chunk in enumerate(all_chunks[:3]):
    print(f"\n[청크 {i+1}]")
    print(chunk)
