"""
Service Registry for Agent Runner.

This module acts as a central repository for system singletons, breaking circular
dependency chains between components (e.g., AgentRunner <-> BackgroundTasks <-> HealthMonitor).

It provides strictly typed accessors for the core services.
"""
from typing import Optional, Any, TYPE_CHECKING
import logging

logger = logging.getLogger("agent_runner.registry")

if TYPE_CHECKING:
    from agent_runner.state import AgentState
    from agent_runner.engine import AgentEngine
    from agent_runner.background_tasks import BackgroundTaskManager

class ServiceRegistry:
    _state: Optional['AgentState'] = None
    _engine: Optional['AgentEngine'] = None
    _task_manager: Optional['BackgroundTaskManager'] = None
    
    @classmethod
    def register_state(cls, state: 'AgentState') -> None:
        cls._state = state
        
    @classmethod
    def register_engine(cls, engine: 'AgentEngine') -> None:
        cls._engine = engine
        
    @classmethod
    def register_task_manager(cls, task_manager: 'BackgroundTaskManager') -> None:
        cls._task_manager = task_manager
        
    @classmethod
    def get_state(cls) -> 'AgentState':
        if cls._state is None:
            raise RuntimeError("AgentState not initialized in registry")
        return cls._state
        
    @classmethod
    def get_engine(cls) -> 'AgentEngine':
        if cls._engine is None:
            raise RuntimeError("AgentEngine not initialized in registry")
        return cls._engine

    @classmethod
    def get_task_manager(cls) -> 'BackgroundTaskManager':
        if cls._task_manager is None:
            raise RuntimeError("BackgroundTaskManager not initialized in registry")
        return cls._task_manager

    # Memory Server (Phase 13 additions)
    _memory_server: Any = None

    @classmethod
    def register_memory_server(cls, server: Any) -> None:
        cls._memory_server = server

    @classmethod
    def get_memory_server(cls) -> Any:
        # Allow None (optional dependency) to avoid crash loops if DB is down
        return cls._memory_server

# Helper functions for cleaner imports
def get_shared_state() -> 'AgentState':
    return ServiceRegistry.get_state()

def get_shared_engine() -> 'AgentEngine':
    return ServiceRegistry.get_engine()

def get_task_manager() -> 'BackgroundTaskManager':
    return ServiceRegistry.get_task_manager()
