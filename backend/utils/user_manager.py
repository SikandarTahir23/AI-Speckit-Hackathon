"""
User Manager (Hackathon Bonus Feature 1)

Handles user registration, validation, and lifecycle events.
"""

from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from utils.config import settings


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    User manager for handling authentication lifecycle.

    Extends FastAPI-Users BaseUserManager with custom validation
    and event handling for user registration.
    """

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Event handler called after successful user registration.

        Args:
            user: The newly registered user
            request: The request context (optional)
        """
        print(f"User {user.id} ({user.email}) has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Event handler for password reset requests.

        Args:
            user: The user requesting password reset
            token: The reset token
            request: The request context (optional)
        """
        print(f"User {user.id} has forgotten their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Event handler for email verification requests.

        Args:
            user: The user requesting verification
            token: The verification token
            request: The request context (optional)
        """
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_password(
        self,
        password: str,
        user: User,
    ) -> None:
        """
        Validate password strength.

        Password must meet minimum requirements defined in settings.

        Args:
            password: The password to validate
            user: The user context

        Raises:
            InvalidPasswordException: If password doesn't meet requirements
        """
        # Minimum length check (from settings.PASSWORD_MIN_LENGTH)
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(
                f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long"
            )

        # Additional strength checks (FR-006 from spec.md)
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
