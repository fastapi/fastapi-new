"""
Custom Exceptions
Application-wide exception classes and exception handlers.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


# Base exception class
class AppException(Exception):
    """
    Base exception for all application exceptions.

    Usage:
        raise AppException("Something went wrong", code="ERR_001")
    """

    def __init__(
        self,
        message: str = "An error occurred",
        code: str | None = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code or "APP_ERROR"
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


# HTTP Exceptions
class BadRequestException(AppException):
    """400 Bad Request"""

    def __init__(
        self,
        message: str = "Bad request",
        code: str = "BAD_REQUEST",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class UnauthorizedException(AppException):
    """401 Unauthorized"""

    def __init__(
        self,
        message: str = "Unauthorized",
        code: str = "UNAUTHORIZED",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class ForbiddenException(AppException):
    """403 Forbidden"""

    def __init__(
        self,
        message: str = "Forbidden",
        code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundException(AppException):
    """404 Not Found"""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class ConflictException(AppException):
    """409 Conflict"""

    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class ValidationException(AppException):
    """422 Unprocessable Entity"""

    def __init__(
        self,
        message: str = "Validation error",
        code: str = "VALIDATION_ERROR",
        details: dict[str, Any] | None = None,
        errors: list[dict[str, Any]] | None = None,
    ):
        if errors:
            details = details or {}
            details["errors"] = errors
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class RateLimitException(AppException):
    """429 Too Many Requests"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "RATE_LIMIT_EXCEEDED",
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


class InternalServerException(AppException):
    """500 Internal Server Error"""

    def __init__(
        self,
        message: str = "Internal server error",
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ServiceUnavailableException(AppException):
    """503 Service Unavailable"""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        code: str = "SERVICE_UNAVAILABLE",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


# Domain-specific exceptions
class DatabaseException(AppException):
    """Database operation error"""

    def __init__(
        self,
        message: str = "Database error",
        code: str = "DATABASE_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class AuthenticationException(AppException):
    """Authentication error"""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTH_FAILED",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class PermissionDeniedException(AppException):
    """Permission denied error"""

    def __init__(
        self,
        message: str = "Permission denied",
        code: str = "PERMISSION_DENIED",
        required_permission: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class EntityNotFoundException(NotFoundException):
    """Specific entity not found"""

    def __init__(
        self,
        entity_type: str,
        entity_id: str | int | None = None,
        message: str | None = None,
    ):
        if message is None:
            if entity_id:
                message = f"{entity_type} with id '{entity_id}' not found"
            else:
                message = f"{entity_type} not found"

        super().__init__(
            message=message,
            code=f"{entity_type.upper()}_NOT_FOUND",
            details={"entity_type": entity_type, "entity_id": entity_id},
        )


class DuplicateEntityException(ConflictException):
    """Entity already exists"""

    def __init__(
        self,
        entity_type: str,
        field: str | None = None,
        value: Any = None,
        message: str | None = None,
    ):
        if message is None:
            if field and value:
                message = f"{entity_type} with {field}='{value}' already exists"
            else:
                message = f"{entity_type} already exists"

        super().__init__(
            message=message,
            code=f"{entity_type.upper()}_ALREADY_EXISTS",
            details={"entity_type": entity_type, "field": field, "value": value},
        )


# Exception handlers
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for AppException and its subclasses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers with the FastAPI application.

    Usage:
        from app.shared.exceptions import register_exception_handlers

        app = FastAPI()
        register_exception_handlers(app)
    """
    app.add_exception_handler(AppException, app_exception_handler)
    # Uncomment the following line to catch all unhandled exceptions
    # app.add_exception_handler(Exception, generic_exception_handler)
