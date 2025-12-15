"""
Authentication Configuration (Hackathon Bonus Feature 1)

FastAPI-Users setup with cookie-based authentication and JWT strategy.
"""

from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from utils.config import settings


# Cookie transport configuration
# Session persists for 7 days (SESSION_MAX_AGE from .env)
cookie_transport = CookieTransport(
    cookie_name="auth_token",
    cookie_max_age=settings.SESSION_MAX_AGE,  # 7 days in seconds
    cookie_secure=False,  # Set to True in production with HTTPS
    cookie_httponly=True,  # Prevent JavaScript access (XSS protection)
    cookie_samesite="lax",  # CSRF protection
)


def get_jwt_strategy() -> JWTStrategy:
    """
    JWT strategy for token generation and validation.

    Returns:
        JWTStrategy configured with secret key and token lifetime
    """
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.SESSION_MAX_AGE,  # 7 days
    )


# Authentication backend combining transport and strategy
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
