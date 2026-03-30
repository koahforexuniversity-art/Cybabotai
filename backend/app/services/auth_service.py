"""Authentication service with JWT token management."""

from datetime import datetime, timedelta
from typing import Any
import cuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.models.user import User

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    def hash_password(self, password: str) -> str:
        """Hash a plain text password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: str, email: str, role: str) -> str:
        """Create a JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        payload: dict[str, Any] = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}") from e

    async def register_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        name: str | None = None,
    ) -> User:
        """Register a new user."""
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        user = User(
            id=cuid.cuid(),
            email=email,
            name=name,
            password_hash=self.hash_password(password),
            credits_balance=settings.free_tier_credits,
            role="user",
        )
        db.add(user)
        await db.flush()
        return user

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User | None:
        """Authenticate a user with email and password."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not self.verify_password(password, user.password_hash):
            return None

        return user
