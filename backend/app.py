from fastapi import FastAPI, HTTPException

from database import get_history, initialize_database
from routers import chat, dashboard, knowledge, system


app = FastAPI(
    title="Campus AI Cloud API",
    description="教育機関向け生成AIクラウドサービスのAPI",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    initialize_database()


@app.get("/history", tags=["履歴"])
def history(limit: int = 20):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail=(
                "limitは1から100の範囲で"
                "指定してください。"
            ),
        )

    rows = get_history(limit)

    return {
        "count": len(rows),
        "history": rows,
    }


app.include_router(system.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(dashboard.router)