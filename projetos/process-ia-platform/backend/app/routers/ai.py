from fastapi import APIRouter
from ..schemas import AIQuestionRequest
from ..services.ai_service import generate_next_question

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/next-question")
def next_question(payload: AIQuestionRequest):
    result = generate_next_question(
        process_name=payload.process_name,
        process_context=payload.process_context,
        latest_answer=payload.latest_answer,
    )
    return {"result": result}
