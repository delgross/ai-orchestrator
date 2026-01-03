
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ToggleDefinition:
    key: str
    name: str
    description: str
    options: List[str]
    default: str
    requires_admin: bool = False

@dataclass
class RoleDefinition:
    role_id: str
    name: str
    description: str
    default_model: str

class SystemRegistry:
    """
    The Single Source of Truth for system capabilities, configuration toggles,
    and architectural definitions.
    """
    
    # --- TOGGLES ---
    _toggles: List[ToggleDefinition] = [
        ToggleDefinition(
            key="router_mode",
            name="Router Mode",
            description="Control how the Router processes requests. 'sync' waits for completion, 'async' returns immediately.",
            options=["sync", "async"],
            default="sync"
        ),
        ToggleDefinition(
            key="policy:internet",
            name="Internet Access",
            description="Global killswitch for external web access.",
            options=["enabled", "local_only"],
            default="enabled",
            requires_admin=True
        ),
        ToggleDefinition(
            key="policy:safety",
            name="Safety Protocols",
            description="Strictness of content filtering and guardrails.",
            options=["strict", "moderate", "off"],
            default="moderate",
            requires_admin=True
        ),
        ToggleDefinition(
            key="agent_runner:enable_command_execution",
            name="Developer Mode (Command Exec)",
            description="Allow the Agent to execute arbitrary shell commands via tool_run_command.",
            options=["true", "false"],
            default="false",
            requires_admin=True
        )
    ]

    # --- ROLES ---
    _roles: List[RoleDefinition] = [
        RoleDefinition("agent", "Primary Agent", "General purpose reasoning and task execution.", "xai:grok-3"),
        RoleDefinition("router", "Router", "Routing requests and Intent classification.", "ollama:mistral"),
        RoleDefinition("maitre_d", "Maître d'", "Tool selection and precision.", "ollama:llama3.1"),
        RoleDefinition("healer", "Diagnostician", "Log analysis and error diagnosis.", "xai:grok-2"),
        RoleDefinition("finalizer", "Finalizer", "Formatting and final response polish.", "xai:grok-3")
    ]

    @classmethod
    def get_all_toggles(cls) -> List[Dict[str, Any]]:
        """Return raw list of toggles for API/Tool consumption."""
        return [
            {
                "key": t.key,
                "name": t.name,
                "description": t.description,
                "options": t.options,
                "default": t.default,
                "requires_admin": t.requires_admin
            }
            for t in cls._toggles
        ]

    @classmethod
    def get_toggle(cls, key: str) -> Optional[ToggleDefinition]:
        """Find a specific toggle definition."""
        for t in cls._toggles:
            if t.key == key:
                return t
        return None

    @classmethod
    def validate_toggle_value(cls, key: str, value: str) -> bool:
        """Check if a value is valid for a given toggle key."""
        toggle = cls.get_toggle(key)
        if not toggle:
            return False # Unknown key
        
        # If options are strict
        if toggle.options and value not in toggle.options:
            return False
            
        return True

    @classmethod
    def get_all_roles(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": r.role_id,
                "name": r.name,
                "description": r.description,
                "default_model": r.default_model
            }
            for r in cls._roles
        ]

# --- SERVICE REGISTRY SHIM (Restored) ---
class ServiceRegistry:
    """
    Legacy singleton registry for holding shared state/engine instances.
    Kept for compatibility with agent_runner.py.
    """
    _state = None
    _engine = None

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

    # --- SERVICE REGISTRY SHIM (Restored) ---
    _memory_server = None
    _task_manager = None

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

