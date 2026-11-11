from documentation_digester.service.search_service import UserStoryHit

# TEMPORARY: stands in for the real Postgres/vector repository until the
# embedding issue lands. Delete this file and swap it out in get_search_service.
_STORIES: list[UserStoryHit] = [
    {
        "user_story_id": "1",
        "title": "Connect a signal to a node",
        "text": "As a developer, I want to connect a signal to a node method so that nodes react to events.",
    },
    {
        "user_story_id": "2",
        "title": "Instance a scene at runtime",
        "text": "As a developer, I want to instance a scene from code so that I can spawn objects while the game runs.",
    },
    {
        "user_story_id": "3",
        "title": "Organize nodes in a scene tree",
        "text": "As a developer, I want to arrange nodes in a scene tree so that I can build reusable game objects.",
    },
]


class FakeUserStoryRepository:
    def has_stories(self) -> bool:
        return True

    def search(self, question: str, limit: int) -> list[UserStoryHit]:
        return _STORIES[:limit]
