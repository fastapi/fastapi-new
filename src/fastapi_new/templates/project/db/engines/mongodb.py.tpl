"""
MongoDB Database Engine Configuration
Provides MongoDB-specific database setup and utilities.

MongoDB is a NoSQL document database, ideal for flexible schemas
and horizontal scaling.
"""

from typing import Any, TypeVar

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings


T = TypeVar("T")


def get_mongodb_url() -> str:
    """
    Get MongoDB connection URL.

    Returns:
        MongoDB connection string
    """
    return settings.DATABASE_URL


def get_database_name() -> str:
    """
    Extract database name from the connection URL.

    Returns:
        Database name
    """
    url = settings.DATABASE_URL
    # Extract database name from URL like mongodb://user:pass@host:port/dbname
    if "/" in url:
        parts = url.rsplit("/", 1)
        if len(parts) > 1:
            db_name = parts[1].split("?")[0]  # Remove query params
            if db_name:
                return db_name
    return "app_database"


def get_connection_options() -> dict[str, Any]:
    """
    Get MongoDB connection options.

    Returns:
        Dictionary of connection options
    """
    return {
        "maxPoolSize": settings.DATABASE_POOL_SIZE,
        "minPoolSize": 1,
        "maxIdleTimeMS": 30000,  # 30 seconds
        "connectTimeoutMS": 10000,  # 10 seconds
        "serverSelectionTimeoutMS": 5000,  # 5 seconds
        "retryWrites": True,
        "retryReads": True,
    }


# Sync client (pymongo)
sync_client: MongoClient | None = None

# Async client (motor)
async_client: AsyncIOMotorClient | None = None


def get_sync_client() -> MongoClient:
    """
    Get or create sync MongoDB client.

    Returns:
        MongoClient instance
    """
    global sync_client
    if sync_client is None:
        sync_client = MongoClient(
            get_mongodb_url(),
            **get_connection_options(),
        )
    return sync_client


def get_async_client() -> AsyncIOMotorClient:
    """
    Get or create async MongoDB client.

    Returns:
        AsyncIOMotorClient instance
    """
    global async_client
    if async_client is None:
        async_client = AsyncIOMotorClient(
            get_mongodb_url(),
            **get_connection_options(),
        )
    return async_client


def get_database() -> Database:
    """
    Get sync database instance.

    Returns:
        Database instance
    """
    client = get_sync_client()
    return client[get_database_name()]


def get_async_database() -> AsyncIOMotorDatabase:
    """
    Get async database instance.

    Returns:
        AsyncIOMotorDatabase instance
    """
    client = get_async_client()
    return client[get_database_name()]


def get_collection(collection_name: str) -> Collection:
    """
    Get sync collection by name.

    Args:
        collection_name: Name of the collection

    Returns:
        Collection instance
    """
    db = get_database()
    return db[collection_name]


def get_async_collection(collection_name: str) -> AsyncIOMotorCollection:
    """
    Get async collection by name.

    Args:
        collection_name: Name of the collection

    Returns:
        AsyncIOMotorCollection instance
    """
    db = get_async_database()
    return db[collection_name]


# FastAPI dependencies
def get_db() -> Database:
    """
    Sync database dependency for FastAPI.

    Usage:
        @app.get("/items")
        def get_items(db: Database = Depends(get_db)):
            return list(db.items.find())
    """
    return get_database()


async def get_async_db() -> AsyncIOMotorDatabase:
    """
    Async database dependency for FastAPI.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncIOMotorDatabase = Depends(get_async_db)):
            cursor = db.items.find()
            return await cursor.to_list(length=100)
    """
    return get_async_database()


# MongoDB-specific utilities
async def check_connection() -> bool:
    """
    Check if MongoDB connection is healthy.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        client = get_async_client()
        await client.admin.command("ping")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError):
        return False


async def get_database_version() -> str | None:
    """
    Get MongoDB server version.

    Returns:
        Version string or None if connection fails
    """
    try:
        client = get_async_client()
        server_info = await client.server_info()
        return server_info.get("version")
    except Exception:
        return None


async def get_database_stats() -> dict[str, Any] | None:
    """
    Get database statistics.

    Returns:
        Dictionary with database stats or None if query fails
    """
    try:
        db = get_async_database()
        return await db.command("dbStats")
    except Exception:
        return None


async def get_database_size() -> str | None:
    """
    Get the size of the database.

    Returns:
        Human-readable database size or None if query fails
    """
    try:
        stats = await get_database_stats()
        if stats:
            size_bytes = stats.get("dataSize", 0)
            for unit in ["B", "KB", "MB", "GB"]:
                if size_bytes < 1024:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.2f} TB"
    except Exception:
        pass
    return None


async def collection_exists(collection_name: str) -> bool:
    """
    Check if a collection exists in the database.

    Args:
        collection_name: Name of the collection

    Returns:
        True if collection exists, False otherwise
    """
    try:
        db = get_async_database()
        collections = await db.list_collection_names()
        return collection_name in collections
    except Exception:
        return False


async def get_all_collections() -> list[str]:
    """
    Get list of all collections in the database.

    Returns:
        List of collection names
    """
    try:
        db = get_async_database()
        return await db.list_collection_names()
    except Exception:
        return []


async def get_collection_stats(collection_name: str) -> dict[str, Any] | None:
    """
    Get statistics for a collection.

    Args:
        collection_name: Name of the collection

    Returns:
        Dictionary with collection stats or None
    """
    try:
        db = get_async_database()
        return await db.command("collStats", collection_name)
    except Exception:
        return None


async def get_collection_count(collection_name: str) -> int:
    """
    Get document count for a collection.

    Args:
        collection_name: Name of the collection

    Returns:
        Document count
    """
    try:
        collection = get_async_collection(collection_name)
        return await collection.count_documents({})
    except Exception:
        return 0


async def create_index(
    collection_name: str,
    keys: list[tuple[str, int]],
    unique: bool = False,
    sparse: bool = False,
    background: bool = True,
    name: str | None = None,
) -> str | None:
    """
    Create an index on a collection.

    Args:
        collection_name: Name of the collection
        keys: List of (field_name, direction) tuples. Direction: 1 for ascending, -1 for descending
        unique: If True, create a unique index
        sparse: If True, only index documents that contain the field
        background: If True, create index in background
        name: Optional index name

    Returns:
        Index name or None if creation fails

    Example:
        await create_index("users", [("email", 1)], unique=True)
        await create_index("products", [("category", 1), ("price", -1)])
    """
    try:
        collection = get_async_collection(collection_name)
        index_opts: dict[str, Any] = {
            "unique": unique,
            "sparse": sparse,
            "background": background,
        }
        if name:
            index_opts["name"] = name
        return await collection.create_index(keys, **index_opts)
    except Exception:
        return None


async def drop_index(collection_name: str, index_name: str) -> bool:
    """
    Drop an index from a collection.

    Args:
        collection_name: Name of the collection
        index_name: Name of the index to drop

    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_async_collection(collection_name)
        await collection.drop_index(index_name)
        return True
    except Exception:
        return False


async def get_indexes(collection_name: str) -> list[dict[str, Any]]:
    """
    Get all indexes for a collection.

    Args:
        collection_name: Name of the collection

    Returns:
        List of index information dictionaries
    """
    try:
        collection = get_async_collection(collection_name)
        cursor = collection.list_indexes()
        return await cursor.to_list(length=None)
    except Exception:
        return []


# CRUD helper functions
async def insert_one(collection_name: str, document: dict[str, Any]) -> str | None:
    """
    Insert a single document.

    Args:
        collection_name: Name of the collection
        document: Document to insert

    Returns:
        Inserted document ID as string or None
    """
    try:
        collection = get_async_collection(collection_name)
        result = await collection.insert_one(document)
        return str(result.inserted_id)
    except Exception:
        return None


async def insert_many(collection_name: str, documents: list[dict[str, Any]]) -> list[str]:
    """
    Insert multiple documents.

    Args:
        collection_name: Name of the collection
        documents: List of documents to insert

    Returns:
        List of inserted document IDs as strings
    """
    try:
        collection = get_async_collection(collection_name)
        result = await collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    except Exception:
        return []


async def find_one(
    collection_name: str,
    filter: dict[str, Any],
    projection: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """
    Find a single document.

    Args:
        collection_name: Name of the collection
        filter: Query filter
        projection: Optional projection

    Returns:
        Document or None
    """
    try:
        collection = get_async_collection(collection_name)
        return await collection.find_one(filter, projection)
    except Exception:
        return None


async def find_many(
    collection_name: str,
    filter: dict[str, Any],
    projection: dict[str, Any] | None = None,
    sort: list[tuple[str, int]] | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Find multiple documents.

    Args:
        collection_name: Name of the collection
        filter: Query filter
        projection: Optional projection
        sort: Optional sort specification
        skip: Number of documents to skip
        limit: Maximum number of documents to return

    Returns:
        List of documents
    """
    try:
        collection = get_async_collection(collection_name)
        cursor = collection.find(filter, projection)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    except Exception:
        return []


async def update_one(
    collection_name: str,
    filter: dict[str, Any],
    update: dict[str, Any],
    upsert: bool = False,
) -> int:
    """
    Update a single document.

    Args:
        collection_name: Name of the collection
        filter: Query filter
        update: Update operations
        upsert: If True, insert if document doesn't exist

    Returns:
        Number of modified documents
    """
    try:
        collection = get_async_collection(collection_name)
        result = await collection.update_one(filter, update, upsert=upsert)
        return result.modified_count
    except Exception:
        return 0


async def update_many(
    collection_name: str,
    filter: dict[str, Any],
    update: dict[str, Any],
    upsert: bool = False,
) -> int:
    """
    Update multiple documents.

    Args:
        collection_name: Name of the collection
        filter: Query filter
        update: Update operations
        upsert: If True, insert if no documents match

    Returns:
        Number of modified documents
    """
    try:
        collection = get_async_collection(collection_name)
        result = await collection.update_many(filter, update, upsert=upsert)
        return result.modified_count
    except Exception:
        return 0


async def delete_one(collection_name: str, filter: dict[str, Any]) -> int:
    """
    Delete a single document.

    Args:
        collection_name: Name of the collection
        filter: Query filter

    Returns:
        Number of deleted documents
    """
    try:
        collection = get_async_collection(collection_name)
        result = await collection.delete_one(filter)
        return result.deleted_count
    except Exception:
        return 0


async def delete_many(collection_name: str, filter: dict[str, Any]) -> int:
    """
    Delete multiple documents.

    Args:
        collection_name: Name of the collection
        filter: Query filter

    Returns:
        Number of deleted documents
    """
    try:
        collection = get_async_collection(collection_name)
        result = await collection.delete_many(filter)
        return result.deleted_count
    except Exception:
        return 0


async def aggregate(
    collection_name: str,
    pipeline: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Run an aggregation pipeline.

    Args:
        collection_name: Name of the collection
        pipeline: Aggregation pipeline stages

    Returns:
        List of results
    """
    try:
        collection = get_async_collection(collection_name)
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
    except Exception:
        return []


# Connection lifecycle
async def close_connections() -> None:
    """Close all MongoDB connections."""
    global sync_client, async_client

    if sync_client:
        sync_client.close()
        sync_client = None

    if async_client:
        async_client.close()
        async_client = None


def close_sync_connection() -> None:
    """Close sync MongoDB connection."""
    global sync_client
    if sync_client:
        sync_client.close()
        sync_client = None
