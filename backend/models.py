from pydantic import BaseModel, Field


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