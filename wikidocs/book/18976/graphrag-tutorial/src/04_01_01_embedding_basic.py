from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# 환경 변수 로드
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 텍스트를 임베딩으로 변환
text = "오늘 날씨가 정말 좋습니다."
vector = embeddings.embed_query(text)

# 결과 확인
print(f"입력 텍스트: {text}")
print(f"벡터 차원: {len(vector)}")
print(f"벡터 앞부분: {vector[:5]}")
