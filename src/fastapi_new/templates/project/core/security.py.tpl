"""
Security Configuration
Handles JWT authentication, OAuth2, role-based access control, and security utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

# HTTP Bearer scheme (alternative)
bearer_scheme = HTTPBearer(auto_error=False)


# Token models
class TokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str  # Subject (usually user ID)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    type: str  # Token type: "access" or "refresh"
    roles: list[str] = []  # User roles
    scopes: list[str] = []  # Permission scopes


class TokenData(BaseModel):
    """Decoded token data."""

    user_id: str
    roles: list[str] = []
    scopes: list[str] = []


class TokenResponse(BaseModel):
    """Token response for API."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# Password utilities
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# JWT utilities
def create_access_token(
    subject: str,
    roles: list[str] | None = None,
    scopes: list[str] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: Token subject (usually user ID)
        roles: User roles for RBAC
        scopes: Permission scopes
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "roles": roles or [],
        "scopes": scopes or [],
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject: Token subject (usually user ID)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload with decoded data

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def create_tokens(
    user_id: str,
    roles: list[str] | None = None,
    scopes: list[str] | None = None,
) -> TokenResponse:
    """
    Create both access and refresh tokens.

    Args:
        user_id: User identifier
        roles: User roles
        scopes: Permission scopes

    Returns:
        TokenResponse with both tokens
    """
    access_token = create_access_token(user_id, roles, scopes)
    refresh_token = create_refresh_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# Dependencies
async def get_current_user_token(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    """
    Dependency to get current user from JWT token.

    Usage:
        @app.get("/me")
        async def get_me(token_data: TokenData = Depends(get_current_user_token)):
            return {"user_id": token_data.user_id}
    """
    payload = decode_token(token)

    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenData(
        user_id=payload.sub,
        roles=payload.roles,
        scopes=payload.scopes,
    )


async def get_optional_user_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TokenData | None:
    """
    Dependency to optionally get current user.
    Returns None if no valid token is provided.

    Usage:
        @app.get("/items")
        async def get_items(token_data: TokenData | None = Depends(get_optional_user_token)):
            if token_data:
                # User is authenticated
                pass
    """
    if not credentials:
        return None

    try:
        payload = decode_token(credentials.credentials)
        if payload.type != "access":
            return None
        return TokenData(
            user_id=payload.sub,
            roles=payload.roles,
            scopes=payload.scopes,
        )
    except HTTPException:
        return None


# Role-based access control
class RoleChecker:
    """
    Dependency class for role-based access control.

    Usage:
        @app.get("/admin", dependencies=[Depends(RoleChecker(["admin"]))])
        async def admin_only():
            return {"message": "Welcome admin"}
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        token_data: TokenData = Depends(get_current_user_token),
    ) -> TokenData:
        if not any(role in self.allowed_roles for role in token_data.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return token_data


class ScopeChecker:
    """
    Dependency class for scope-based access control.

    Usage:
        @app.get("/data", dependencies=[Depends(ScopeChecker(["read:data"]))])
        async def read_data():
            return {"data": "sensitive"}
    """

    def __init__(self, required_scopes: list[str]):
        self.required_scopes = required_scopes

    async def __call__(
        self,
        token_data: TokenData = Depends(get_current_user_token),
    ) -> TokenData:
        if not all(scope in token_data.scopes for scope in self.required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient scopes",
            )
        return token_data


# Rate limiting (simple in-memory implementation)
class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, use Redis-based rate limiting.

    Usage:
        rate_limiter = RateLimiter(requests=100, window=60)

        @app.get("/api/resource", dependencies=[Depends(rate_limiter)])
        async def get_resource():
            return {"data": "resource"}
    """

    def __init__(self, requests: int = 100, window: int = 60):
        self.requests = requests
        self.window = window
        self._cache: dict[str, list[float]] = {}

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _cleanup_old_requests(self, client_id: str) -> None:
        """Remove expired request timestamps."""
        if client_id not in self._cache:
            return

        cutoff = datetime.now(timezone.utc).timestamp() - self.window
        self._cache[client_id] = [
            ts for ts in self._cache[client_id] if ts > cutoff
        ]

    async def __call__(self, request: Request) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return

        client_id = self._get_client_id(request)
        self._cleanup_old_requests(client_id)

        if client_id not in self._cache:
            self._cache[client_id] = []

        if len(self._cache[client_id]) >= self.requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(self.window)},
            )

        self._cache[client_id].append(datetime.now(timezone.utc).timestamp())


# Default rate limiter instance
default_rate_limiter = RateLimiter(
    requests=settings.RATE_LIMIT_REQUESTS,
    window=settings.RATE_LIMIT_WINDOW,
)


# Convenience functions for common role checks
def require_admin() -> Any:
    """Dependency to require admin role."""
    return Depends(RoleChecker(["admin"]))


def require_staff() -> Any:
    """Dependency to require staff or admin role."""
    return Depends(RoleChecker(["admin", "staff"]))


def require_authenticated() -> Any:
    """Dependency to require any authenticated user."""
    return Depends(get_current_user_token)
