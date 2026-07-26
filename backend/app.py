from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests

app = FastAPI(
    title="Campus AI Cloud API",
    description="教育機関向け生成AIクラウドサービスのAPI",
    version="1.0.0",
)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "granite4:3b"


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
        description="AIに送信する質問",
        examples=["微分係数とは何ですか？"],
    )


class AskResponse(BaseModel):
    model: str
    question: str
    answer: str


@app.get("/")
def root():
    return {
        "service": "Campus AI Cloud",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/about")
def about():
    return {
        "name": "Campus AI Cloud",
        "llm": MODEL_NAME,
        "rag": "Enabled in Open WebUI",
        "purpose": "教育機関における学習支援",
    }


@app.get("/features")
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


@app.post("/ask", response_model=AskResponse)
def ask_ai(request: AskRequest):
    payload = {
        "model": MODEL_NAME,
        "prompt": (
            "あなたは教育機関向けの学習支援AIです。"
            "初学者にも分かる日本語で説明してください。\n\n"
            f"質問: {request.question}"
        ),
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        result = response.json()

        return AskResponse(
            model=MODEL_NAME,
            question=request.question,
            answer=result.get("response", "回答を取得できませんでした。"),
        )

    except requests.exceptions.ConnectionError as error:
        raise HTTPException(
            status_code=503,
            detail="Ollamaに接続できません。Ollamaが起動しているか確認してください。",
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