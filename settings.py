import os

MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "competencies")
TOP_N = int(os.getenv("TOP_N", 3))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.4))
MAX_COURSES = int(os.getenv("MAX_COURSES", 5))
COMPETENCY_DATA_PATH = os.getenv(
    "COMPETENCY_DATA_PATH", "./data/openai_result - competencies.csv"
)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o")
