"""
CivicPulse AI — Global Error Handling.

Provides consistent error responses across the API.

SECURITY:
- Raw Python stack traces are NEVER exposed to clients.
- Internal error details are logged server-side only.
- Error responses use a consistent structure.
"""

from __future__ import annotations

import logging
import traceback
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("civicpulse.errors")


def error_response(
    status_code: int,
    error: str,
    detail: str | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    """
    Create a consistent error JSON response.

    Args:
        status_code: HTTP status code.
        error: Short error identifier.
        detail: Human-readable description (safe to show to client).
        request_id: Correlation ID for log tracing.
    """
    body: Dict[str, Any] = {
        "status": "error",
        "error": error,
    }
    if detail:
        body["detail"] = detail
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(status_code=status_code, content=body)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle standard HTTP exceptions."""
        request_id = getattr(request.state, "request_id", None)
        return error_response(
            status_code=exc.status_code,
            error="http_error",
            detail=str(exc.detail),
            request_id=request_id,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors with safe details."""
        request_id = getattr(request.state, "request_id", None)
        # Provide validation error details but not raw internals
        errors = []
        for err in exc.errors():
            errors.append({
                "field": " → ".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", "Validation error"),
                "type": err.get("type", "unknown"),
            })
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "error": "validation_error",
                "detail": "Request validation failed.",
                "errors": errors,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all for unhandled exceptions.

        Logs full stack trace server-side but returns a safe
        response to the client.
        """
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            "Unhandled exception [request_id=%s]: %s\n%s",
            request_id,
            str(exc),
            traceback.format_exc(),
        )
        return error_response(
            status_code=500,
            error="internal_error",
            detail="An internal error occurred. Please try again later.",
            request_id=request_id,
        )
