import json

import numpy as np
import requests
from fastapi import HTTPException

from config import (
    EMBEDDING_API_URL,
    EMBEDDING_MODEL,
    KNOWLEDGE_PATH,
)


def load_knowledge() -> list[dict]:
    if not KNOWLEDGE_PATH.exists():
        return []

    with KNOWLEDGE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_knowledge(knowledge: list[dict]) -> None:
    KNOWLEDGE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with KNOWLEDGE_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            knowledge,
            file,
            ensure_ascii=False,
        )


def split_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_embedding(text: str) -> list[float]:
    try:
        response = requests.post(
            EMBEDDING_API_URL,
            json={
                "model": EMBEDDING_MODEL,
                "input": text,
            },
            timeout=180,
        )
        response.raise_for_status()

        result = response.json()
        embeddings = result.get("embeddings", [])

        if not embeddings:
            raise HTTPException(
                status_code=500,
                detail="埋め込みベクトルを取得できませんでした。",
            )

        return embeddings[0]

    except requests.exceptions.ConnectionError as error:
        raise HTTPException(
            status_code=503,
            detail="Ollamaの埋め込みAPIに接続できません。",
        ) from error

    except requests.exceptions.Timeout as error:
        raise HTTPException(
            status_code=504,
            detail="埋め込み処理がタイムアウトしました。",
        ) from error

    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=500,
            detail=f"埋め込み処理中にエラーが発生しました: {error}",
        ) from error


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    array_a = np.array(vector_a)
    array_b = np.array(vector_b)

    denominator = (
        np.linalg.norm(array_a)
        * np.linalg.norm(array_b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(array_a, array_b) / denominator
    )


def search_knowledge(
    question: str,
    top_k: int = 3,
) -> list[dict]:
    knowledge = load_knowledge()

    if not knowledge:
        return []

    question_embedding = create_embedding(question)
    scored_documents = []

    for item in knowledge:
        score = cosine_similarity(
            question_embedding,
            item["embedding"],
        )

        scored_documents.append(
            {
                "score": score,
                "text": item["text"],
                "page": item["page"],
                "filename": item["filename"],
            }
        )

    scored_documents.sort(
        key=lambda document: document["score"],
        reverse=True,
    )

    return scored_documents[:top_k]