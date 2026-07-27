from fastapi import APIRouter

from config import MODEL_NAME
from database import count_history


router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "healthy",
    }


@router.get("/about")
def about():
    return {
        "name": "Campus AI Cloud",
        "llm": MODEL_NAME,
        "rag": "Enabled",
        "purpose": "教育機関における学習支援",
    }


@router.get("/features")
def features():
    return {
        "features": [
            "AIチャット",
            "教材PDF検索（RAG）",
            "学校専用AIアシスタント",
            "FastAPIバックエンド",
            "Docker Compose",
            "Open WebUI",
        ]
    }


@router.get("/dashboard")
def dashboard():
    return {
        "service": "Campus AI Cloud",
        "status": "running",
        "model": MODEL_NAME,
        "rag": "Enabled",
        "version": "1.0.0",
        "questions": count_history(),
    }