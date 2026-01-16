"""
Tests for message_utils.py - multimodal content handling
"""

import pytest
from common.message_utils import (
    extract_text_content,
    normalize_message_content,
    has_multimodal_content,
    get_message_text,
    filter_text_only_messages
)


class TestExtractTextContent:
    """Test extract_text_content function"""

    def test_string_content(self):
        """Test extraction from string content"""
        content = "Hello world"
        result = extract_text_content(content)
        assert result == "Hello world"

    def test_multimodal_content_text_only(self):
        """Test extraction from multimodal content with only text"""
        content = [
            {"type": "text", "text": "Hello"},
            {"type": "text", "text": "world"}
        ]
        result = extract_text_content(content)
        assert result == "Hello world"

    def test_multimodal_content_mixed(self):
        """Test extraction from multimodal content with text and images"""
        content = [
            {"type": "text", "text": "Describe this"},
            {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}}
        ]
        result = extract_text_content(content)
        assert result == "Describe this"

    def test_multimodal_content_empty(self):
        """Test extraction from multimodal content with no text"""
        content = [
            {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}}
        ]
        result = extract_text_content(content)
        assert result == ""

    def test_none_content(self):
        """Test extraction from None content"""
        result = extract_text_content(None)
        assert result == ""

    def test_empty_list(self):
        """Test extraction from empty list"""
        result = extract_text_content([])
        assert result == ""

    def test_invalid_type(self):
        """Test extraction from invalid type"""
        result = extract_text_content(123)
        assert result == "123"


class TestNormalizeMessageContent:
    """Test normalize_message_content function"""

    def test_string_message(self):
        """Test normalization of message with string content"""
        message = {"role": "user", "content": "Hello world"}
        result = normalize_message_content(message)
        assert result["content"] == "Hello world"
        assert result["role"] == "user"

    def test_multimodal_message(self):
        """Test normalization of message with multimodal content"""
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}}
            ]
        }
        result = normalize_message_content(message)
        assert result["content"] == "Hello"
        assert result["role"] == "user"


class TestHasMultimodalContent:
    """Test has_multimodal_content function"""

    def test_string_content(self):
        """Test detection of multimodal content in string"""
        message = {"role": "user", "content": "Hello world"}
        result = has_multimodal_content(message)
        assert result is False

    def test_multimodal_content(self):
        """Test detection of multimodal content in list"""
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}}
            ]
        }
        result = has_multimodal_content(message)
        assert result is True

    def test_text_only_multimodal(self):
        """Test detection when multimodal content is text-only"""
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": "world"}
            ]
        }
        result = has_multimodal_content(message)
        assert result is False


class TestGetMessageText:
    """Test get_message_text function"""

    def test_string_content(self):
        """Test getting text from string content"""
        message = {"role": "user", "content": "  Hello world  "}
        result = get_message_text(message)
        assert result == "Hello world"

    def test_multimodal_content(self):
        """Test getting text from multimodal content"""
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "  Hello  "},
                {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}}
            ]
        }
        result = get_message_text(message)
        assert result == "Hello"


class TestFilterTextOnlyMessages:
    """Test filter_text_only_messages function"""

    def test_mixed_messages(self):
        """Test filtering messages with and without text"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "user", "content": ""},  # Empty string
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "..."}}]},  # No text
            {"role": "user", "content": [{"type": "text", "text": "World"}]},  # Has text
            {"role": "assistant", "content": "Response"}
        ]
        result = filter_text_only_messages(messages)
        assert len(result) == 3
        assert result[0]["content"] == "Hello"
        assert result[1]["content"] == "World"
        assert result[2]["content"] == "Response"