"""
Message Content Utilities
Handles multimodal message content extraction and processing.
"""

from typing import Dict, Any, List, Union, Optional


def extract_text_content(content: Any) -> str:
    """
    Extract text content from message content field.

    Handles both OpenAI formats:
    - Text-only: "content": "Hello world"
    - Multimodal: "content": [{"type": "text", "text": "Hello"}, {"type": "image_url", ...}]

    Args:
        content: The message content field (string or list)

    Returns:
        str: Extracted text content, empty string if no text found
    """
    if content is None:
        return ""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        # Multimodal content - extract all text blocks
        text_parts = []
        for block in content:
            if isinstance(block, dict):
                block_type = block.get("type")
                if block_type == "text":
                    text = block.get("text", "")
                    if text:
                        text_parts.append(text)
                # Could extend for other content types in the future
                # elif block_type == "image_url":
                #     # Handle image descriptions if needed
                #     pass
        return " ".join(text_parts)

    # Fallback for unexpected types
    return str(content)


def normalize_message_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a message to ensure content is always a string.

    Args:
        message: Message dict with potential multimodal content

    Returns:
        Dict with normalized content field
    """
    normalized = dict(message)
    if "content" in normalized:
        normalized["content"] = extract_text_content(normalized["content"])
    return normalized


def has_multimodal_content(message: Dict[str, Any]) -> bool:
    """
    Check if a message contains multimodal content (images, etc.).

    Args:
        message: Message dict to check

    Returns:
        bool: True if message contains non-text content
    """
    content = message.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") != "text":
                return True
    return False


def get_message_text(message: Dict[str, Any]) -> str:
    """
    Get the text content of a message, normalized and stripped.

    Args:
        message: Message dict

    Returns:
        str: Normalized, stripped text content
    """
    content = extract_text_content(message.get("content", ""))
    return content.strip()


def filter_text_only_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter messages to only include those with text content.

    Args:
        messages: List of message dicts

    Returns:
        List of messages with text content only (normalized)
    """
    return [normalize_message_content(msg) for msg in messages if get_message_text(msg)]