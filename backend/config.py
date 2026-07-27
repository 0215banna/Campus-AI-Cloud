from pathlib import Path


OLLAMA_API_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "granite4:3b"

EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_API_URL = "http://host.docker.internal:11434/api/embed"

DATA_DIRECTORY = Path("/app/data")
DATABASE_PATH = DATA_DIRECTORY / "campus_ai.db"
KNOWLEDGE_PATH = DATA_DIRECTORY / "knowledge.json"