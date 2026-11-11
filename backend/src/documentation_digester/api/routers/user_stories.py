from fastapi import APIRouter, Depends

from documentation_digester.api.routers.documents import get_user_story_repo
from documentation_digester.repository.user_story_repo import UserStoryRepo

router = APIRouter(prefix="/user-stories", tags=["User Stories"])

@router.post("/index")
def index_user_stories(
    repo: UserStoryRepo = Depends(get_user_story_repo),
) -> dict[str, int]:
    return {"indexed": repo.index_all()}