from fastapi import APIRouter, Depends, Query, Request
from langchain_core.language_models import BaseChatModel

router = APIRouter(prefix="/ask", tags=["test"])


def get_llm(request: Request) -> BaseChatModel:
    return request.app.state.llm


@router.get("")
def prompt(
    prompt: str = Query(min_length=1, max_length=100), llm=Depends(get_llm)
) -> str:
    return llm.invoke(prompt).content
