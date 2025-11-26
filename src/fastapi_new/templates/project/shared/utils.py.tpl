"""
Shared Utilities
Common utility functions and helpers used across the application.
"""

import hashlib
import re
import secrets
import string
import uuid
from datetime import datetime, timezone
from typing import Any, TypeVar

T = TypeVar("T")


# String utilities
def generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    Generate a short random ID.

    Args:
        length: Length of the ID (default: 8)

    Returns:
        Random alphanumeric string
    """
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_token(length: int = 32) -> str:
    """
    Generate a secure random token.

    Args:
        length: Length of the token in bytes (default: 32)

    Returns:
        URL-safe token string
    """
    return secrets.token_urlsafe(length)


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Input text

    Returns:
        Slugified string

    Example:
        slugify("Hello World!") -> "hello-world"
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r"\s+", "-", text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^a-z0-9\-]", "", text)
    # Remove multiple consecutive hyphens
    text = re.sub(r"-+", "-", text)
    # Strip leading/trailing hyphens
    return text.strip("-")


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.

    Args:
        text: Input text
        length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated string
    """
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix


def snake_case(text: str) -> str:
    """
    Convert text to snake_case.

    Args:
        text: Input text (CamelCase or space-separated)

    Returns:
        snake_case string
    """
    # Insert underscore before uppercase letters
    text = re.sub(r"([A-Z])", r"_\1", text)
    # Replace spaces and hyphens with underscores
    text = re.sub(r"[\s\-]+", "_", text)
    # Remove leading underscore and convert to lowercase
    return text.lstrip("_").lower()


def camel_case(text: str) -> str:
    """
    Convert text to camelCase.

    Args:
        text: Input text (snake_case or space-separated)

    Returns:
        camelCase string
    """
    # Split by underscores, spaces, or hyphens
    words = re.split(r"[_\s\-]+", text)
    if not words:
        return ""
    # First word lowercase, rest capitalized
    return words[0].lower() + "".join(word.capitalize() for word in words[1:])


def pascal_case(text: str) -> str:
    """
    Convert text to PascalCase.

    Args:
        text: Input text (snake_case or space-separated)

    Returns:
        PascalCase string
    """
    words = re.split(r"[_\s\-]+", text)
    return "".join(word.capitalize() for word in words)


# Hash utilities
def md5_hash(data: str) -> str:
    """Generate MD5 hash of string."""
    return hashlib.md5(data.encode()).hexdigest()


def sha256_hash(data: str) -> str:
    """Generate SHA256 hash of string."""
    return hashlib.sha256(data.encode()).hexdigest()


def hash_file(file_path: str) -> str:
    """
    Generate SHA256 hash of a file.

    Args:
        file_path: Path to the file

    Returns:
        SHA256 hash string
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


# Date/Time utilities
def utc_now() -> datetime:
    """Get current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def timestamp_now() -> int:
    """Get current Unix timestamp (seconds)."""
    return int(datetime.now(timezone.utc).timestamp())


def timestamp_ms() -> int:
    """Get current Unix timestamp (milliseconds)."""
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.

    Args:
        dt: Datetime object
        fmt: Format string (default: ISO-like format)

    Returns:
        Formatted datetime string
    """
    return dt.strftime(fmt)


def parse_datetime(date_string: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse datetime from string.

    Args:
        date_string: Date string to parse
        fmt: Expected format

    Returns:
        Parsed datetime object
    """
    return datetime.strptime(date_string, fmt).replace(tzinfo=timezone.utc)


def time_ago(dt: datetime) -> str:
    """
    Get human-readable time difference from now.

    Args:
        dt: Datetime to compare

    Returns:
        Human-readable string like "5 minutes ago"
    """
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = seconds // 604800
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = seconds // 2592000
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = seconds // 31536000
        return f"{years} year{'s' if years != 1 else ''} ago"


# Collection utilities
def chunk_list(lst: list[T], size: int) -> list[list[T]]:
    """
    Split list into chunks of specified size.

    Args:
        lst: Input list
        size: Chunk size

    Returns:
        List of chunks
    """
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def flatten(nested: list[list[T]]) -> list[T]:
    """
    Flatten a nested list.

    Args:
        nested: Nested list

    Returns:
        Flattened list
    """
    return [item for sublist in nested for item in sublist]


def unique(lst: list[T]) -> list[T]:
    """
    Remove duplicates while preserving order.

    Args:
        lst: Input list

    Returns:
        List with duplicates removed
    """
    seen: set[Any] = set()
    result: list[T] = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def first(lst: list[T] | None, default: T | None = None) -> T | None:
    """
    Get first element of list or default.

    Args:
        lst: Input list
        default: Default value if list is empty

    Returns:
        First element or default
    """
    if not lst:
        return default
    return lst[0]


def last(lst: list[T] | None, default: T | None = None) -> T | None:
    """
    Get last element of list or default.

    Args:
        lst: Input list
        default: Default value if list is empty

    Returns:
        Last element or default
    """
    if not lst:
        return default
    return lst[-1]


# Dictionary utilities
def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Dictionary to merge (takes precedence)

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def pick(d: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """
    Pick specific keys from dictionary.

    Args:
        d: Input dictionary
        keys: Keys to pick

    Returns:
        Dictionary with only specified keys
    """
    return {k: v for k, v in d.items() if k in keys}


def omit(d: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """
    Omit specific keys from dictionary.

    Args:
        d: Input dictionary
        keys: Keys to omit

    Returns:
        Dictionary without specified keys
    """
    return {k: v for k, v in d.items() if k not in keys}


def get_nested(d: dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get nested dictionary value by dot-notation path.

    Args:
        d: Input dictionary
        path: Dot-notation path (e.g., "user.profile.name")
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    keys = path.split(".")
    result: Any = d
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    return result


def set_nested(d: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """
    Set nested dictionary value by dot-notation path.

    Args:
        d: Input dictionary
        path: Dot-notation path (e.g., "user.profile.name")
        value: Value to set

    Returns:
        Modified dictionary
    """
    keys = path.split(".")
    current = d
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return d


# Validation utilities
def is_valid_email(email: str) -> bool:
    """Check if string is a valid email address."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL."""
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url, re.IGNORECASE))


def is_valid_uuid(value: str) -> bool:
    """Check if string is a valid UUID."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def is_valid_phone(phone: str) -> bool:
    """Check if string is a valid phone number (basic validation)."""
    pattern = r"^\+?1?\d{9,15}$"
    return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))


# Sanitization utilities
def sanitize_html(text: str) -> str:
    """
    Remove HTML tags from string.

    Args:
        text: Input text with possible HTML

    Returns:
        Text with HTML tags removed
    """
    return re.sub(r"<[^>]+>", "", text)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Input filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    # Remove leading/trailing dots and spaces
    return sanitized.strip(". ")


# Mask utilities
def mask_email(email: str) -> str:
    """
    Mask email address for privacy.

    Args:
        email: Email address

    Returns:
        Masked email (e.g., "j***n@example.com")
    """
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*" * (len(local) - 1)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy.

    Args:
        phone: Phone number

    Returns:
        Masked phone (e.g., "****1234")
    """
    digits = re.sub(r"\D", "", phone)
    if len(digits) <= 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]


def mask_card(card_number: str) -> str:
    """
    Mask credit card number.

    Args:
        card_number: Credit card number

    Returns:
        Masked card (e.g., "**** **** **** 1234")
    """
    digits = re.sub(r"\D", "", card_number)
    if len(digits) < 4:
        return "*" * len(digits)
    return "**** **** **** " + digits[-4:]
