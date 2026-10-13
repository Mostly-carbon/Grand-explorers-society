
"""Application entry point for the Grand Explorers' Society API."""

import logging
import os
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.species_routes import router as species_router
from routes.taxa_routes import router as taxa_router


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

logger = logging.getLogger("ges.api")

APP_ENV = os.getenv("GES_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV == "production"

configured_origins = os.getenv("GES_ALLOWED_ORIGINS", "")

ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in configured_origins.split(",")
    if origin.strip()
]

if not IS_PRODUCTION and not ALLOWED_ORIGINS:
    ALLOWED_ORIGINS = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ]


def validate_allowed_origins(origins: list[str]) -> None:
    """Reject unsafe or malformed production CORS configuration."""

    if IS_PRODUCTION and not origins:
        raise RuntimeError(
            "GES_ALLOWED_ORIGINS must contain at least one valid origin."
        )

    for origin in origins:
        parsed = urlsplit(origin)

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.path
            or parsed.query
            or parsed.fragment
            or "*" in origin
        ):
            raise RuntimeError(
                f"Invalid GES_ALLOWED_ORIGINS entry: {origin!r}"
            )

        if IS_PRODUCTION and parsed.scheme != "https":
            raise RuntimeError(
                "Production CORS origins must use HTTPS."
            )

        try:
            _ = parsed.port
        except ValueError as exc:
            raise RuntimeError(
                f"Invalid port in GES_ALLOWED_ORIGINS: {origin!r}"
            ) from exc


validate_allowed_origins(ALLOWED_ORIGINS)


# ------------------------------------------------------------
# Security response headers
# ------------------------------------------------------------

def apply_security_headers(response):
    """Apply browser security headers to an API response."""

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

    if IS_PRODUCTION:
        # Assumes the public API is served exclusively over HTTPS.
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000"
        )

    return response


# ------------------------------------------------------------
# Application
# ------------------------------------------------------------

app = FastAPI(
    title="Grand Explorers' Society API",
    description=(
        "Production API for the Grand Explorers' Society "
        "species archive."
    ),
    version="1.0.0",
    debug=False,
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)


# ------------------------------------------------------------
# Middleware
# ------------------------------------------------------------

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Apply security headers to normal API responses."""

    response = await call_next(request)
    return apply_security_headers(response)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["Accept", "Content-Type"],
    max_age=600,
)


# ------------------------------------------------------------
# Error handling
# ------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return a safe response for invalid request parameters."""

    logger.info(
        "Invalid request: method=%s path=%s",
        request.method,
        request.url.path,
    )

    response = JSONResponse(
        status_code=422,
        content={"detail": "Invalid request parameters."},
    )
    return apply_security_headers(response)


@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Log internal failures without exposing details to clients."""

    logger.error(
        "Unhandled API exception: method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    response = JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )
    return apply_security_headers(response)


# ------------------------------------------------------------
# Production API routes
# ------------------------------------------------------------

app.include_router(species_router)
app.include_router(taxa_router)


# ------------------------------------------------------------
# Health / status endpoint
# ------------------------------------------------------------

@app.get("/")
def root():
    """Return a simple API status message."""

    return {"message": "Camp's standing"}
