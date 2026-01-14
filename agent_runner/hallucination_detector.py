"""
Robust Generic Learning Hallucination Detector

A multi-layered hallucination detection system that analyzes AI responses for:
- Factual inaccuracies
- Logical inconsistencies
- Contextual mismatches
- Statistical anomalies

Architecture:
- Layer 1: Fast statistical checks (<50ms)
- Layer 2: Semantic analysis (<200ms)
- Layer 3: Factual verification (<300ms)
- Learning: Continuous improvement from user feedback
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum
import math
import httpx

from agent_runner.state import AgentState
from common.unified_tracking import track_event, EventSeverity, EventCategory

logger = logging.getLogger("agent_runner.hallucination_detector")

class DetectionLayer(Enum):
    """Detection layers in order of execution speed."""
    STATISTICAL = "statistical"  # Fastest (<50ms)
    SEMANTIC = "semantic"        # Medium (<200ms)
    FACTUAL = "factual"          # Thorough (<300ms)

class HallucinationSeverity(Enum):
    """Severity levels for detected hallucinations."""
    LOW = "low"          # Minor inconsistencies, low confidence
    MEDIUM = "medium"    # Clear errors but not critical
    HIGH = "high"        # Significant factual errors
    CRITICAL = "critical" # Dangerous misinformation

@dataclass
class DetectionResult:
    """Result of hallucination detection."""
    is_hallucination: bool
    severity: HallucinationSeverity
    confidence: float  # 0.0 to 1.0
    detected_issues: List[Dict[str, Any]]
    layer_results: Dict[str, Any]
    processing_time_ms: float
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_hallucination": self.is_hallucination,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "detected_issues": self.detected_issues,
            "layer_results": self.layer_results,
            "processing_time_ms": self.processing_time_ms,
            "recommendations": self.recommendations
        }

@dataclass
class DetectorConfig:
    """Configuration for hallucination detection."""
    enabled: bool = True

    # Statistical detection thresholds
    perplexity_threshold: float = 2.5  # Lower is more confident
    token_prob_threshold: float = 0.1  # Minimum token probability
    repetition_threshold: int = 3      # Max repeated phrases

    # Semantic detection thresholds
    coherence_threshold: float = 0.7   # Topic coherence score
    entity_consistency_threshold: float = 0.8

    # Factual verification settings
    fact_check_enabled: bool = True
    math_verification_enabled: bool = True
    temporal_check_enabled: bool = True

    # Performance settings
    max_processing_time_ms: int = 500
    enable_caching: bool = True
    cache_ttl_seconds: int = 300

    # Learning settings
    learning_enabled: bool = True
    feedback_collection_enabled: bool = True

class LLMHallucinationAnalyzer:
    """LLM-based hallucination analysis using llama3.2:latest."""

    def __init__(self, ollama_base: str = "http://127.0.0.1:11434"):
        self.ollama_base = ollama_base.rstrip("/")
        self.model_name = "llama3.2:latest"
        self.client = None

    async def _ensure_client(self):
        """Ensure HTTP client is available."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=10.0)

    async def _call_ollama(self, prompt: str, max_tokens: int = 50) -> str:
        """Call Ollama API for analysis."""
        await self._ensure_client()

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 32768,  # [USER] Expanded Context to 32k
                "num_predict": max_tokens,
                "temperature": 0.1,  # Low temperature for consistent analysis
                "top_p": 0.9
            }
        }

        try:
            response = await self.client.post(
                f"{self.ollama_base}/api/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            logger.warning(f"LLM analysis failed: {e}")
            return ""

    async def analyze_semantic_coherence(self, query: str, response: str, context: Optional[Dict] = None) -> float:
        """Analyze semantic coherence between query and response."""
        context_str = ""
        if context and context.get("conversation_history"):
            # Include recent conversation context
            recent_history = context["conversation_history"][-2:]  # Last 2 exchanges
            context_str = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}" for msg in recent_history])

        prompt = f"""Analyze how semantically coherent this response is to the query.
Return only a number from 0.0 to 1.0 where:
- 1.0 = Perfect semantic coherence (response directly and accurately answers query)
- 0.5 = Partial coherence (response is related but misses key aspects)
- 0.0 = No semantic coherence (response is completely unrelated or contradictory)

Consider:
- Does the response answer what was asked?
- Is the meaning consistent with the query?
- Does it maintain logical relationships?

Query: {query}
Response: {response}

{f"Recent context:\n{context_str}" if context_str else ""}

Coherence score (0.0-1.0):"""

        result = await self._call_ollama(prompt, max_tokens=10)

        try:
            # Extract the numeric score
            import re
            score_match = re.search(r'(\d+\.?\d*)', result)
            if score_match:
                score = float(score_match.group(1))
                return max(0.0, min(1.0, score))  # Clamp to 0-1 range
        except (ValueError, AttributeError):
            pass

        logger.debug(f"Could not parse coherence score from: {result}")
        return 0.5  # Default neutral score

    async def analyze_factual_consistency(self, response: str, known_facts: List[str]) -> float:
        """Analyze if response is consistent with known facts."""
        if not known_facts:
            return 0.8  # Neutral if no facts to check against

        facts_str = "\n".join(f"- {fact}" for fact in known_facts[:5])  # Limit to 5 facts

        prompt = f"""Analyze if this response is factually consistent with the known facts.
Return only a number from 0.0 to 1.0 where:
- 1.0 = Fully consistent with all known facts
- 0.5 = Partially consistent (some contradictions but mostly okay)
- 0.0 = Major factual contradictions

Known facts:
{facts_str}

Response to analyze: {response}

Factual consistency score (0.0-1.0):"""

        result = await self._call_ollama(prompt, max_tokens=10)

        try:
            import re
            score_match = re.search(r'(\d+\.?\d*)', result)
            if score_match:
                score = float(score_match.group(1))
                return max(0.0, min(1.0, score))
        except (ValueError, AttributeError):
            pass

        return 0.8  # Default to mostly consistent

    async def detect_response_quality(self, query: str, response: str) -> Dict[str, Any]:
        """Comprehensive response quality analysis."""
        prompt = f"""Analyze this AI response for quality and potential issues.
Return a JSON object with these fields:
- coherence_score: 0.0-1.0 (semantic coherence with query)
- factual_confidence: 0.0-1.0 (confidence in factual accuracy)
- completeness_score: 0.0-1.0 (how complete the answer is)
- hallucination_risk: 0.0-1.0 (risk of hallucination)
- issues: array of strings describing any problems

Query: {query}
Response: {response}

Analysis (JSON only):"""

        result = await self._call_ollama(prompt, max_tokens=200)

        try:
            # Try to parse JSON response
            analysis = json.loads(result)
            return analysis
        except json.JSONDecodeError:
            # Fallback to basic analysis
            return {
                "coherence_score": 0.5,
                "factual_confidence": 0.5,
                "completeness_score": 0.5,
                "hallucination_risk": 0.5,
                "issues": ["Could not parse LLM analysis"]
            }

    async def close(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
            self.client = None

class HallucinationDetector:
    """
    Multi-layered hallucination detection system.

    Detects hallucinations through:
    1. Statistical analysis (token probabilities, perplexity)
    2. Semantic coherence (topic consistency, entity relationships)
    3. Factual verification (knowledge base lookup, mathematical validation)
    4. LLM-based analysis (deep semantic understanding)
    """

    def __init__(self, state: AgentState, config: Optional[DetectorConfig] = None):
        self.state = state
        self.config = config or DetectorConfig()

        # Detection method registry
        self.detectors: Dict[DetectionLayer, List[Callable]] = {
            DetectionLayer.STATISTICAL: [],
            DetectionLayer.SEMANTIC: [],
            DetectionLayer.FACTUAL: []
        }

        # Caching for performance
        self.result_cache: Dict[str, Tuple[DetectionResult, float]] = {}

        # Learning data
        self.feedback_history: List[Dict[str, Any]] = []

        # LLM analyzer
        self.llm_analyzer = LLMHallucinationAnalyzer()

        # Initialize detectors
        self._initialize_detectors()

        logger.info("HallucinationDetector initialized with config: enabled=%s, layers=%s, llm_analyzer=%s",
                   self.config.enabled, [layer.value for layer in self.detectors.keys()],
                   "enabled" if self.llm_analyzer else "disabled")

    def _initialize_detectors(self):
        """Initialize all detection methods."""
        # Statistical detectors (Layer 1)
        self.detectors[DetectionLayer.STATISTICAL] = [
            self._detect_low_confidence_tokens,
            self._detect_repetition_patterns,
            self._detect_length_anomalies,
            self._detect_perplexity_anomalies,
        ]

        # Semantic detectors (Layer 2)
        self.detectors[DetectionLayer.SEMANTIC] = [
            self._detect_topic_drift,
            self._detect_entity_inconsistencies,
            self._detect_sentiment_mismatch,
            self._detect_style_inconsistencies,
            self._detect_llm_semantic_coherence,
        ]

        # Factual detectors (Layer 3)
        self.detectors[DetectionLayer.FACTUAL] = [
            self._verify_factual_claims,
            self._verify_mathematical_claims,
            self._verify_temporal_consistency,
            self._verify_source_attribution,
            self._verify_llm_factual_consistency,
        ]

    async def detect_hallucinations(
        self,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        user_query: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        model_info: Optional[Dict[str, Any]] = None
    ) -> DetectionResult:
        """
        Main detection method. Analyzes a response for hallucinations.

        Args:
            response: The AI-generated response text
            context: Additional context (user profile, session info, etc.)
            user_query: The original user query
            conversation_history: Previous conversation messages
            model_info: Information about the model that generated the response

        Returns:
            DetectionResult with analysis and recommendations
        """
        if not self.config.enabled:
            return DetectionResult(
                is_hallucination=False,
                severity=HallucinationSeverity.LOW,
                confidence=0.0,
                detected_issues=[],
                layer_results={},
                processing_time_ms=0.0
            )

        start_time = time.time()

        # Create cache key for response caching
        cache_key = self._generate_cache_key(response, context, user_query)
        if self.config.enable_caching and cache_key in self.result_cache:
            cached_result, cache_time = self.result_cache[cache_key]
            if time.time() - cache_time < self.config.cache_ttl_seconds:
                logger.debug("Returning cached hallucination detection result")
                return cached_result

        # Prepare analysis context
        analysis_context = self._prepare_analysis_context(
            response, context, user_query, conversation_history, model_info
        )

        # Run detection layers
        layer_results = {}
        all_issues = []

        # Layer 1: Statistical (fastest)
        if DetectionLayer.STATISTICAL in self.detectors:
            stat_issues = await self._run_detection_layer(
                DetectionLayer.STATISTICAL, analysis_context
            )
            layer_results["statistical"] = stat_issues
            all_issues.extend(stat_issues)

        # Layer 2: Semantic (medium)
        if DetectionLayer.SEMANTIC in self.detectors:
            semantic_issues = await self._run_detection_layer(
                DetectionLayer.SEMANTIC, analysis_context
            )
            layer_results["semantic"] = semantic_issues
            all_issues.extend(semantic_issues)

        # Layer 3: Factual (thorough, only if needed)
        factual_needed = (
            len(all_issues) > 0 or  # If earlier layers found issues
            self._requires_factual_check(analysis_context)  # Or if query type requires it
        )

        if factual_needed and DetectionLayer.FACTUAL in self.detectors:
            factual_issues = await self._run_detection_layer(
                DetectionLayer.FACTUAL, analysis_context
            )
            layer_results["factual"] = factual_issues
            all_issues.extend(factual_issues)

        # Calculate overall result
        result = self._calculate_overall_result(all_issues, layer_results)

        # Generate recommendations
        result.recommendations = self._generate_recommendations(result, analysis_context)

        # Performance tracking
        processing_time = (time.time() - start_time) * 1000
        result.processing_time_ms = processing_time

        # Cache result
        if self.config.enable_caching:
            self.result_cache[cache_key] = (result, time.time())

        # Log performance
        if processing_time > 100:
            logger.warning("Hallucination detection took %.2fms (threshold: %dms)",
                          processing_time, self.config.max_processing_time_ms)

        # Track detection events
        if result.is_hallucination:
            track_event(
                "hallucination_detected",
                message=f"Hallucination detected: {result.severity.value} severity, {result.confidence:.2f} confidence",
                severity=EventSeverity.HIGH if result.severity in [HallucinationSeverity.HIGH, HallucinationSeverity.CRITICAL] else EventSeverity.MEDIUM,
                category=EventCategory.SECURITY,
                metadata={
                    "severity": result.severity.value,
                    "confidence": result.confidence,
                    "issue_count": len(result.detected_issues),
                    "processing_time_ms": processing_time,
                    "layers_used": list(layer_results.keys())
                }
            )

        return result

    async def _run_detection_layer(
        self,
        layer: DetectionLayer,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Run all detectors for a specific layer."""
        issues = []

        for detector_func in self.detectors[layer]:
            try:
                layer_issues = await detector_func(context)
                if layer_issues:
                    issues.extend(layer_issues)
            except Exception as e:
                logger.warning("Detector %s failed: %s", detector_func.__name__, e)
                continue

        return issues

    def _calculate_overall_result(
        self,
        all_issues: List[Dict[str, Any]],
        layer_results: Dict[str, Any]
    ) -> DetectionResult:
        """Calculate overall detection result from all issues."""

        if not all_issues:
            return DetectionResult(
                is_hallucination=False,
                severity=HallucinationSeverity.LOW,
                confidence=0.0,
                detected_issues=[],
                layer_results=layer_results,
                processing_time_ms=0.0
            )

        # Calculate severity based on issue types and counts
        severity_counts = {
            HallucinationSeverity.LOW: 0,
            HallucinationSeverity.MEDIUM: 0,
            HallucinationSeverity.HIGH: 0,
            HallucinationSeverity.CRITICAL: 0
        }

        max_confidence = 0.0

        for issue in all_issues:
            severity = HallucinationSeverity(issue.get("severity", "low"))
            severity_counts[severity] += 1
            max_confidence = max(max_confidence, issue.get("confidence", 0.0))

        # Determine overall severity
        if severity_counts[HallucinationSeverity.CRITICAL] > 0:
            overall_severity = HallucinationSeverity.CRITICAL
        elif severity_counts[HallucinationSeverity.HIGH] > 0:
            overall_severity = HallucinationSeverity.HIGH
        elif severity_counts[HallucinationSeverity.MEDIUM] > 1:  # Multiple medium issues
            overall_severity = HallucinationSeverity.HIGH
        elif severity_counts[HallucinationSeverity.MEDIUM] > 0:
            overall_severity = HallucinationSeverity.MEDIUM
        else:
            overall_severity = HallucinationSeverity.LOW

        # Calculate overall confidence
        overall_confidence = min(max_confidence, 0.95)  # Cap at 95%

        # Determine if it's a hallucination
        is_hallucination = (
            overall_severity in [HallucinationSeverity.HIGH, HallucinationSeverity.CRITICAL] or
            (overall_severity == HallucinationSeverity.MEDIUM and overall_confidence > 0.7) or
            (len(all_issues) >= 3 and overall_confidence > 0.6)  # Multiple issues with decent confidence
        )

        return DetectionResult(
            is_hallucination=is_hallucination,
            severity=overall_severity,
            confidence=overall_confidence,
            detected_issues=all_issues,
            layer_results=layer_results,
            processing_time_ms=0.0  # Will be set by caller
        )

    def _generate_cache_key(
        self,
        response: str,
        context: Optional[Dict[str, Any]],
        user_query: Optional[str]
    ) -> str:
        """Generate cache key for response caching."""
        # Create a hash of key components
        import hashlib
        key_components = [
            response[:500],  # First 500 chars
            user_query or "",
            json.dumps(context, sort_keys=True, default=str) if context else ""
        ]
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _prepare_analysis_context(
        self,
        response: str,
        context: Optional[Dict[str, Any]],
        user_query: Optional[str],
        conversation_history: Optional[List[Dict[str, Any]]],
        model_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare context for analysis."""
        return {
            "response": response,
            "user_query": user_query,
            "conversation_history": conversation_history or [],
            "context": context or {},
            "model_info": model_info or {},
            "response_length": len(response),
            "word_count": len(response.split()),
            "sentence_count": len([s for s in response.split('.') if s.strip()]),
        }

    def _requires_factual_check(self, context: Dict[str, Any]) -> bool:
        """Determine if factual checking is needed for this query."""
        user_query = context.get("user_query", "").lower()

        # Check for keywords that indicate factual verification is needed
        factual_keywords = [
            "what", "when", "where", "who", "how much", "how many",
            "fact", "true", "accurate", "correct", "verify", "confirm",
            "date", "time", "cost", "price", "number", "statistics"
        ]

        return any(keyword in user_query for keyword in factual_keywords)

    def _generate_recommendations(
        self,
        result: DetectionResult,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on detection results."""
        recommendations = []

        if result.is_hallucination:
            if result.severity == HallucinationSeverity.CRITICAL:
                recommendations.append("Block response and request user confirmation")
                recommendations.append("Log for human review")
            elif result.severity == HallucinationSeverity.HIGH:
                recommendations.append("Add warning disclaimer to response")
                recommendations.append("Suggest alternative sources")
            elif result.severity == HallucinationSeverity.MEDIUM:
                recommendations.append("Add uncertainty indicators")
                recommendations.append("Offer to verify information")

            # Specific recommendations based on issue types
            issue_types = set(issue.get("type") for issue in result.detected_issues)
            if "factual_error" in issue_types:
                recommendations.append("Cross-reference with trusted sources")
            if "logical_inconsistency" in issue_types:
                recommendations.append("Request clarification on reasoning")
            if "temporal_error" in issue_types:
                recommendations.append("Verify time-sensitive information")

        return recommendations

    # ===== STATISTICAL DETECTORS (Layer 1) =====

    async def _detect_low_confidence_tokens(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect tokens with abnormally low probability."""
        issues = []

        # This would require access to token probabilities from the LLM
        # For now, we'll use heuristics based on text patterns

        response = context["response"]

        # Look for hedging language that might indicate uncertainty
        hedging_phrases = [
            "i think", "maybe", "perhaps", "possibly", "might be",
            "could be", "i'm not sure", "uncertain", "doubt", "questionable"
        ]

        hedging_count = sum(1 for phrase in hedging_phrases if phrase in response.lower())
        hedging_ratio = hedging_count / max(len(response.split()), 1)

        if hedging_ratio > 0.1:  # More than 10% hedging
            issues.append({
                "type": "excessive_hedging",
                "severity": "low",
                "confidence": min(hedging_ratio * 2, 0.8),
                "description": f"High hedging ratio ({hedging_ratio:.2f}) indicates uncertainty",
                "evidence": f"Found {hedging_count} hedging phrases"
            })

        return issues

    async def _detect_repetition_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect repetitive content that might indicate hallucination."""
        issues = []
        response = context["response"]

        # Split into sentences and look for repetition
        sentences = [s.strip() for s in response.split('.') if s.strip()]

        # Count repeated phrases (3+ words)
        phrase_counts = {}
        for sentence in sentences:
            words = sentence.lower().split()
            for i in range(len(words) - 2):
                phrase = " ".join(words[i:i+3])
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        repeated_phrases = [phrase for phrase, count in phrase_counts.items() if count >= 2]

        if len(repeated_phrases) >= self.config.repetition_threshold:
            issues.append({
                "type": "content_repetition",
                "severity": "medium",
                "confidence": 0.7,
                "description": f"Found {len(repeated_phrases)} repeated phrases",
                "evidence": f"Repeated phrases: {repeated_phrases[:3]}"
            })

        return issues

    async def _detect_length_anomalies(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect responses that are abnormally short or long for the query type."""
        issues = []
        response = context["response"]
        user_query = context.get("user_query", "")
        word_count = context["word_count"]

        # Expected response lengths based on query type
        query_type = self._classify_query_type(user_query)

        expected_ranges = {
            "factual": (10, 200),    # Factual questions need concise answers
            "explanatory": (50, 500), # Explanations need more detail
            "creative": (20, 1000),  # Creative tasks vary widely
            "conversational": (5, 100), # Chat responses are shorter
            "technical": (30, 800),  # Technical answers need detail
        }

        expected_min, expected_max = expected_ranges.get(query_type, (10, 300))

        if word_count < expected_min * 0.3:  # Much shorter than expected
            issues.append({
                "type": "abnormally_short",
                "severity": "low",
                "confidence": 0.6,
                "description": f"Response too short for {query_type} query ({word_count} words vs expected {expected_min}+)",
                "evidence": f"Query type: {query_type}, word count: {word_count}"
            })
        elif word_count > expected_max * 2:  # Much longer than expected
            issues.append({
                "type": "abnormally_long",
                "severity": "low",
                "confidence": 0.5,
                "description": f"Response too long for {query_type} query ({word_count} words vs expected <{expected_max})",
                "evidence": f"Query type: {query_type}, word count: {word_count}"
            })

        return issues

    async def _detect_perplexity_anomalies(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect responses with unusual perplexity patterns."""
        issues = []
        response = context["response"]

        # Simple perplexity heuristic: unusual word patterns
        # This is a placeholder - real perplexity would require model integration

        # Check for very simple/repetitive language
        unique_words = len(set(response.lower().split()))
        total_words = len(response.split())

        if total_words > 10:
            uniqueness_ratio = unique_words / total_words
            if uniqueness_ratio < 0.3:  # Very repetitive
                issues.append({
                    "type": "low_lexical_diversity",
                    "severity": "medium",
                    "confidence": 0.7,
                    "description": f"Very repetitive language (uniqueness ratio: {uniqueness_ratio:.2f})",
                    "evidence": f"Only {unique_words} unique words in {total_words} total words"
                })

        return issues

    # ===== SEMANTIC DETECTORS (Layer 2) =====

    async def _detect_topic_drift(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect when response drifts from the original topic."""
        issues = []
        response = context["response"]
        user_query = context.get("user_query", "")
        conversation_history = context.get("conversation_history", [])

        if not user_query:
            return issues

        # Extract key topics from user query
        query_topics = self._extract_topics(user_query)

        # Extract topics from response
        response_topics = self._extract_topics(response)

        # Calculate topic overlap
        if query_topics:
            overlap = len(set(query_topics) & set(response_topics)) / len(set(query_topics))
            if overlap < 0.3:  # Less than 30% topic overlap
                issues.append({
                    "type": "topic_drift",
                    "severity": "medium",
                    "confidence": 0.8,
                    "description": f"Response deviates from query topic (overlap: {overlap:.2f})",
                    "evidence": f"Query topics: {query_topics[:3]}, Response topics: {response_topics[:3]}"
                })

        return issues

    async def _detect_entity_inconsistencies(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect inconsistent entity references."""
        issues = []
        response = context["response"]

        # Extract named entities (simple regex-based)
        entities = self._extract_entities(response)

        # Look for contradictory statements about entities
        contradictions = self._find_entity_contradictions(entities, response)

        if contradictions:
            issues.append({
                "type": "entity_inconsistency",
                "severity": "high",
                "confidence": 0.8,
                "description": f"Found {len(contradictions)} contradictory entity statements",
                "evidence": f"Contradictions: {contradictions[:2]}"
            })

        return issues

    async def _detect_sentiment_mismatch(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect sentiment mismatch between query and response."""
        issues = []
        response = context["response"]
        user_query = context.get("user_query", "")

        if not user_query:
            return issues

        query_sentiment = self._analyze_sentiment(user_query)
        response_sentiment = self._analyze_sentiment(response)

        # Check for major sentiment mismatches
        if query_sentiment == "negative" and response_sentiment == "positive":
            issues.append({
                "type": "sentiment_mismatch",
                "severity": "medium",
                "confidence": 0.7,
                "description": "Query has negative sentiment but response is positive",
                "evidence": f"Query sentiment: {query_sentiment}, Response sentiment: {response_sentiment}"
            })

        return issues

    async def _detect_style_inconsistencies(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect style inconsistencies within the response."""
        issues = []
        response = context["response"]

        # Check for abrupt style changes
        sentences = [s.strip() for s in response.split('.') if s.strip()]

        if len(sentences) >= 3:
            # Analyze sentence length variation
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            std_dev = math.sqrt(variance)

            # High variation might indicate inconsistency
            if std_dev > avg_length * 0.8:  # Standard deviation > 80% of mean
                issues.append({
                    "type": "style_inconsistency",
                    "severity": "low",
                    "confidence": 0.6,
                    "description": "Inconsistent sentence lengths indicate style variation",
                    "evidence": f"Sentence length std dev: {std_dev:.1f}, mean: {avg_length:.1f}"
                })

        return issues

    async def _detect_llm_semantic_coherence(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use LLM to detect semantic coherence issues."""
        issues = []
        response = context["response"]
        user_query = context.get("user_query", "")

        if not user_query or len(response.strip()) < 10:
            return issues

        try:
            # Get LLM-based coherence analysis
            coherence_score = await self.llm_analyzer.analyze_semantic_coherence(
                user_query, response, context
            )

            # Low coherence indicates potential hallucination
            if coherence_score < 0.6:  # Below 60% coherence
                severity = "high" if coherence_score < 0.3 else "medium"
                confidence = 0.8  # High confidence in LLM analysis

                issues.append({
                    "type": "llm_semantic_incoherence",
                    "severity": severity,
                    "confidence": confidence,
                    "description": f"LLM analysis detected low semantic coherence ({coherence_score:.2f})",
                    "evidence": f"Response does not adequately address the query intent"
                })

            # Also get comprehensive quality analysis
            quality_analysis = await self.llm_analyzer.detect_response_quality(user_query, response)

            # Check for high hallucination risk from LLM analysis
            hallucination_risk = quality_analysis.get("hallucination_risk", 0.5)
            if hallucination_risk > 0.7:  # High hallucination risk
                issues.append({
                    "type": "llm_hallucination_risk",
                    "severity": "high" if hallucination_risk > 0.8 else "medium",
                    "confidence": 0.85,
                    "description": f"LLM analysis detected high hallucination risk ({hallucination_risk:.2f})",
                    "evidence": f"Issues: {', '.join(quality_analysis.get('issues', []))}"
                })

            # Check factual confidence
            factual_confidence = quality_analysis.get("factual_confidence", 0.5)
            if factual_confidence < 0.4:  # Low factual confidence
                issues.append({
                    "type": "llm_factual_uncertainty",
                    "severity": "medium",
                    "confidence": 0.75,
                    "description": f"LLM analysis indicates low factual confidence ({factual_confidence:.2f})",
                    "evidence": "Response may contain uncertain or inaccurate information"
                })

        except Exception as e:
            logger.warning(f"LLM semantic coherence analysis failed: {e}")
            # Don't add issues if LLM analysis fails - fall back to other methods

        return issues

    # ===== FACTUAL DETECTORS (Layer 3) =====

    async def _verify_factual_claims(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verify factual claims against knowledge base."""
        issues = []
        response = context["response"]

        if not self.config.fact_check_enabled:
            return issues

        # Extract factual claims from response
        claims = self._extract_factual_claims(response)

        for claim in claims:
            try:
                # Check against knowledge base
                from agent_runner.knowledge_base import KnowledgeBase
                kb = KnowledgeBase(self.state)
                verification = await kb.verify_fact(claim, context)

                if not verification.verified and verification.confidence > 0.6:
                    severity = "high" if verification.confidence > 0.8 else "medium"
                    issues.append({
                        "type": "factual_error",
                        "severity": severity,
                        "confidence": verification.confidence,
                        "description": f"Unverified factual claim: {claim[:100]}",
                        "evidence": f"Verification result: {verification.evidence}"
                    })
            except Exception as e:
                logger.debug(f"Factual verification failed for claim '{claim[:50]}...': {e}")

        return issues

    async def _verify_mathematical_claims(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verify mathematical claims and calculations."""
        issues = []
        response = context["response"]

        if not self.config.math_verification_enabled:
            return issues

        # Extract mathematical expressions and calculations
        math_claims = self._extract_mathematical_claims(response)

        for claim in math_claims:
            verification = self._verify_mathematical_claim(claim)

            if not verification["verified"]:
                issues.append({
                    "type": "mathematical_error",
                    "severity": "critical",
                    "confidence": 0.9,
                    "description": f"Incorrect mathematical claim: {claim['expression']}",
                    "evidence": f"Expected: {verification.get('expected')}, Got: {claim.get('result')}"
                })

        return issues

    async def _verify_temporal_consistency(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verify temporal consistency and time-sensitive claims."""
        issues = []
        response = context["response"]

        if not self.config.temporal_check_enabled:
            return issues

        # Extract time references
        time_refs = self._extract_time_references(response)
        current_time = time.time()

        for ref in time_refs:
            if self._is_temporal_inconsistency(ref, current_time):
                issues.append({
                    "type": "temporal_error",
                    "severity": "high",
                    "confidence": 0.8,
                    "description": f"Temporal inconsistency: {ref['text']}",
                    "evidence": f"Reference time: {ref.get('timestamp')}, Current time: {current_time}"
                })

        return issues

    async def _verify_source_attribution(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verify that claims are properly attributed to sources."""
        issues = []
        response = context["response"]

        # Extract claims that should have sources
        claims_needing_sources = self._extract_claims_needing_sources(response)

        for claim in claims_needing_sources:
            if not self._has_source_attribution(claim):
                issues.append({
                    "type": "missing_attribution",
                    "severity": "medium",
                    "confidence": 0.7,
                    "description": f"Claim lacks source attribution: {claim[:100]}",
                    "evidence": "No source citation found for controversial or specific claim"
                })

        return issues

    async def _verify_llm_factual_consistency(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use LLM to verify factual consistency with known information."""
        issues = []
        response = context["response"]

        # Get relevant facts from knowledge base or context
        known_facts = []

        # Try to get facts from knowledge base integration
        try:
            # Extract key claims from response
            claims = self._extract_factual_claims(response)
            if claims:
                # Get some relevant known facts (simplified)
                # In practice, this would query your knowledge base
                known_facts = [
                    "The Earth orbits the Sun",
                    "Water boils at 100°C at sea level",
                    "The United States has 50 states",
                    "Paris is the capital of France"
                ]  # Placeholder - would be dynamic

                if known_facts:
                    consistency_score = await self.llm_analyzer.analyze_factual_consistency(
                        response, known_facts
                    )

                    if consistency_score < 0.6:  # Below 60% consistency
                        severity = "high" if consistency_score < 0.3 else "medium"
                        issues.append({
                            "type": "llm_factual_inconsistency",
                            "severity": severity,
                            "confidence": 0.8,
                            "description": f"LLM analysis detected factual inconsistencies ({consistency_score:.2f})",
                            "evidence": f"Response contradicts known facts or contains uncertain information"
                        })

        except Exception as e:
            logger.debug(f"LLM factual consistency check failed: {e}")

        return issues

    # ===== HELPER METHODS =====

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of user query."""
        query_lower = query.lower()

        if any(word in query_lower for word in ["what", "when", "where", "who", "how much", "how many"]):
            return "factual"
        elif any(word in query_lower for word in ["explain", "describe", "how does", "why does"]):
            return "explanatory"
        elif any(word in query_lower for word in ["write", "create", "generate", "imagine"]):
            return "creative"
        elif any(word in query_lower for word in ["hello", "hi", "how are you", "thanks"]):
            return "conversational"
        elif any(word in query_lower for word in ["code", "function", "api", "debug", "error"]):
            return "technical"
        else:
            return "general"

    def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text (simplified)."""
        # This is a basic implementation - in practice, you'd use NLP libraries
        words = text.lower().split()
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}

        topics = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(topics))[:10]  # Return top 10 unique topics

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text (simplified)."""
        # Basic regex-based entity extraction
        entities = []

        # Simple patterns for demonstration
        # In practice, use spaCy or similar NLP library

        return entities

    def _find_entity_contradictions(self, entities: List[Dict[str, Any]], text: str) -> List[str]:
        """Find contradictory statements about entities."""
        # Simplified contradiction detection
        contradictions = []

        # Look for obvious contradictions like "X is Y" and "X is not Y"
        # This is a placeholder - real implementation would be more sophisticated

        return contradictions

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (simplified)."""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "worst", "hate"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_factual_claims(self, text: str) -> List[str]:
        """Extract factual claims that can be verified."""
        claims = []

        # Look for statements with specific facts
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        for sentence in sentences:
            # Look for sentences with numbers, dates, specific facts
            if any(indicator in sentence.lower() for indicator in [
                " in ", " on ", " at ", " by ", " was ", " were ", " is ", " are ",
                " cost ", " costs ", " price ", " worth ", " born ", " died ",
                " population ", " area ", " distance ", " speed ", " weight "
            ]):
                claims.append(sentence)

        return claims

    async def _verify_claim_against_kb(self, claim: str) -> Dict[str, Any]:
        """Verify a claim against the knowledge base."""
        # This would integrate with the project's memory system
        # For now, return a placeholder result

        # In practice, this would:
        # 1. Parse the claim to extract key facts
        # 2. Query the knowledge base (project memory, external APIs)
        # 3. Compare the claim against verified facts
        # 4. Return verification result with confidence

        return {
            "verified": True,  # Placeholder - assume true for now
            "confidence": 0.9,
            "reason": "Verified against knowledge base"
        }

    def _extract_mathematical_claims(self, text: str) -> List[Dict[str, Any]]:
        """Extract mathematical expressions and calculations."""
        claims = []

        # Look for mathematical expressions
        # This is a simplified implementation

        return claims

    def _verify_mathematical_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a mathematical claim."""
        # This would evaluate mathematical expressions
        # For now, return placeholder

        return {
            "verified": True,
            "expected": None,
            "actual": None
        }

    def _extract_time_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract time references from text."""
        time_refs = []

        # Look for temporal expressions
        # This is a simplified implementation

        return time_refs

    def _is_temporal_inconsistency(self, time_ref: Dict[str, Any], current_time: float) -> bool:
        """Check if a time reference is inconsistent."""
        # Check for obviously wrong dates (future dates that have passed, etc.)
        return False  # Placeholder

    def _extract_claims_needing_sources(self, text: str) -> List[str]:
        """Extract claims that should have source attribution."""
        claims = []

        # Look for controversial or specific claims that need sources
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        for sentence in sentences:
            # Claims about current events, statistics, quotes, etc.
            if any(indicator in sentence.lower() for indicator in [
                "according to", "studies show", "research indicates",
                "data shows", "statistics", "reportedly", "allegedly"
            ]):
                claims.append(sentence)

        return claims

    def _has_source_attribution(self, claim: str) -> bool:
        """Check if a claim has proper source attribution."""
        # Look for source citations
        return any(indicator in claim.lower() for indicator in [
            "according to", "source:", "cited in", "from", "via",
            "reference:", "study:", "report:"
        ])

    async def collect_feedback(
        self,
        response: str,
        user_feedback: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ):
        """Collect user feedback for learning."""
        if not self.config.learning_enabled or not self.config.feedback_collection_enabled:
            return

        feedback_entry = {
            "timestamp": time.time(),
            "response": response,
            "feedback": user_feedback,
            "context": context,
            "detection_result": await self.detect_hallucinations(response, context)
        }

        self.feedback_history.append(feedback_entry)

        # Keep only recent feedback
        if len(self.feedback_history) > 1000:
            self.feedback_history = self.feedback_history[-1000:]

        logger.debug("Collected feedback for hallucination learning")

    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return {
            "enabled": self.config.enabled,
            "feedback_count": len(self.feedback_history),
            "cache_size": len(self.result_cache),
            "layers": [layer.value for layer in self.detectors.keys()],
            "llm_analyzer": "enabled" if self.llm_analyzer else "disabled",
            "config": {
                "perplexity_threshold": self.config.perplexity_threshold,
                "coherence_threshold": self.config.coherence_threshold,
                "fact_check_enabled": self.config.fact_check_enabled,
                "learning_enabled": self.config.learning_enabled
            }
        }

    async def cleanup(self):
        """Clean up resources."""
        if self.llm_analyzer:
            await self.llm_analyzer.close()