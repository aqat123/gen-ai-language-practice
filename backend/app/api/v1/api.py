from fastapi import APIRouter
from app.api.v1.endpoints import (
    greeting,
    auth,
    placement_test,
    conversation,
    vocabulary,
    grammar,
    writing,
    phonetics,
    progress,
    achievements,
    llm_config
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(greeting.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(placement_test.router, prefix="/placement-test", tags=["placement-test"])
api_router.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["vocabulary"])
api_router.include_router(grammar.router, prefix="/grammar", tags=["grammar"])
api_router.include_router(writing.router, prefix="/writing", tags=["writing"])
api_router.include_router(phonetics.router, prefix="/phonetics", tags=["phonetics"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["achievements"])
api_router.include_router(llm_config.router, prefix="/llm-config", tags=["llm-config"])
