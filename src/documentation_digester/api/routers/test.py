from fastapi import APIRouter, Depends, HTTPException, Query, status

router = APIRouter(prefix="/test", tags=["test"])


# query param: http://localhost:8000/test?name=Test
@router.get("")
def get_students_by_name(
    name: str = Query(min_length=1, max_length=100),
) -> str:
    return "Hello"
