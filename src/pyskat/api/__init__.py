from fastapi.routing import APIRouter

from pyskat.api import player
from pyskat.api import match
from pyskat.api import session
from pyskat.api import result

__all__ = ["router"]

router = APIRouter()

router.include_router(player.router)
router.include_router(match.router)
router.include_router(session.router)
router.include_router(result.router)
