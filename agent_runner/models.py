"""
Pydantic AI Integration - Phase 2: Structured Outputs
Type-safe models for chat completions, tool calls, and responses.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class MessageRole(str, Enum):
    """Valid message roles in chat completions."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class FinishReason(str, Enum):
    """Valid finish reasons for chat completions."""
    STOP = "stop"
    LENGTH = "length"
    FUNCTION_CALL = "function_call"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"


class ChatMessage(BaseModel):
    """A single chat message."""
    role: MessageRole
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

    @validator('content')
    def validate_content(cls, v):
        """Ensure content is not empty for non-tool messages."""
        if v is not None and v.strip() == "":
            return None
        return v

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)


class Choice(BaseModel):
    """A single choice in a chat completion response."""
    index: int = Field(..., ge=0)
    message: ChatMessage
    finish_reason: Optional[FinishReason] = None

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ChatCompletionRequest(BaseModel):
    """Request structure for chat completions."""
    messages: List[ChatMessage] = Field(..., min_items=1)
    model: str
    max_tokens: Optional[int] = Field(None, gt=0)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, gt=0.0, le=1.0)
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None

    @validator('stop')
    def validate_stop(cls, v):
        """Validate stop parameter."""
        if isinstance(v, str):
            return [v]
        if isinstance(v, list) and len(v) > 4:
            raise ValueError("stop parameter cannot have more than 4 sequences")
        return v


class ChatCompletionResponse(BaseModel):
    """Response structure for chat completions."""
    id: str
    object: str = Field(..., pattern=r"^chat\.completion(\.chunk)?$")
    created: int = Field(..., gt=0)
    model: str
    choices: List[Choice] = Field(..., min_items=1)
    usage: Usage

    @validator('object')
    def validate_object(cls, v):
        """Ensure object type is valid."""
        if not v.startswith("chat.completion"):
            raise ValueError("object must start with 'chat.completion'")
        return v


class ToolCall(BaseModel):
    """A tool call within a message."""
    id: str
    type: str = "function"
    function: Dict[str, Any]  # Function call details

    @validator('type')
    def validate_type(cls, v):
        """Ensure tool type is valid."""
        if v != "function":
            raise ValueError("tool type must be 'function'")
        return v


class ToolMessage(ChatMessage):
    """A tool result message."""
    role: MessageRole = Field(..., literal=MessageRole.TOOL)
    tool_call_id: str = Field(..., min_length=1)


class ErrorResponse(BaseModel):
    """Error response structure."""
    error: Dict[str, Any]
    choices: Optional[List[Choice]] = None


class StreamChunk(BaseModel):
    """A chunk in a streaming response."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]  # Stream chunks have different structure

    class Config:
        """Allow extra fields in stream chunks."""
        extra = "allow"


# Type-safe result types for validation
ChatCompletionResult = Union[ChatCompletionResponse, ErrorResponse]
ToolValidationResult = Dict[str, Any]
ContentSafetyResult = Dict[str, Any]