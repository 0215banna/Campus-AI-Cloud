from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from config import MODEL_NAME
from database import get_history
from rag import load_knowledge


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard_page():
    knowledge = load_knowledge()
    history = get_history(limit=10)

    filenames = sorted(
        {
            item["filename"]
            for item in knowledge
        }
    )

    file_list_html = "".join(
        f"<li>{escape(filename)}</li>"
        for filename in filenames
    )

    if not file_list_html:
        file_list_html = (
            "<li>登録された教材はありません。</li>"
        )

    history_list_html = "".join(
        (
            "<li>"
            f"{escape(row['question'])}"
            "</li>"
        )
        for row in history
    )

    if not history_list_html:
        history_list_html = (
            "<li>質問履歴はありません。</li>"
        )

    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >
        <title>Campus AI Cloud</title>

        <style>
            body {{
                margin: 0;
                background: #f4f6f8;
                font-family: Arial, sans-serif;
                color: #222;
            }}

            header {{
                background: #243447;
                color: white;
                padding: 24px 40px;
            }}

            main {{
                max-width: 1000px;
                margin: 30px auto;
                padding: 0 20px;
            }}

            .cards {{
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}

            .card,
            section {{
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow:
                    0 2px 8px rgba(0, 0, 0, 0.08);
            }}

            section {{
                margin-bottom: 24px;
            }}

            .number {{
                font-size: 28px;
                font-weight: bold;
            }}

            li {{
                margin: 10px 0;
            }}

            a {{
                color: #1769aa;
            }}
        </style>
    </head>

    <body>
        <header>
            <h1>Campus AI Cloud</h1>
            <p>学校向け生成AI基盤 管理ダッシュボード</p>
        </header>

        <main>
            <div class="cards">
                <div class="card">
                    <h2>使用モデル</h2>
                    <div class="number">
                        {escape(MODEL_NAME)}
                    </div>
                </div>

                <div class="card">
                    <h2>登録教材数</h2>
                    <div class="number">
                        {len(filenames)}
                    </div>
                </div>

                <div class="card">
                    <h2>質問履歴数</h2>
                    <div class="number">
                        {len(history)}
                    </div>
                </div>

                <div class="card">
                    <h2>登録チャンク数</h2>
                    <div class="number">
                        {len(knowledge)}
                    </div>
                </div>
            </div>

            <section>
                <h2>登録教材</h2>
                <ul>{file_list_html}</ul>
            </section>

            <section>
                <h2>最近の質問</h2>
                <ul>{history_list_html}</ul>
            </section>

            <section>
                <h2>APIメニュー</h2>
                <p>
                    <a href="/docs">
                        Swagger API画面
                    </a>
                </p>
                <p>
                    <a href="/history">
                        質問履歴
                    </a>
                </p>
                <p>
                    <a href="/dashboard">
                        統計情報
                    </a>
                </p>
            </section>
        </main>
    </body>
    </html>
    """

    return HTMLResponse(content=html)