"""
Security and Cryptography Tools

Provides utilities for password generation, hashing, and basic cryptographic operations.
"""

import hashlib
import hmac
import secrets
import string
import logging
from typing import Dict, Any, Optional
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.security")

async def tool_generate_password(state: AgentState, length: int = 16, complexity: str = "high", include_special: bool = True) -> Dict[str, Any]:
    """Generate a secure random password.

    Args:
        length: Password length (default: 16)
        complexity: Complexity level ("low", "medium", "high")
        include_special: Whether to include special characters

    Returns:
        Dict containing the generated password and metadata
    """
    try:
        # Define character sets based on complexity
        chars = string.ascii_letters + string.digits

        if complexity == "low":
            # Only letters and numbers
            pass
        elif complexity == "medium":
            # Add some special characters
            chars += "!@#$%^&*"
        elif complexity == "high":
            # Add all special characters
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if include_special and complexity != "low":
            # Ensure at least one special character
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            chars += special_chars

        # Generate password
        password = ''.join(secrets.choice(chars) for _ in range(length))

        # Validate complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        complexity_score = sum([has_upper, has_lower, has_digit, has_special])

        return {
            "ok": True,
            "password": password,
            "length": length,
            "complexity": complexity,
            "complexity_score": complexity_score,
            "has_upper": has_upper,
            "has_lower": has_lower,
            "has_digit": has_digit,
            "has_special": has_special
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Password generation failed: {str(e)}",
            "error_type": "generation_error"
        }

async def tool_hash_string(state: AgentState, text: str, algorithm: str = "sha256", salt: Optional[str] = None) -> Dict[str, Any]:
    """Hash a string using various algorithms.

    Args:
        text: The text to hash
        algorithm: Hash algorithm ("md5", "sha1", "sha256", "sha512")
        salt: Optional salt to add to the text before hashing

    Returns:
        Dict containing the hash and metadata
    """
    try:
        # Prepare text with salt
        if salt:
            text_to_hash = salt + text
        else:
            text_to_hash = text

        # Convert to bytes
        text_bytes = text_to_hash.encode('utf-8')

        # Hash based on algorithm
        if algorithm == "md5":
            hash_obj = hashlib.md5(text_bytes)
        elif algorithm == "sha1":
            hash_obj = hashlib.sha1(text_bytes)
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256(text_bytes)
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512(text_bytes)
        else:
            return {
                "ok": False,
                "error": f"Unsupported algorithm: {algorithm}",
                "supported_algorithms": ["md5", "sha1", "sha256", "sha512"],
                "error_type": "unsupported_algorithm"
            }

        hash_value = hash_obj.hexdigest()

        return {
            "ok": True,
            "hash": hash_value,
            "algorithm": algorithm,
            "salt_used": salt is not None,
            "input_length": len(text),
            "hash_length": len(hash_value)
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Hashing failed: {str(e)}",
            "error_type": "hashing_error"
        }

async def tool_generate_token(state: AgentState, length: int = 32, format: str = "hex") -> Dict[str, Any]:
    """Generate a cryptographically secure random token.

    Args:
        length: Token length in bytes (for hex/binary) or characters (for url-safe)
        format: Output format ("hex", "binary", "url-safe")

    Returns:
        Dict containing the generated token
    """
    try:
        if format == "hex":
            token = secrets.token_hex(length)
        elif format == "binary":
            token_bytes = secrets.token_bytes(length)
            token = token_bytes.hex()
        elif format == "url-safe":
            token = secrets.token_urlsafe(length)
        else:
            return {
                "ok": False,
                "error": f"Unsupported format: {format}",
                "supported_formats": ["hex", "binary", "url-safe"],
                "error_type": "unsupported_format"
            }

        return {
            "ok": True,
            "token": token,
            "format": format,
            "length_bytes": length,
            "actual_length": len(token)
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Token generation failed: {str(e)}",
            "error_type": "generation_error"
        }

async def tool_validate_password_strength(state: AgentState, password: str) -> Dict[str, Any]:
    """Analyze password strength and provide recommendations.

    Args:
        password: The password to analyze

    Returns:
        Dict containing strength analysis and recommendations
    """
    try:
        length = len(password)

        # Check character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        # Calculate strength score (0-10)
        score = 0

        # Length scoring
        if length >= 8:
            score += 2
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1

        # Character variety scoring
        if has_upper:
            score += 1
        if has_lower:
            score += 1
        if has_digit:
            score += 1
        if has_special:
            score += 1

        # Complexity bonus
        unique_chars = len(set(password))
        if unique_chars > length * 0.8:  # High character diversity
            score += 1

        # Determine strength level
        if score >= 8:
            strength = "very_strong"
            recommendations = []
        elif score >= 6:
            strength = "strong"
            recommendations = []
        elif score >= 4:
            strength = "medium"
            recommendations = ["Consider adding more character variety"]
        elif score >= 2:
            strength = "weak"
            recommendations = ["Add uppercase letters", "Add numbers", "Add special characters", "Make it longer"]
        else:
            strength = "very_weak"
            recommendations = ["Use at least 8 characters", "Add uppercase letters", "Add numbers", "Add special characters"]

        return {
            "ok": True,
            "password_length": length,
            "strength_score": score,
            "strength_level": strength,
            "has_upper": has_upper,
            "has_lower": has_lower,
            "has_digit": has_digit,
            "has_special": has_special,
            "unique_characters": unique_chars,
            "recommendations": recommendations
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Password analysis failed: {str(e)}",
            "error_type": "analysis_error"
        }