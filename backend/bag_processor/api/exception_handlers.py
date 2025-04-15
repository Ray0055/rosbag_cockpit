from fastapi import Request
from fastapi.responses import JSONResponse

from ..bag_manager.error import BagPlaybackBusyError


def register_exception_handlers(app):
    @app.exception_handler(BagPlaybackBusyError)
    async def busy_exception_handler(request: Request, exc: BagPlaybackBusyError):
        return JSONResponse(
            status_code=1001, content={"detail": str(exc), "error_code": exc.error_code}
        )
