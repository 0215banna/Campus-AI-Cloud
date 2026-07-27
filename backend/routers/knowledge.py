import io
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader

from config import EMBEDDING_MODEL
from rag import (
    create_embedding,
    load_knowledge,
    save_knowledge,
    split_text,
)


router = APIRouter(
    prefix="/knowledge",
    tags=["教材管理"],
)


@router.post("/upload")
async def upload_knowledge(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="ファイル名を確認できません。",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="PDFファイルのみ登録できます。",
        )

    try:
        file_data = await file.read()
        reader = PdfReader(io.BytesIO(file_data))

        page_texts = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text()

            if text and text.strip():
                page_texts.append(
                    {
                        "page": page_number,
                        "text": text.strip(),
                    }
                )

        if not page_texts:
            raise HTTPException(
                status_code=400,
                detail="PDFから文字を抽出できませんでした。",
            )

        knowledge = load_knowledge()
        added_chunks = 0

        for page_data in page_texts:
            chunks = split_text(
                page_data["text"]
            )

            for chunk_number, chunk in enumerate(
                chunks,
                start=1,
            ):
                embedding = create_embedding(chunk)

                knowledge.append(
                    {
                        "filename": file.filename,
                        "page": page_data["page"],
                        "chunk": chunk_number,
                        "text": chunk,
                        "embedding": embedding,
                        "created_at": datetime.now().isoformat(
                            timespec="seconds"
                        ),
                    }
                )

                added_chunks += 1

        save_knowledge(knowledge)

        return {
            "message": "教材PDFを登録しました。",
            "filename": file.filename,
            "pages": len(page_texts),
            "added_chunks": added_chunks,
            "total_chunks": len(knowledge),
            "embedding_model": EMBEDDING_MODEL,
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF登録中にエラーが発生しました: {error}",
        ) from error