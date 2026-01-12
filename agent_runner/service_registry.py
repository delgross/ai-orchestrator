from typing import Any

class ServiceRegistry:
    """
    Singleton registry for holding shared state/engine instances.
    Migrated from agent_runner/registry.py to break dependency cycles and support Sovereign unification.
    """
    _state = None
    _engine = None
    _memory_server = None
    _task_manager = None

    @classmethod
    def register_state(cls, state):
        cls._state = state

    @classmethod
    def get_state(cls):
        if cls._state is None:
            raise RuntimeError("AgentState not yet registered")
        return cls._state

    @classmethod
    def register_engine(cls, engine):
        cls._engine = engine

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            raise RuntimeError("AgentEngine not yet registered")
        return cls._engine

    @classmethod
    def register_memory_server(cls, server: Any) -> None:
        """Register the MemoryServer singleton."""
        cls._memory_server = server

    @classmethod
    def get_memory_server(cls) -> Any:
        """Get the MemoryServer instance."""
        if cls._memory_server is None:
            raise RuntimeError("MemoryServer not yet registered")
        return cls._memory_server

    @classmethod
    def register_task_manager(cls, manager: Any) -> None:
        """Register the TaskManager singleton."""
        cls._task_manager = manager

    @classmethod
    def get_task_manager(cls) -> Any:
        """Get the TaskManager instance."""
        if cls._task_manager is None:
            raise RuntimeError("TaskManager not yet registered")
        return cls._task_manager
