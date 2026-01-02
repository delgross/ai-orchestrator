from fastapi import APIRouter
from .chat import router as chat_router
from .models import router as models_router
from .embeddings import router as embeddings_router
from .audio import router as audio_router
from .files import router as files_router
from .misc import router as misc_router
from .rag_proxy import router as rag_proxy_router

# Base router to aggregate all specialized routes
router = APIRouter()

router.include_router(chat_router)
router.include_router(models_router)
router.include_router(embeddings_router)
router.include_router(audio_router)
router.include_router(files_router)
router.include_router(misc_router)
router.include_router(rag_proxy_router)
