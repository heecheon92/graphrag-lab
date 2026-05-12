from util import ensure_project_root_on_path, split_texts

ensure_project_root_on_path()

from data.documents import DOCUMENTS

# 문서 분할
all_chunks = split_texts(DOCUMENTS, chunk_size=100, chunk_overlap=20)

print(f"원본 문서 수: {len(DOCUMENTS)}")
print(f"분할된 청크 수: {len(all_chunks)}")
print("\n처음 3개 청크:")
for i, chunk in enumerate(all_chunks[:3]):
    print(f"\n[청크 {i+1}]")
    print(chunk)
