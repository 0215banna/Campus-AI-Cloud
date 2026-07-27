import requests
from fastapi import APIRouter, HTTPException

from config import MODEL_NAME, OLLAMA_API_URL
from database import save_history
from models import AskRequest, AskResponse
from rag import search_knowledge


router = APIRouter(
    tags=["AIチャット"],
)


def generate_answer(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()

        result = response.json()

        return result.get(
            "response",
            "回答を取得できませんでした。",
        )

    except requests.exceptions.ConnectionError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                "Ollamaに接続できません。"
                "Ollamaが起動しているか確認してください。"
            ),
        ) from error

    except requests.exceptions.Timeout as error:
        raise HTTPException(
            status_code=504,
            detail="AIの回答生成がタイムアウトしました。",
        ) from error

    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=500,
            detail=f"AIへの接続中にエラーが発生しました: {error}",
        ) from error


@router.post(
    "/ask",
    response_model=AskResponse,
)
def ask_ai(request: AskRequest):
    prompt = (
        "あなたは教育機関向けの学習支援AIです。"
        "初学者にも分かる日本語で回答してください。\n\n"
        f"質問: {request.question}"
    )

    answer = generate_answer(prompt)

    save_history(
        question=request.question,
        answer=answer,
    )

    return AskResponse(
        model=MODEL_NAME,
        question=request.question,
        answer=answer,
    )


@router.post("/ask-rag")
def ask_rag(request: AskRequest):
    documents = search_knowledge(
        request.question
    )

    if not documents:
        raise HTTPException(
            status_code=404,
            detail="登録された教材がありません。",
        )

    context_parts = []

    for document in documents:
        context_parts.append(
            (
                f"資料名: {document['filename']}\n"
                f"ページ: {document['page']}\n"
                f"内容:\n{document['text']}"
            )
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
あなたは教育機関向けの学習支援AIです。

以下の教材だけを参考にして回答してください。
教材に答えがない場合は、
「登録教材からは確認できませんでした」と回答してください。

【教材】
{context}

【質問】
{request.question}
"""

    answer = generate_answer(prompt)

    save_history(
        question=request.question,
        answer=answer,
    )

    return {
        "model": MODEL_NAME,
        "question": request.question,
        "answer": answer,
        "references": documents,
    }