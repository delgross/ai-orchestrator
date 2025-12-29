"""
Dashboard error tracking and learning system.

Tracks dashboard errors, user interactions, and patterns to learn from failures
and improve the dashboard over time.
"""

from __future__ import annotations

import json
import time
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("agent_runner.dashboard_tracker")


class DashboardErrorType(Enum):
    """Types of dashboard errors."""
    JAVASCRIPT_ERROR = "javascript_error"
    API_ERROR = "api_error"
    RENDERING_ERROR = "rendering_error"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    AUTH_ERROR = "auth_error"
    UNKNOWN = "unknown"


@dataclass
class DashboardError:
    """Recorded dashboard error."""
    timestamp: float
    error_type: str
    error_message: str
    error_stack: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    component: Optional[str] = None  # Which part of dashboard (e.g., "refresh", "models", "scheduler")
    context: Optional[Dict[str, Any]] = None
    frequency: int = 1  # How many times this error occurred
    request_id: Optional[str] = None  # Request ID for correlating with backend logs


@dataclass
class UserInteraction:
    """User interaction pattern."""
    timestamp: float
    action: str  # e.g., "click", "refresh", "tab_switch"
    target: Optional[str] = None  # What was clicked/interacted with
    success: bool = True
    duration_ms: Optional[float] = None
    context: Optional[Dict[str, Any]] = None


class DashboardTracker:
    """Tracks dashboard errors and user patterns for learning."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize dashboard tracker."""
        if storage_path is None:
            storage_path = Path(__file__).parent.parent / "logs" / "dashboard_tracking"
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.errors: List[DashboardError] = []
        self.interactions: List[UserInteraction] = []
        self._error_patterns: Dict[str, DashboardError] = {}  # Deduplicate by pattern
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load existing tracking data from disk."""
        errors_file = self.storage_path / "errors.jsonl"
        if errors_file.exists():
            try:
                with open(errors_file, "r") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            error = DashboardError(**data)
                            self.errors.append(error)
                            # Track patterns
                            pattern_key = self._get_error_pattern_key(error)
                            if pattern_key in self._error_patterns:
                                self._error_patterns[pattern_key].frequency += 1
                            else:
                                self._error_patterns[pattern_key] = error
            except Exception as e:
                logger.warning(f"Failed to load dashboard error data: {e}")
        
        interactions_file = self.storage_path / "interactions.jsonl"
        if interactions_file.exists():
            try:
                with open(interactions_file, "r") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self.interactions.append(UserInteraction(**data))
            except Exception as e:
                logger.warning(f"Failed to load dashboard interaction data: {e}")
    
    def _get_error_pattern_key(self, error: DashboardError) -> str:
        """Generate a pattern key for error deduplication."""
        # Use error type, message, and component to identify patterns
        parts = [error.error_type, error.component or "unknown"]
        if error.error_message:
            # Use first 100 chars of message for pattern matching
            msg_part = error.error_message[:100].replace("\n", " ").strip()
            parts.append(msg_part)
        return "|".join(parts)
    
    def record_error(
        self,
        error_type: DashboardErrorType,
        error_message: str,
        error_stack: Optional[str] = None,
        url: Optional[str] = None,
        user_agent: Optional[str] = None,
        component: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """Record a dashboard error."""
        error = DashboardError(
            timestamp=time.time(),
            error_type=error_type.value,
            error_message=error_message,
            error_stack=error_stack,
            url=url,
            user_agent=user_agent,
            component=component,
            context=context or {},
            request_id=request_id,
        )
        
        self.errors.append(error)
        
        # Check if this is a known pattern
        pattern_key = self._get_error_pattern_key(error)
        if pattern_key in self._error_patterns:
            self._error_patterns[pattern_key].frequency += 1
        else:
            self._error_patterns[pattern_key] = error
        
        # Persist to disk
        self._save_error(error)
        
        logger.warning(
            f"Dashboard error recorded: {error_type.value} in {component or 'unknown'}: {error_message[:100]}"
        )
    
    def record_interaction(
        self,
        action: str,
        target: Optional[str] = None,
        success: bool = True,
        duration_ms: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a user interaction."""
        interaction = UserInteraction(
            timestamp=time.time(),
            action=action,
            target=target,
            success=success,
            duration_ms=duration_ms,
            context=context or {},
        )
        
        self.interactions.append(interaction)
        
        # Keep only last 1000 interactions in memory
        if len(self.interactions) > 1000:
            self.interactions = self.interactions[-1000:]
        
        # Persist to disk
        self._save_interaction(interaction)
    
    def _save_error(self, error: DashboardError) -> None:
        """Save error to disk."""
        errors_file = self.storage_path / "errors.jsonl"
        try:
            # Use 'with' statement for guaranteed file closure
            with open(errors_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(error)) + "\n")
                f.flush()  # Ensure data is written
        except Exception as e:
            logger.error(f"Failed to save dashboard error: {e}")
    
    def _save_interaction(self, interaction: UserInteraction) -> None:
        """Save interaction to disk."""
        interactions_file = self.storage_path / "interactions.jsonl"
        try:
            # Use 'with' statement for guaranteed file closure
            with open(interactions_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(interaction)) + "\n")
                f.flush()  # Ensure data is written
        except Exception as e:
            logger.error(f"Failed to save dashboard interaction: {e}")
    
    def get_error_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequent error patterns."""
        patterns = sorted(
            self._error_patterns.values(),
            key=lambda e: e.frequency,
            reverse=True
        )[:limit]
        return [asdict(p) for p in patterns]
    
    def get_recent_errors(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors within the specified time window."""
        cutoff = time.time() - (hours * 3600)
        recent = [e for e in self.errors if e.timestamp >= cutoff]
        recent.sort(key=lambda e: e.timestamp, reverse=True)
        return [asdict(e) for e in recent[:limit]]
    
    def get_component_error_rate(self, component: str, hours: int = 24) -> Dict[str, Any]:
        """Get error rate for a specific component."""
        cutoff = time.time() - (hours * 3600)
        component_errors = [e for e in self.errors if e.component == component and e.timestamp >= cutoff]
        total_interactions = len([i for i in self.interactions if i.target == component and i.timestamp >= cutoff])
        
        error_rate = len(component_errors) / max(total_interactions, 1) if total_interactions > 0 else 0
        
        return {
            "component": component,
            "error_count": len(component_errors),
            "interaction_count": total_interactions,
            "error_rate": error_rate,
            "hours": hours,
        }
    
    def clear_errors(self) -> Dict[str, Any]:
        """Clear all errors from memory and disk."""
        error_count = len(self.errors)
        self.errors.clear()
        self._error_patterns.clear()
        
        # Clear disk file
        errors_file = self.storage_path / "errors.jsonl"
        if errors_file.exists():
            try:
                errors_file.unlink()
                logger.info(f"Cleared {error_count} errors from disk")
            except Exception as e:
                logger.error(f"Failed to delete errors file: {e}")
        
        return {
            "cleared_count": error_count,
            "message": f"Cleared {error_count} errors"
        }
    
    def clear_interactions(self) -> Dict[str, Any]:
        """Clear all interactions from memory and disk."""
        interaction_count = len(self.interactions)
        self.interactions.clear()
        
        # Clear disk file
        interactions_file = self.storage_path / "interactions.jsonl"
        if interactions_file.exists():
            try:
                interactions_file.unlink()
                logger.info(f"Cleared {interaction_count} interactions from disk")
            except Exception as e:
                logger.error(f"Failed to delete interactions file: {e}")
        
        return {
            "cleared_count": interaction_count,
            "message": f"Cleared {interaction_count} interactions"
        }
    
    def clear_all(self) -> Dict[str, Any]:
        """Clear all errors and interactions."""
        error_result = self.clear_errors()
        interaction_result = self.clear_interactions()
        
        return {
            "errors_cleared": error_result["cleared_count"],
            "interactions_cleared": interaction_result["cleared_count"],
            "message": f"Cleared {error_result['cleared_count']} errors and {interaction_result['cleared_count']} interactions"
        }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Generate insights from tracked data for learning."""
        # Most problematic components
        component_errors: Dict[str, int] = {}
        for error in self.errors:
            if error.component:
                component_errors[error.component] = component_errors.get(error.component, 0) + 1
        
        # Most common error types
        error_type_counts: Dict[str, int] = {}
        for error in self.errors:
            error_type_counts[error.error_type] = error_type_counts.get(error.error_type, 0) + 1
        
        # User interaction patterns
        action_counts: Dict[str, int] = {}
        for interaction in self.interactions:
            action_counts[interaction.action] = action_counts.get(interaction.action, 0) + 1
        
        return {
            "most_problematic_components": sorted(
                component_errors.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "most_common_errors": sorted(
                error_type_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "most_common_actions": sorted(
                action_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "total_errors": len(self.errors),
            "total_interactions": len(self.interactions),
            "top_error_patterns": self.get_error_patterns(5),
        }


# Global tracker instance
_tracker: Optional[DashboardTracker] = None


def get_dashboard_tracker() -> DashboardTracker:
    """Get or create the global dashboard tracker."""
    global _tracker
    if _tracker is None:
        _tracker = DashboardTracker()
    return _tracker


