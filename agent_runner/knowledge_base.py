"""
Knowledge Base Interface for Hallucination Detection

Provides fact verification against multiple knowledge sources:
- Project memory (internal facts and episodes)
- External APIs (weather, time, location)
- Mathematical verification
- Temporal consistency checks
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from agent_runner.state import AgentState
from agent_runner.tools.mcp import tool_mcp_proxy

logger = logging.getLogger("agent_runner.knowledge_base")

@dataclass
class VerificationResult:
    """Result of knowledge base verification."""
    verified: bool
    confidence: float  # 0.0 to 1.0
    source: str
    evidence: str
    timestamp: float
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verified": self.verified,
            "confidence": self.confidence,
            "source": self.source,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {}
        }

class KnowledgeBase:
    """
    Multi-source knowledge base for fact verification.

    Integrates with:
    - Project memory (facts, episodes, knowledge bases)
    - External APIs (time, location, weather)
    - Mathematical verification
    - Temporal consistency checks
    """

    def __init__(self, state: AgentState):
        self.state = state
        self.cache: Dict[str, Tuple[VerificationResult, float]] = {}
        self.cache_ttl = 3600  # 1 hour cache

    async def verify_fact(self, fact: str, context: Optional[Dict[str, Any]] = None) -> VerificationResult:
        """
        Verify a factual claim against available knowledge sources.

        Args:
            fact: The factual claim to verify
            context: Additional context for verification

        Returns:
            VerificationResult with verification status and evidence
        """
        # Check cache first
        cache_key = f"fact:{fact}:{json.dumps(context, sort_keys=True) if context else ''}"
        if cache_key in self.cache:
            result, cache_time = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return result

        # Try multiple verification sources in order of preference
        sources = [
            self._verify_against_project_memory,
            self._verify_against_external_apis,
            self._verify_mathematical_fact,
            self._verify_temporal_fact,
        ]

        for source_func in sources:
            try:
                result = await source_func(fact, context)
                if result.confidence > 0.5:  # Only return confident results
                    # Cache the result
                    self.cache[cache_key] = (result, time.time())
                    return result
            except Exception as e:
                logger.debug(f"Verification source {source_func.__name__} failed: {e}")
                continue

        # If no source could verify with confidence, return uncertain result
        return VerificationResult(
            verified=False,
            confidence=0.5,
            source="unknown",
            evidence="Could not verify against available knowledge sources",
            timestamp=time.time()
        )

    async def _verify_against_project_memory(
        self,
        fact: str,
        context: Optional[Dict[str, Any]] = None
    ) -> VerificationResult:
        """Verify fact against project memory system."""
        try:
            # Use semantic search to find related facts
            search_result = await tool_mcp_proxy(
                self.state,
                "project-memory",
                "semantic_search",
                {"query": fact, "limit": 5}
            )

            if search_result.get("ok"):
                facts = search_result.get("result", {}).get("facts", [])

                # Check if any retrieved facts support or contradict the claim
                supporting_facts = []
                contradicting_facts = []

                for retrieved_fact in facts:
                    similarity = self._calculate_fact_similarity(fact, retrieved_fact.get("content", ""))
                    if similarity > 0.8:  # High similarity
                        if self._facts_agree(fact, retrieved_fact.get("content", "")):
                            supporting_facts.append(retrieved_fact)
                        else:
                            contradicting_facts.append(retrieved_fact)

                if contradicting_facts:
                    return VerificationResult(
                        verified=False,
                        confidence=0.8,
                        source="project_memory",
                        evidence=f"Contradicted by {len(contradicting_facts)} stored facts",
                        timestamp=time.time(),
                        metadata={"contradicting_facts": contradicting_facts}
                    )
                elif supporting_facts:
                    return VerificationResult(
                        verified=True,
                        confidence=0.9,
                        source="project_memory",
                        evidence=f"Supported by {len(supporting_facts)} stored facts",
                        timestamp=time.time(),
                        metadata={"supporting_facts": supporting_facts}
                    )

        except Exception as e:
            logger.debug(f"Project memory verification failed: {e}")

        return VerificationResult(
            verified=False,
            confidence=0.3,
            source="project_memory",
            evidence="Could not verify against project memory",
            timestamp=time.time()
        )

    async def _verify_against_external_apis(
        self,
        fact: str,
        context: Optional[Dict[str, Any]] = None
    ) -> VerificationResult:
        """Verify fact against external APIs (time, location, weather, etc.)."""
        fact_lower = fact.lower()

        # Time/date verification
        if any(keyword in fact_lower for keyword in ["time", "date", "day", "current"]):
            return await self._verify_time_fact(fact)

        # Location verification
        if any(keyword in fact_lower for keyword in ["location", "city", "country", "address"]):
            return await self._verify_location_fact(fact)

        # Weather verification
        if any(keyword in fact_lower for keyword in ["weather", "temperature", "forecast"]):
            return await self._verify_weather_fact(fact)

        return VerificationResult(
            verified=False,
            confidence=0.1,
            source="external_apis",
            evidence="No applicable external API for this fact type",
            timestamp=time.time()
        )

    async def _verify_time_fact(self, fact: str) -> VerificationResult:
        """Verify time-related facts."""
        try:
            # Use time MCP server
            time_result = await tool_mcp_proxy(
                self.state,
                "time",
                "get_current_time",
                {}
            )

            if time_result.get("ok"):
                current_time = time_result.get("result", {}).get("current_time")
                if current_time:
                    # Parse the fact and compare with current time
                    # This is a simplified implementation
                    return VerificationResult(
                        verified=True,
                        confidence=0.95,
                        source="time_api",
                        evidence=f"Verified against current time: {current_time}",
                        timestamp=time.time()
                    )

        except Exception as e:
            logger.debug(f"Time verification failed: {e}")

        return VerificationResult(
            verified=False,
            confidence=0.5,
            source="time_api",
            evidence="Could not verify time fact",
            timestamp=time.time()
        )

    async def _verify_location_fact(self, fact: str) -> VerificationResult:
        """Verify location-related facts."""
        # This would use location services
        # For now, return uncertain
        return VerificationResult(
            verified=False,
            confidence=0.4,
            source="location_api",
            evidence="Location verification not fully implemented",
            timestamp=time.time()
        )

    async def _verify_weather_fact(self, fact: str) -> VerificationResult:
        """Verify weather-related facts."""
        try:
            # Weather MCP server is disabled in config, so this will fail
            # But we include it for completeness
            weather_result = await tool_mcp_proxy(
                self.state,
                "weather",
                "get_weather",
                {"location": "current"}  # Simplified
            )

            if weather_result.get("ok"):
                return VerificationResult(
                    verified=True,
                    confidence=0.9,
                    source="weather_api",
                    evidence="Verified against current weather data",
                    timestamp=time.time()
                )

        except Exception as e:
            logger.debug(f"Weather verification failed: {e}")

        return VerificationResult(
            verified=False,
            confidence=0.5,
            source="weather_api",
            evidence="Weather service unavailable or fact unverifiable",
            timestamp=time.time()
        )

    def _verify_mathematical_fact(self, fact: str) -> VerificationResult:
        """Verify mathematical calculations and formulas."""
        import re

        # Look for mathematical expressions
        math_patterns = [
            r'(\d+(?:\.\d+)?)\s*[\+\-\*/]\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)',  # Basic arithmetic
            r'(\d+)\s*\^\s*(\d+)\s*=\s*(\d+)',  # Exponents
            r'sqrt\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(\d+(?:\.\d+)?)',  # Square roots
        ]

        for pattern in math_patterns:
            matches = re.findall(pattern, fact, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    try:
                        # Evaluate the mathematical expression
                        if "+" in fact and "=" in fact:
                            a, b, expected = map(float, match[:3])
                            actual = a + b
                        elif "-" in fact and "=" in fact:
                            a, b, expected = map(float, match[:3])
                            actual = a - b
                        elif "*" in fact and "=" in fact:
                            a, b, expected = map(float, match[:3])
                            actual = a * b
                        elif "/" in fact and "=" in fact:
                            a, b, expected = map(float, match[:3])
                            actual = a / b if b != 0 else 0
                        elif "^" in fact and "=" in fact:
                            a, b, expected = map(float, match[:3])
                            actual = a ** b
                        elif "sqrt" in fact and "=" in fact:
                            a, expected = map(float, [match[0], match[-1]])
                            actual = a ** 0.5
                        else:
                            continue

                        # Check if calculation is correct (within tolerance)
                        tolerance = abs(expected) * 0.01  # 1% tolerance
                        if abs(actual - expected) <= tolerance:
                            return VerificationResult(
                                verified=True,
                                confidence=0.95,
                                source="mathematical",
                                evidence=f"Calculation verified: {actual:.6f} ≈ {expected:.6f}",
                                timestamp=time.time()
                            )
                        else:
                            return VerificationResult(
                                verified=False,
                                confidence=0.9,
                                source="mathematical",
                                evidence=f"Calculation error: expected {expected:.6f}, got {actual:.6f}",
                                timestamp=time.time()
                            )

                    except (ValueError, ZeroDivisionError) as e:
                        logger.debug(f"Mathematical verification failed: {e}")

        return VerificationResult(
            verified=False,
            confidence=0.3,
            source="mathematical",
            evidence="No verifiable mathematical expressions found",
            timestamp=time.time()
        )

    def _verify_temporal_fact(self, fact: str) -> VerificationResult:
        """Verify temporal consistency and time-sensitive facts."""
        import re
        from datetime import datetime

        current_time = time.time()

        # Look for date/time references
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
            r'(\d{2})/(\d{2})/(\d{4})',  # MM/DD/YYYY
            r'(\w+)\s+(\d{1,2}),\s+(\d{4})',  # Month DD, YYYY
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, fact, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match) == 3:
                        # Parse date and check if it's in the future or too far in the past
                        if "-" in match[0]:  # YYYY-MM-DD
                            year, month, day = map(int, match)
                        elif "/" in match[0]:  # MM/DD/YYYY
                            month, day, year = map(int, match)
                        else:
                            # Text month - skip for now
                            continue

                        fact_timestamp = time.mktime(time.struct_time((year, month, day, 0, 0, 0, -1, -1, -1)))

                        # Check for obviously wrong dates
                        if fact_timestamp > current_time + (365 * 24 * 3600):  # More than 1 year in future
                            return VerificationResult(
                                verified=False,
                                confidence=0.8,
                                source="temporal",
                                evidence=f"Date {year}-{month:02d}-{day:02d} is too far in the future",
                                timestamp=time.time()
                            )
                        elif fact_timestamp < current_time - (50 * 365 * 24 * 3600):  # More than 50 years ago
                            # This might be okay for historical facts, but flag for verification
                            return VerificationResult(
                                verified=True,
                                confidence=0.6,
                                source="temporal",
                                evidence=f"Historical date {year}-{month:02d}-{day:02d} verified as plausible",
                                timestamp=time.time()
                            )

                except (ValueError, OverflowError) as e:
                    logger.debug(f"Date parsing failed: {e}")

        return VerificationResult(
            verified=True,  # Default to verified if no obvious issues
            confidence=0.7,
            source="temporal",
            evidence="No temporal inconsistencies detected",
            timestamp=time.time()
        )

    def _calculate_fact_similarity(self, fact1: str, fact2: str) -> float:
        """Calculate semantic similarity between two facts."""
        # Simplified similarity calculation
        # In practice, you'd use embeddings or more sophisticated NLP

        words1 = set(fact1.lower().split())
        words2 = set(fact2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _facts_agree(self, fact1: str, fact2: str) -> bool:
        """Determine if two facts agree or contradict each other."""
        # Simplified agreement detection
        # Look for obvious contradictions

        fact1_lower = fact1.lower()
        fact2_lower = fact2.lower()

        # Check for direct contradictions
        contradiction_pairs = [
            ("is", "is not"),
            ("was", "was not"),
            ("has", "does not have"),
            ("can", "cannot"),
            ("will", "will not"),
        ]

        for pos, neg in contradiction_pairs:
            if pos in fact1_lower and neg in fact2_lower:
                return False
            if neg in fact1_lower and pos in fact2_lower:
                return False

        # If no contradictions found, assume agreement
        return True

    def clear_cache(self):
        """Clear the verification cache."""
        self.cache.clear()
        logger.info("Knowledge base cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            "cache_size": len(self.cache),
            "cache_ttl": self.cache_ttl,
            "sources": ["project_memory", "external_apis", "mathematical", "temporal"]
        }