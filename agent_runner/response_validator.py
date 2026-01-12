"""
Response Validation System

Validates AI-generated responses against known high-confidence facts to prevent hallucinations.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.response_validator")


class ResponseValidationResult:
    """Result of response validation."""

    def __init__(self, is_valid: bool, contradictions: List[Dict], warnings: List[str]):
        self.is_valid = is_valid
        self.contradictions = contradictions
        self.warnings = warnings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "contradictions": self.contradictions,
            "warnings": self.warnings
        }


class ResponseValidator:
    """Validates AI responses against known facts to prevent hallucinations."""

    def __init__(self, state: AgentState):
        self.state = state

        # Known models and capabilities in the system
        self.known_models = {
            # Ollama models
            'llama3.3', 'llama3.1', 'mistral', 'qwen3', 'qwen2.5', 'mxbai-embed-large',
            'llama3.2-vision', 'qwq', 'gemma3', 'llama2',
            # OpenAI models
            'gpt-5.1', 'gpt-4o',
            # Other providers
            'grok-3'  # xAI
        }

        # Known capabilities (not separate models)
        self.known_capabilities = {
            'translation', 'summarization', 'sentiment analysis', 'named entity recognition',
            'speech synthesis', 'speech recognition', 'text generation', 'conversation',
            'creative writing', 'poetry generation', 'storytelling'
        }

        # Known impossible/recent events that definitely haven't happened
        # These are used to detect hallucinations about current events
        self.impossible_events = {
            'covid_19_pandemic_ended': True,  # WHO hasn't declared this
            'spacex_starship_orbit': True,  # Hasn't achieved orbital flight yet
            'neuralink_brain_computer_interface': True,  # Not publicly available yet
            'ukraine_russia_ceasefire_donbass': True,  # No such agreement exists
            'google_deepfake_detection_tool': True,  # No such specific tool announced
            'microplastics_human_health_study': True,  # Not a specific breakthrough
            'amazon_mgm_acquisition': True,  # Didn't happen for $8.45B
        }

    async def validate_response(self, response: str, context: Optional[Dict[str, Any]] = None) -> ResponseValidationResult:
        """
        Validate a response against known high-confidence facts.

        Args:
            response: The AI-generated response text
            context: Optional context about the query/user

        Returns:
            ValidationResult indicating if response is valid and any issues found
        """
        contradictions = []
        warnings = []

        try:
            # Extract factual claims from the response
            claims = self._extract_factual_claims(response)

            # Check each claim against known facts
            for claim in claims:
                contradiction = await self._verify_claim(claim, context)
                if contradiction:
                    contradictions.append(contradiction)

            # Check for location-specific claims (high priority)
            location_issues = await self._validate_location_claims(response)
            if location_issues:
                contradictions.extend(location_issues)

            # Check for model/capability claims (high priority)
            model_issues = self._validate_model_claims(response)
            if model_issues:
                contradictions.extend(model_issues)

            # Check for time-based hallucinations and impossible events (high priority)
            time_issues = self._validate_time_hallucinations(response)
            if time_issues:
                contradictions.extend(time_issues)

            # Generate warnings for potentially problematic claims
            claim_warnings = self._generate_claim_warnings(claims)
            warnings.extend(claim_warnings)

        except Exception as e:
            logger.warning(f"Response validation failed: {e}")
            warnings.append(f"Validation failed: {e}")

        is_valid = len(contradictions) == 0

        return ResponseValidationResult(
            is_valid=is_valid,
            contradictions=contradictions,
            warnings=warnings
        )

    def _extract_factual_claims(self, response: str) -> List[Dict[str, Any]]:
        """Extract factual claims from response text."""
        claims = []

        # Patterns for different types of factual claims
        patterns = [
            # Location claims: "I am in X", "You live in X", "Located in X"
            (r"(?:I am in|you (?:live|are) in|located in|based in)\s+([A-Za-z\s,]+)", "location"),
            # Identity claims: "You are X", "Your name is X"
            (r"(?:you are|your name is|you work as)\s+([A-Za-z\s,]+)", "identity"),
            # Possession claims: "you have X", "your X is"
            (r"(?:you have|your)\s+([A-Za-z\s]+)\s+(?:is|are)\s+([A-Za-z0-9\s,]+)", "possession"),
            # Time claims: "it is X time", "current time is X"
            (r"(?:it is|current time is|the time is)\s+([0-9:APM\s]+)", "time"),
        ]

        for pattern, claim_type in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle patterns with multiple capture groups
                    claims.append({
                        "type": claim_type,
                        "text": " ".join(match),
                        "full_match": match
                    })
                else:
                    claims.append({
                        "type": claim_type,
                        "text": match.strip(),
                        "full_match": match
                    })

        return claims

    async def _verify_claim(self, claim: Dict[str, Any], context: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Verify a claim against known facts."""
        claim_type = claim.get("type")
        claim_text = claim.get("text", "").lower()

        try:
            if claim_type == "location":
                return await self._verify_location_claim(claim_text)
            elif claim_type == "identity":
                return await self._verify_identity_claim(claim_text)
            elif claim_type == "time":
                return await self._verify_time_claim(claim_text)
            else:
                # Generic fact checking
                return await self._verify_generic_claim(claim_text)

        except Exception as e:
            logger.debug(f"Claim verification failed for {claim_type}: {claim_text} - {e}")
            return None

    async def _verify_location_claim(self, location_text: str) -> Optional[Dict[str, Any]]:
        """Verify location claims against user profile."""
        # Check if this contradicts known user location
        if "newark" in location_text and "ohio" in location_text:
            # Check if user profile actually says Granville
            if hasattr(self.state, 'memory') and self.state.memory:
                try:
                    # Query user profile for actual location
                    profile_facts = await self.state.memory.query_facts(
                        "granville ohio OR 341 orchard drive",
                        kb_id="project_registry/user_profile",
                        limit=3
                    )

                    if profile_facts and profile_facts.get("ok"):
                        facts = profile_facts.get("result", [])
                        for fact in facts:
                            content = fact.get("content", "").lower()
                            if "granville" in content and "ohio" in content:
                                return {
                                    "claim": f"location: {location_text}",
                                    "contradiction": "User profile indicates Granville, OH",
                                    "confidence": fact.get("confidence", 1.0),
                                    "severity": "high"
                                }
                except Exception as e:
                    logger.debug(f"Location verification failed: {e}")

        return None

    async def _verify_identity_claim(self, identity_text: str) -> Optional[Dict[str, Any]]:
        """Verify identity claims."""
        # Check against known user identity from profile
        if hasattr(self.state, 'memory') and self.state.memory:
            try:
                profile_facts = await self.state.memory.query_facts(
                    "name is OR I am OR my name",
                    kb_id="project_registry/user_profile",
                    limit=3
                )

                if profile_facts and profile_facts.get("ok"):
                    facts = profile_facts.get("result", [])
                    for fact in facts:
                        content = fact.get("content", "").lower()
                        if "ed" in content or "doctor" in content or "radiologist" in content:
                            # This is consistent with profile
                            return None

                # If we can't verify the identity claim, flag it
                return {
                    "claim": f"identity: {identity_text}",
                    "contradiction": "Cannot verify identity claim against user profile",
                    "confidence": 0.5,
                    "severity": "medium"
                }
            except Exception as e:
                logger.debug(f"Identity verification failed: {e}")

        return None

    async def _verify_time_claim(self, time_text: str) -> Optional[Dict[str, Any]]:
        """Verify time claims are reasonable."""
        # This is a simple reasonableness check
        # Time claims are generally acceptable unless obviously wrong
        return None

    async def _verify_generic_claim(self, claim_text: str) -> Optional[Dict[str, Any]]:
        """Generic claim verification against known facts."""
        if hasattr(self.state, 'memory') and self.state.memory:
            try:
                # Search for contradictory information
                contradiction_results = await self.state.memory.query_facts(
                    f"NOT {claim_text} OR contradicts {claim_text}",
                    limit=3
                )

                if contradiction_results and contradiction_results.get("ok"):
                    facts = contradiction_results.get("result", [])
                    if facts:
                        return {
                            "claim": claim_text,
                            "contradiction": f"Found {len(facts)} contradictory facts",
                            "confidence": max(f.get("confidence", 0.5) for f in facts),
                            "severity": "medium"
                        }
            except Exception as e:
                logger.debug(f"Generic claim verification failed: {e}")

        return None

    async def _validate_location_claims(self, response: str) -> List[Dict[str, Any]]:
        """Special validation for location claims in response."""
        issues = []

        # Look for location mentions in the response
        location_patterns = [
            r"in ([A-Za-z\s,]+(?:Ohio|OH|United States|USA))",
            r"located in ([A-Za-z\s,]+(?:Ohio|OH))",
            r"based in ([A-Za-z\s,]+(?:Ohio|OH))",
            r"from ([A-Za-z\s,]+(?:Ohio|OH))"
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                issue = await self._verify_location_claim(match.lower())
                if issue:
                    issues.append(issue)

        return issues

    def _validate_time_hallucinations(self, response: str) -> List[Dict[str, Any]]:
        """
        Detect hallucinations about impossible current events and time-based fabrications.
        """
        contradictions = []
        response_lower = response.lower()

        # Check for impossible events that definitely haven't happened
        for event_key, is_impossible in self.impossible_events.items():
            if is_impossible:
                # Map event keys to detection patterns
                event_patterns = {
                    'covid_19_pandemic_ended': [
                        'who declares end to covid',
                        'covid-19 pandemic ended',
                        'world health organization declares covid over'
                    ],
                    'spacex_starship_orbit': [
                        'spacex successfully launches starship',
                        'starship prototype launched',
                        'starship achieves orbit'
                    ],
                    'neuralink_brain_computer_interface': [
                        'elon musk unveils neuralink',
                        'neuralink brain-computer interface',
                        'neuralink publicly available'
                    ],
                    'ukraine_russia_ceasefire_donbass': [
                        'ukraine and russia agree on ceasefire',
                        'ceasefire in donbass',
                        'russia-ukraine peace agreement'
                    ],
                    'google_deepfake_detection_tool': [
                        'google announces new ai tool for detecting deepfakes'
                    ],
                    'microplastics_human_health_study': [
                        'new study reveals link between microplastics and human health'
                    ],
                    'amazon_mgm_acquisition': [
                        'amazon acquires mgm studios for'
                    ]
                }

                patterns = event_patterns.get(event_key, [])
                for pattern in patterns:
                    if pattern in response_lower:
                        contradictions.append({
                            "category": "impossible_event",
                            "severity": "high",
                            "claim": f"Event that definitely hasn't happened: {pattern}",
                            "evidence": f"This event ({event_key}) is known to be impossible/fake",
                            "confidence": 0.95
                        })
                        break  # Only report once per event type

        # Check for time-based impossibilities (events that couldn't happen by current date)
        import datetime
        current_year = datetime.datetime.now().year

        # Events claiming to happen in future years when current year is known
        future_year_patterns = [
            r'(\d{4})\s+(rose bowl|championship|olympic)',  # Sports events in specific years
            r'(\d{4})\s+(presidential election|election)',  # Elections in specific years
        ]

        for pattern in future_year_patterns:
            matches = re.findall(pattern, response_lower)
            for match in matches:
                year = int(match[0]) if isinstance(match, tuple) else int(match)
                if year > current_year + 1:  # Events more than 1 year in future are suspicious
                    contradictions.append({
                        "category": "future_event_impossible",
                        "severity": "medium",
                        "claim": f"Event dated {year} when current year is {current_year}",
                        "evidence": "Events dated far in the future are likely fabricated",
                        "confidence": 0.8
                    })

        return contradictions

    def _validate_model_claims(self, response: str) -> List[Dict[str, Any]]:
        """Validate claims about internal models and capabilities."""
        issues = []
        response_lower = response.lower()

        # Check for claims about specific models that the system doesn't actually run
        import re

        # Pattern to find model names being claimed as "internal" or "running"
        model_claim_pattern = r'\b(BERT|RoBERTa|DistilBERT|XLNet|ALBERT|T5|GPT-3|MobileBERT|Transformers?|RNNs?|CNNs?|Neural Networks?)\b'

        claimed_models = re.findall(model_claim_pattern, response, re.IGNORECASE)
        claimed_models = list(set(m.lower() for m in claimed_models))  # Remove duplicates

        for claimed_model in claimed_models:
            # Check if this is a real model that the system actually runs
            if not any(known.lower() in claimed_model for known in self.known_models):
                # This model is not in our known models list
                issues.append({
                    "claim": f"claims to run model: {claimed_model}",
                    "contradiction": f"System does not run '{claimed_model}' - only uses Ollama and OpenAI models",
                    "confidence": 0.9,
                    "severity": "high",
                    "category": "false_model_claim"
                })

        # Check for claims about specific models that don't exist
        for model in self.known_models:
            if model in response_lower:
                # This is okay - the model actually exists
                continue

        # Look for patterns of model claims
        import re

        # Pattern for model names (capitalized words that might be fake models)
        fake_model_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+\d+)?)\s*-\s*a model'
        matches = re.findall(fake_model_pattern, response)

        # Also check for compound model names like "MegaModel 4"
        compound_model_pattern = r'\b([A-Z][a-z]+[A-Z][a-z]+(?:\s+\d+)?)\s*-\s*a model'
        compound_matches = re.findall(compound_model_pattern, response)
        matches.extend(compound_matches)

        for match in matches:
            model_name = match.strip()
            # Skip known real models
            if any(known.lower() in model_name.lower() for known in self.known_models):
                continue

            # Check if this looks like a made-up model name
            if self._is_likely_fake_model(model_name):
                issues.append({
                    "claim": f"model: {model_name}",
                    "contradiction": f"Model '{model_name}' does not exist in system configuration",
                    "confidence": 0.95,
                    "severity": "high",
                    "category": "fake_model"
                })

        # Check for capability claims that are misrepresented as separate models
        capability_claims = [
            ("whisper", "Whisper is a speech-to-text capability, not a separate internal LLM"),
            ("speaker", "Speech synthesis is a capability, not a separate internal LLM"),
            ("translator", "Translation is a capability, not a separate internal LLM"),
            ("summarizer", "Summarization is a capability, not a separate internal LLM"),
            ("sentiment analyzer", "Sentiment analysis is a capability, not a separate internal LLM"),
            ("named entity recognizer", "Named entity recognition is a capability, not a separate internal LLM"),
        ]

        for capability, explanation in capability_claims:
            if capability in response_lower and "model" in response_lower:
                # Find the context around this claim
                context_start = max(0, response_lower.find(capability) - 50)
                context_end = min(len(response_lower), response_lower.find(capability) + 100)
                context = response[context_start:context_end]

                if "llm" in context.lower() or "model" in context.lower():
                    issues.append({
                        "claim": f"capability misrepresented as model: {capability}",
                        "contradiction": explanation,
                        "confidence": 0.9,
                        "severity": "medium",
                        "category": "misrepresented_capability"
                    })

        return issues

    def _is_likely_fake_model(self, model_name: str) -> bool:
        """Determine if a model name is likely fake/invented."""
        fake_indicators = [
            'megamodel', 'chatterbox', 'excalibur', 'scribe',  # The specific fake names we saw
            'a model optimized for',  # Generic model descriptions
            'a model designed to',
            'a model focused on',
            'a model specialized in',
            'a model that can'
        ]

        model_lower = model_name.lower()
        for indicator in fake_indicators:
            if indicator in model_lower:
                return True

        return False

    def _generate_claim_warnings(self, claims: List[Dict[str, Any]]) -> List[str]:
        """Generate warnings for potentially problematic claims."""
        warnings = []

        # Warn about claims with low verification confidence
        for claim in claims:
            if claim.get("confidence", 1.0) < 0.7:
                warnings.append(f"Low confidence claim: {claim.get('text', '')}")

        # Warn about speculative language
        speculative_phrases = ["might be", "could be", "possibly", "perhaps", "I think"]
        response_lower = " ".join(c.get("text", "") for c in claims).lower()

        for phrase in speculative_phrases:
            if phrase in response_lower:
                warnings.append(f"Response contains speculative language: '{phrase}'")
                break

        return warnings

    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get statistics about validation performance."""
        return {
            "validator_status": "active",
            "supported_claim_types": ["location", "identity", "time", "generic"],
            "validation_methods": ["user_profile_check", "fact_contradiction_search"],
            "confidence_thresholds": {
                "high_confidence": 0.9,
                "medium_confidence": 0.7,
                "low_confidence": 0.4
            }
        }


# Global validator instance
_response_validator = None

def get_response_validator(state: AgentState) -> ResponseValidator:
    """Get or create the global response validator instance."""
    global _response_validator
    if _response_validator is None:
        _response_validator = ResponseValidator(state)
    return _response_validator

async def validate_response(response: str, state: AgentState, context: Optional[Dict] = None) -> ResponseValidationResult:
    """Convenience function to validate a response."""
    validator = get_response_validator(state)
    return await validator.validate_response(response, context)