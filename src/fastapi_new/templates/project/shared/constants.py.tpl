"""
Application Constants
Centralized constants used across the application.
"""

from enum import Enum, IntEnum
from typing import Final


# HTTP Status Messages
class HTTPStatus:
    """Standard HTTP status messages."""

    OK: Final[str] = "OK"
    CREATED: Final[str] = "Created"
    ACCEPTED: Final[str] = "Accepted"
    NO_CONTENT: Final[str] = "No Content"
    BAD_REQUEST: Final[str] = "Bad Request"
    UNAUTHORIZED: Final[str] = "Unauthorized"
    FORBIDDEN: Final[str] = "Forbidden"
    NOT_FOUND: Final[str] = "Not Found"
    METHOD_NOT_ALLOWED: Final[str] = "Method Not Allowed"
    CONFLICT: Final[str] = "Conflict"
    UNPROCESSABLE_ENTITY: Final[str] = "Unprocessable Entity"
    TOO_MANY_REQUESTS: Final[str] = "Too Many Requests"
    INTERNAL_SERVER_ERROR: Final[str] = "Internal Server Error"
    SERVICE_UNAVAILABLE: Final[str] = "Service Unavailable"


# Error Codes
class ErrorCode:
    """Application error codes."""

    # General errors (1xxx)
    UNKNOWN_ERROR: Final[str] = "ERR_1000"
    VALIDATION_ERROR: Final[str] = "ERR_1001"
    NOT_FOUND: Final[str] = "ERR_1002"
    CONFLICT: Final[str] = "ERR_1003"
    BAD_REQUEST: Final[str] = "ERR_1004"

    # Authentication errors (2xxx)
    AUTH_FAILED: Final[str] = "ERR_2000"
    TOKEN_EXPIRED: Final[str] = "ERR_2001"
    TOKEN_INVALID: Final[str] = "ERR_2002"
    CREDENTIALS_INVALID: Final[str] = "ERR_2003"
    SESSION_EXPIRED: Final[str] = "ERR_2004"

    # Authorization errors (3xxx)
    PERMISSION_DENIED: Final[str] = "ERR_3000"
    INSUFFICIENT_ROLE: Final[str] = "ERR_3001"
    INSUFFICIENT_SCOPE: Final[str] = "ERR_3002"

    # Database errors (4xxx)
    DATABASE_ERROR: Final[str] = "ERR_4000"
    DUPLICATE_ENTRY: Final[str] = "ERR_4001"
    FOREIGN_KEY_ERROR: Final[str] = "ERR_4002"
    CONNECTION_ERROR: Final[str] = "ERR_4003"

    # External service errors (5xxx)
    EXTERNAL_SERVICE_ERROR: Final[str] = "ERR_5000"
    TIMEOUT_ERROR: Final[str] = "ERR_5001"
    RATE_LIMIT_ERROR: Final[str] = "ERR_5002"


# User Roles
class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "admin"
    STAFF = "staff"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


# Account Status
class AccountStatus(str, Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    DELETED = "deleted"


# Sort Order
class SortOrder(str, Enum):
    """Sort order for queries."""

    ASC = "asc"
    DESC = "desc"


# Pagination
class Pagination:
    """Default pagination settings."""

    DEFAULT_PAGE: Final[int] = 1
    DEFAULT_PAGE_SIZE: Final[int] = 20
    MIN_PAGE_SIZE: Final[int] = 1
    MAX_PAGE_SIZE: Final[int] = 100


# Time Constants (in seconds)
class TimeConstants:
    """Time-related constants in seconds."""

    SECOND: Final[int] = 1
    MINUTE: Final[int] = 60
    HOUR: Final[int] = 3600
    DAY: Final[int] = 86400
    WEEK: Final[int] = 604800
    MONTH: Final[int] = 2592000  # 30 days
    YEAR: Final[int] = 31536000  # 365 days


# Cache TTL (in seconds)
class CacheTTL:
    """Cache time-to-live constants."""

    SHORT: Final[int] = 60  # 1 minute
    MEDIUM: Final[int] = 300  # 5 minutes
    LONG: Final[int] = 3600  # 1 hour
    DAY: Final[int] = 86400  # 24 hours
    WEEK: Final[int] = 604800  # 7 days


# File Size Limits (in bytes)
class FileSizeLimit:
    """File size limit constants."""

    KB: Final[int] = 1024
    MB: Final[int] = 1024 * 1024
    GB: Final[int] = 1024 * 1024 * 1024

    MAX_IMAGE_SIZE: Final[int] = 5 * MB  # 5 MB
    MAX_DOCUMENT_SIZE: Final[int] = 10 * MB  # 10 MB
    MAX_VIDEO_SIZE: Final[int] = 100 * MB  # 100 MB
    MAX_UPLOAD_SIZE: Final[int] = 50 * MB  # 50 MB


# Content Types
class ContentType:
    """Common MIME content types."""

    JSON: Final[str] = "application/json"
    HTML: Final[str] = "text/html"
    TEXT: Final[str] = "text/plain"
    XML: Final[str] = "application/xml"
    PDF: Final[str] = "application/pdf"
    FORM: Final[str] = "application/x-www-form-urlencoded"
    MULTIPART: Final[str] = "multipart/form-data"
    OCTET_STREAM: Final[str] = "application/octet-stream"

    # Images
    PNG: Final[str] = "image/png"
    JPEG: Final[str] = "image/jpeg"
    GIF: Final[str] = "image/gif"
    WEBP: Final[str] = "image/webp"
    SVG: Final[str] = "image/svg+xml"


# Allowed File Extensions
class AllowedExtensions:
    """Allowed file extensions by category."""

    IMAGES: Final[frozenset[str]] = frozenset({".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"})
    DOCUMENTS: Final[frozenset[str]] = frozenset({".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"})
    VIDEOS: Final[frozenset[str]] = frozenset({".mp4", ".avi", ".mov", ".wmv", ".webm"})
    AUDIO: Final[frozenset[str]] = frozenset({".mp3", ".wav", ".ogg", ".flac"})
    ARCHIVES: Final[frozenset[str]] = frozenset({".zip", ".tar", ".gz", ".rar", ".7z"})


# HTTP Headers
class Headers:
    """Common HTTP header names."""

    AUTHORIZATION: Final[str] = "Authorization"
    CONTENT_TYPE: Final[str] = "Content-Type"
    ACCEPT: Final[str] = "Accept"
    USER_AGENT: Final[str] = "User-Agent"
    X_REQUEST_ID: Final[str] = "X-Request-ID"
    X_FORWARDED_FOR: Final[str] = "X-Forwarded-For"
    X_REAL_IP: Final[str] = "X-Real-IP"
    X_API_KEY: Final[str] = "X-API-Key"
    X_RATE_LIMIT: Final[str] = "X-RateLimit-Limit"
    X_RATE_REMAINING: Final[str] = "X-RateLimit-Remaining"
    X_RATE_RESET: Final[str] = "X-RateLimit-Reset"


# Regex Patterns
class Patterns:
    """Common regex patterns."""

    EMAIL: Final[str] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    PHONE: Final[str] = r"^\+?[1-9]\d{1,14}$"
    URL: Final[str] = r"^https?://[^\s/$.?#].[^\s]*$"
    UUID: Final[str] = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    SLUG: Final[str] = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    USERNAME: Final[str] = r"^[a-zA-Z0-9_]{3,30}$"
    PASSWORD_STRONG: Final[str] = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    IPV4: Final[str] = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    DATE_ISO: Final[str] = r"^\d{4}-\d{2}-\d{2}$"
    DATETIME_ISO: Final[str] = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"


# API Version
class APIVersion:
    """API versioning constants."""

    V1: Final[str] = "v1"
    V2: Final[str] = "v2"
    CURRENT: Final[str] = V1
    PREFIX: Final[str] = "/api"


# Environment
class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"
    TESTING = "test"


# Database
class DatabaseEngine(str, Enum):
    """Supported database engines."""

    POSTGRESQL = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


# Message Templates
class Messages:
    """Common message templates."""

    # Success messages
    CREATED: Final[str] = "{entity} created successfully"
    UPDATED: Final[str] = "{entity} updated successfully"
    DELETED: Final[str] = "{entity} deleted successfully"
    FETCHED: Final[str] = "{entity} retrieved successfully"

    # Error messages
    NOT_FOUND: Final[str] = "{entity} not found"
    ALREADY_EXISTS: Final[str] = "{entity} already exists"
    INVALID_INPUT: Final[str] = "Invalid input provided"
    UNAUTHORIZED: Final[str] = "Authentication required"
    FORBIDDEN: Final[str] = "You don't have permission to perform this action"
    SERVER_ERROR: Final[str] = "An unexpected error occurred"


# Task Status
class TaskStatus(str, Enum):
    """Background task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Priority Levels
class Priority(IntEnum):
    """Priority levels for tasks/notifications."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5
