"""
Conversation State Compression for Prefix Caching Optimization

This module provides intelligent conversation state management that maintains
AI reasoning capabilities while enabling prefix caching optimizations.

Key Features:
- Tool state tracking (successes/failures)
- Task context awareness
- User clarification preservation
- Selective history retention
- Compressed working memory generation
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("agent_runner.conversation_state")


class TaskStatus(Enum):
    """Current task execution status"""
    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class ToolExecutionRecord:
    """Record of a tool execution attempt"""
    tool_name: str
    success: bool
    timestamp: float
    error_message: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result_summary: Optional[str] = None

    def to_summary(self) -> str:
        """Convert to human-readable summary"""
        if self.success:
            return f"✅ {self.tool_name}: {self.result_summary or 'completed successfully'}"
        else:
            return f"❌ {self.tool_name}: {self.error_message or 'failed'}"


@dataclass
class ConversationState:
    """
    Compressed conversation state that maintains essential reasoning context
    without storing full message history.
    """
    conversation_id: str
    current_task: str = ""
    task_status: TaskStatus = TaskStatus.INITIALIZING
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

    # Tool execution tracking
    tool_history: List[ToolExecutionRecord] = field(default_factory=list)
    successful_tools: Dict[str, List[ToolExecutionRecord]] = field(default_factory=dict)
    failed_tools: Dict[str, List[ToolExecutionRecord]] = field(default_factory=dict)

    # User context preservation
    user_clarifications: List[str] = field(default_factory=list)
    important_context: List[str] = field(default_factory=list)

    # Selective message retention
    essential_messages: List[Dict[str, Any]] = field(default_factory=list)
    max_essential_messages: int = 6  # Keep last 3 exchanges (6 messages)

    def update_task(self, task_description: str, status: TaskStatus = TaskStatus.IN_PROGRESS):
        """Update current task context"""
        self.current_task = task_description
        self.task_status = status
        self.last_updated = time.time()
        logger.debug(f"Task updated: {task_description} ({status.value})")

    def record_tool_execution(self, tool_name: str, success: bool,
                            error_message: Optional[str] = None,
                            parameters: Optional[Dict[str, Any]] = None,
                            result_summary: Optional[str] = None):
        """Record a tool execution attempt"""
        record = ToolExecutionRecord(
            tool_name=tool_name,
            success=success,
            timestamp=time.time(),
            error_message=error_message,
            parameters=parameters,
            result_summary=result_summary
        )

        self.tool_history.append(record)

        # Update categorized tracking
        if success:
            if tool_name not in self.successful_tools:
                self.successful_tools[tool_name] = []
            self.successful_tools[tool_name].append(record)
        else:
            if tool_name not in self.failed_tools:
                self.failed_tools[tool_name] = []
            self.failed_tools[tool_name].append(record)

        self.last_updated = time.time()
        logger.debug(f"Tool execution recorded: {tool_name} ({'success' if success else 'failed'})")

    def add_user_clarification(self, clarification: str):
        """Add important user clarification to preserve context"""
        if clarification not in self.user_clarifications:
            self.user_clarifications.append(clarification)
            self.last_updated = time.time()
            logger.debug(f"User clarification added: {clarification[:50]}...")

    def add_important_context(self, context: str):
        """Add important context that should be preserved"""
        if context not in self.important_context:
            self.important_context.append(context)
            self.last_updated = time.time()
            logger.debug(f"Important context added: {context[:50]}...")

    def add_essential_message(self, message: Dict[str, Any]):
        """Add essential message to selective retention"""
        self.essential_messages.append(message)
        # Maintain max size by removing oldest messages
        if len(self.essential_messages) > self.max_essential_messages:
            removed = self.essential_messages.pop(0)
            logger.debug(f"Removed old essential message: {removed.get('role', 'unknown')}")

        self.last_updated = time.time()

    def should_avoid_tool(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a tool should be avoided based on failure history

        Returns:
            (should_avoid, reason)
        """
        if tool_name in self.failed_tools:
            failures = self.failed_tools[tool_name]
            recent_failures = [f for f in failures if time.time() - f.timestamp < 300]  # Last 5 minutes

            if len(recent_failures) >= 2:
                last_failure = recent_failures[-1]
                reason = f"Recently failed {len(recent_failures)} times"
                if last_failure.error_message:
                    reason += f": {last_failure.error_message}"
                return True, reason

        return False, None

    def get_tool_success_summary(self) -> str:
        """Generate summary of tool execution success/failure"""
        if not self.tool_history:
            return "No tools executed yet"

        total_executions = len(self.tool_history)
        successful_executions = sum(1 for t in self.tool_history if t.success)
        success_rate = successful_executions / total_executions if total_executions > 0 else 0

        summary_parts = [f"Tool execution: {successful_executions}/{total_executions} successful ({success_rate:.1%})"]

        # Add details for recently failed tools
        recent_failures = {}
        for tool_name, failures in self.failed_tools.items():
            recent = [f for f in failures if time.time() - f.timestamp < 300]
            if recent:
                recent_failures[tool_name] = len(recent)

        if recent_failures:
            failure_summary = ", ".join(f"{tool}: {count} recent failures"
                                       for tool, count in recent_failures.items())
            summary_parts.append(f"Recent failures: {failure_summary}")

        return " | ".join(summary_parts)

    def get_task_progress_summary(self) -> str:
        """Generate summary of current task progress"""
        if not self.current_task:
            return "No active task"

        status_emoji = {
            TaskStatus.INITIALIZING: "🔄",
            TaskStatus.IN_PROGRESS: "⚡",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.BLOCKED: "⏸️"
        }

        emoji = status_emoji.get(self.task_status, "❓")
        return f"{emoji} {self.task_status.value.upper()}: {self.current_task}"

    def get_user_context_summary(self) -> str:
        """Generate summary of preserved user context"""
        context_parts = []

        if self.user_clarifications:
            clarifications = self.user_clarifications[-3:]  # Last 3 clarifications
            context_parts.append(f"User clarifications: {'; '.join(clarifications)}")

        if self.important_context:
            important = self.important_context[-2:]  # Last 2 important items
            context_parts.append(f"Key context: {'; '.join(important)}")

        return " | ".join(context_parts) if context_parts else "No special user context"

    def get_compressed_context(self, include_essential_messages: bool = True) -> Dict[str, Any]:
        """
        Generate compressed context for AI reasoning

        Args:
            include_essential_messages: Whether to include selective message history

        Returns:
            Dictionary with compressed reasoning context
        """
        context = {
            "task_status": self.get_task_progress_summary(),
            "tool_history": self.get_tool_success_summary(),
            "user_context": self.get_user_context_summary(),
            "conversation_age": time.time() - self.created_at,
            "last_activity": time.time() - self.last_updated
        }

        if include_essential_messages and self.essential_messages:
            context["recent_messages"] = self.essential_messages[-4:]  # Last 2 exchanges

        return context

    def get_compressed_prompt_addition(self) -> str:
        """
        Generate the compressed context as a prompt addition
        for use with prefix caching.
        """
        context = self.get_compressed_context()

        prompt_parts = [
            "[CONVERSATION STATE]",
            f"Status: {context['task_status']}",
            f"Tools: {context['tool_history']}",
        ]

        if context['user_context'] != "No special user context":
            prompt_parts.append(f"Context: {context['user_context']}")

        # Add recent messages if available
        if 'recent_messages' in context:
            prompt_parts.append("\n[RECENT EXCHANGES]")
            for msg in context['recent_messages']:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]  # Truncate long content
                if len(content) > 97:
                    content = content[:97] + "..."
                prompt_parts.append(f"{role.title()}: {content}")

        return "\n".join(prompt_parts)

    def reset_for_new_conversation(self):
        """Reset state for a new conversation while preserving learning"""
        # Keep tool success/failure patterns but reset conversation-specific state
        self.current_task = ""
        self.task_status = TaskStatus.INITIALIZING
        self.user_clarifications.clear()
        self.important_context.clear()
        self.essential_messages.clear()
        self.created_at = time.time()
        self.last_updated = time.time()

        logger.debug("Conversation state reset for new conversation")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for storage/persistence"""
        return {
            "conversation_id": self.conversation_id,
            "current_task": self.current_task,
            "task_status": self.task_status.value,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "tool_history": [vars(record) for record in self.tool_history],
            "successful_tools": {k: [vars(r) for r in v] for k, v in self.successful_tools.items()},
            "failed_tools": {k: [vars(r) for r in v] for k, v in self.failed_tools.items()},
            "user_clarifications": self.user_clarifications,
            "important_context": self.important_context,
            "essential_messages": self.essential_messages,
            "max_essential_messages": self.max_essential_messages
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationState':
        """Deserialize state from storage"""
        # Reconstruct ToolExecutionRecord objects
        tool_history = []
        for record_data in data.get("tool_history", []):
            record = ToolExecutionRecord(
                tool_name=record_data["tool_name"],
                success=record_data["success"],
                timestamp=record_data.get("timestamp", time.time()),
                error_message=record_data.get("error_message"),
                parameters=record_data.get("parameters"),
                result_summary=record_data.get("result_summary")
            )
            tool_history.append(record)

        # Reconstruct categorized tool records
        successful_tools = {}
        for tool_name, records_data in data.get("successful_tools", {}).items():
            successful_tools[tool_name] = []
            for record_data in records_data:
                record = ToolExecutionRecord(
                    tool_name=record_data["tool_name"],
                    success=record_data["success"],
                    timestamp=record_data.get("timestamp", time.time()),
                    error_message=record_data.get("error_message"),
                    parameters=record_data.get("parameters"),
                    result_summary=record_data.get("result_summary")
                )
                successful_tools[tool_name].append(record)

        failed_tools = {}
        for tool_name, records_data in data.get("failed_tools", {}).items():
            failed_tools[tool_name] = []
            for record_data in records_data:
                record = ToolExecutionRecord(
                    tool_name=record_data["tool_name"],
                    success=record_data["success"],
                    timestamp=record_data.get("timestamp", time.time()),
                    error_message=record_data.get("error_message"),
                    parameters=record_data.get("parameters"),
                    result_summary=record_data.get("result_summary")
                )
                failed_tools[tool_name].append(record)

        # Create instance
        instance = cls(
            conversation_id=data["conversation_id"],
            current_task=data.get("current_task", ""),
            created_at=data.get("created_at", time.time()),
            last_updated=data.get("last_updated", time.time()),
            tool_history=tool_history,
            successful_tools=successful_tools,
            failed_tools=failed_tools,
            user_clarifications=data.get("user_clarifications", []),
            important_context=data.get("important_context", []),
            essential_messages=data.get("essential_messages", []),
            max_essential_messages=data.get("max_essential_messages", 6)
        )

        # Set task status
        try:
            instance.task_status = TaskStatus(data.get("task_status", "initializing"))
        except ValueError:
            instance.task_status = TaskStatus.INITIALIZING

        return instance