"""
Dependency Injection Container
Manages service lifecycle, scoped resources, and provider registry.

This module provides a simple but powerful DI container for managing
application dependencies and services.
"""

from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar, get_type_hints

T = TypeVar("T")


class Scope(Enum):
    """Service lifecycle scopes."""

    SINGLETON = "singleton"  # One instance for entire application
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"  # One instance per request/scope


class ServiceDescriptor:
    """Describes a registered service."""

    def __init__(
        self,
        service_type: type,
        implementation: type | Callable[..., Any] | None = None,
        instance: Any = None,
        scope: Scope = Scope.TRANSIENT,
        factory: Callable[..., Any] | None = None,
    ):
        self.service_type = service_type
        self.implementation = implementation or service_type
        self.instance = instance
        self.scope = scope
        self.factory = factory


class Container:
    """
    Dependency Injection Container.

    Usage:
        container = Container()

        # Register services
        container.register(UserService)
        container.register(IUserRepository, UserRepository)
        container.register_singleton(DatabaseConnection, instance=db_conn)
        container.register_factory(CacheService, lambda: CacheService(redis_url))

        # Resolve services
        user_service = container.resolve(UserService)
    """

    def __init__(self) -> None:
        self._services: dict[type, ServiceDescriptor] = {}
        self._singletons: dict[type, Any] = {}
        self._scoped_instances: dict[str, dict[type, Any]] = {}
        self._current_scope: str | None = None

    def register(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        scope: Scope = Scope.TRANSIENT,
    ) -> "Container":
        """
        Register a service with the container.

        Args:
            service_type: The service interface/type
            implementation: The concrete implementation (optional, defaults to service_type)
            scope: Service lifecycle scope

        Returns:
            Self for method chaining
        """
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            scope=scope,
        )
        return self

    def register_singleton(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        instance: T | None = None,
    ) -> "Container":
        """
        Register a singleton service.

        Args:
            service_type: The service interface/type
            implementation: The concrete implementation
            instance: Pre-created instance (optional)

        Returns:
            Self for method chaining
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            instance=instance,
            scope=Scope.SINGLETON,
        )
        self._services[service_type] = descriptor

        if instance is not None:
            self._singletons[service_type] = instance

        return self

    def register_scoped(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
    ) -> "Container":
        """
        Register a scoped service (one instance per request/scope).

        Args:
            service_type: The service interface/type
            implementation: The concrete implementation

        Returns:
            Self for method chaining
        """
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            scope=Scope.SCOPED,
        )
        return self

    def register_factory(
        self,
        service_type: type[T],
        factory: Callable[..., T],
        scope: Scope = Scope.TRANSIENT,
    ) -> "Container":
        """
        Register a service with a factory function.

        Args:
            service_type: The service interface/type
            factory: Factory function to create instances
            scope: Service lifecycle scope

        Returns:
            Self for method chaining
        """
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            scope=scope,
        )
        return self

    def register_instance(
        self,
        service_type: type[T],
        instance: T,
    ) -> "Container":
        """
        Register a pre-created instance as singleton.

        Args:
            service_type: The service interface/type
            instance: The instance to register

        Returns:
            Self for method chaining
        """
        return self.register_singleton(service_type, instance=instance)

    def resolve(self, service_type: type[T]) -> T:
        """
        Resolve a service from the container.

        Args:
            service_type: The service type to resolve

        Returns:
            Instance of the requested service

        Raises:
            KeyError: If service is not registered
        """
        if service_type not in self._services:
            raise KeyError(f"Service '{service_type.__name__}' is not registered")

        descriptor = self._services[service_type]

        # Handle different scopes
        if descriptor.scope == Scope.SINGLETON:
            return self._resolve_singleton(service_type, descriptor)
        elif descriptor.scope == Scope.SCOPED:
            return self._resolve_scoped(service_type, descriptor)
        else:
            return self._create_instance(descriptor)

    def _resolve_singleton(
        self,
        service_type: type[T],
        descriptor: ServiceDescriptor,
    ) -> T:
        """Resolve or create a singleton instance."""
        if service_type not in self._singletons:
            self._singletons[service_type] = self._create_instance(descriptor)
        return self._singletons[service_type]

    def _resolve_scoped(
        self,
        service_type: type[T],
        descriptor: ServiceDescriptor,
    ) -> T:
        """Resolve or create a scoped instance."""
        if self._current_scope is None:
            raise RuntimeError("No active scope. Use 'with container.scope():' to create a scope.")

        scope_instances = self._scoped_instances.get(self._current_scope, {})

        if service_type not in scope_instances:
            scope_instances[service_type] = self._create_instance(descriptor)
            self._scoped_instances[self._current_scope] = scope_instances

        return scope_instances[service_type]

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create a new instance of a service."""
        # Use factory if available
        if descriptor.factory:
            return descriptor.factory()

        # Use pre-created instance
        if descriptor.instance is not None:
            return descriptor.instance

        # Create new instance with dependency injection
        impl = descriptor.implementation
        if impl is None:
            raise ValueError(f"No implementation for {descriptor.service_type.__name__}")

        # Get constructor dependencies
        try:
            hints = get_type_hints(impl.__init__)
            hints.pop("return", None)
        except Exception:
            hints = {}

        # Resolve dependencies
        kwargs: dict[str, Any] = {}
        for param_name, param_type in hints.items():
            if param_type in self._services:
                kwargs[param_name] = self.resolve(param_type)

        return impl(**kwargs)

    def scope(self, scope_id: str | None = None) -> "ScopeContext":
        """
        Create a new scope context.

        Args:
            scope_id: Optional scope identifier

        Returns:
            ScopeContext for use with 'with' statement

        Usage:
            with container.scope() as scope:
                service = scope.resolve(MyService)
        """
        return ScopeContext(self, scope_id)

    def is_registered(self, service_type: type) -> bool:
        """Check if a service is registered."""
        return service_type in self._services

    def unregister(self, service_type: type) -> bool:
        """
        Unregister a service from the container.

        Args:
            service_type: The service type to unregister

        Returns:
            True if service was unregistered, False if not found
        """
        if service_type in self._services:
            del self._services[service_type]
            self._singletons.pop(service_type, None)
            return True
        return False

    def clear(self) -> None:
        """Clear all registered services and instances."""
        self._services.clear()
        self._singletons.clear()
        self._scoped_instances.clear()

    def get_registered_services(self) -> list[type]:
        """Get list of all registered service types."""
        return list(self._services.keys())


class ScopeContext:
    """Context manager for scoped service resolution."""

    def __init__(self, container: Container, scope_id: str | None = None):
        self.container = container
        self.scope_id = scope_id or f"scope_{id(self)}"

    def __enter__(self) -> "ScopeContext":
        self.container._current_scope = self.scope_id
        self.container._scoped_instances[self.scope_id] = {}
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Cleanup scoped instances
        if self.scope_id in self.container._scoped_instances:
            del self.container._scoped_instances[self.scope_id]
        self.container._current_scope = None

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service within this scope."""
        return self.container.resolve(service_type)


# Global container instance
container = Container()


# FastAPI integration
def get_container() -> Container:
    """
    FastAPI dependency to get the container.

    Usage:
        @app.get("/items")
        async def get_items(container: Container = Depends(get_container)):
            service = container.resolve(ItemService)
            return service.get_all()
    """
    return container


class Inject:
    """
    Descriptor for automatic dependency injection in classes.

    Usage:
        class MyController:
            user_service: UserService = Inject(UserService)

            def get_users(self):
                return self.user_service.get_all()
    """

    def __init__(self, service_type: type[T]):
        self.service_type = service_type
        self._instance: T | None = None

    def __get__(self, obj: Any, objtype: type | None = None) -> T:
        if self._instance is None:
            self._instance = container.resolve(self.service_type)
        return self._instance


def inject(service_type: type[T]) -> Callable[[], T]:
    """
    FastAPI dependency for injecting services.

    Usage:
        @app.get("/users")
        async def get_users(
            user_service: UserService = Depends(inject(UserService))
        ):
            return user_service.get_all()
    """

    def _inject() -> T:
        return container.resolve(service_type)

    return _inject
