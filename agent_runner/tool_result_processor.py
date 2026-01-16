"""
Tool Result Processor - Quality Mitigation for Tool Result Truncation

Implements intelligent processing of tool results to preserve quality while
maintaining performance optimizations through adaptive truncation and
selective retention strategies.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger("agent_runner.tool_result_processor")


class QualityTier(Enum):
    """Quality tiers for result processing"""
    LOW = "low"       # Speed-optimized (50 chars)
    MEDIUM = "medium" # Balanced (100 chars)
    HIGH = "high"     # Quality-optimized (500 chars)
    MAX = "max"       # Full detail (2000 chars)


class TruncationStrategy(Enum):
    """Strategies for intelligent truncation"""
    HARD_CUTOFF = "hard_cutoff"           # Simple character limit
    ADAPTIVE_CONTENT = "adaptive_content" # Content-aware truncation
    STRUCTURED_PRESERVE = "structured_preserve" # Preserve JSON/lists
    ERROR_PRIORITY = "error_priority"     # Prioritize error information
    SUMMARY_BASED = "summary_based"       # AI-generated summaries


@dataclass
class ToolPolicy:
    """Policy for processing specific tool results"""
    max_chars: int = 100
    strategy: TruncationStrategy = TruncationStrategy.ADAPTIVE_CONTENT
    preserve_errors: bool = True
    preserve_counts: bool = True
    preserve_structure: bool = True
    critical: bool = False  # Always retain full results for critical tools


class ToolResultProcessor:
    """
    Intelligent processor for tool results that mitigates quality loss
    through adaptive truncation and selective retention.
    """

    def __init__(self, summarizer_client=None):
        self.tool_policies = self._initialize_tool_policies()
        self.quality_metrics = {
            "total_processed": 0,
            "truncated": 0,
            "full_retained": 0,
            "error_cases": 0,
            "adaptive_improvements": 0,
            "ai_summaries": 0
        }
        self.summarizer_client = summarizer_client  # For AI-driven summarization

    def _initialize_tool_policies(self) -> Dict[str, ToolPolicy]:
        """Initialize tool-specific processing policies"""
        return {
            # Critical diagnostic tools - retain full results
            'validate_config': ToolPolicy(
                max_chars=1000, strategy=TruncationStrategy.ERROR_PRIORITY,
                preserve_errors=True, critical=True
            ),
            'diagnose_system': ToolPolicy(
                max_chars=800, strategy=TruncationStrategy.ERROR_PRIORITY,
                preserve_errors=True, critical=True
            ),
            'run_terminal': ToolPolicy(
                max_chars=500, strategy=TruncationStrategy.ERROR_PRIORITY,
                preserve_errors=True, critical=True
            ),

            # Search tools - preserve structure and counts
            'grep': ToolPolicy(
                max_chars=300, strategy=TruncationStrategy.ADAPTIVE_CONTENT,
                preserve_counts=True, preserve_structure=True
            ),
            'find': ToolPolicy(
                max_chars=250, strategy=TruncationStrategy.STRUCTURED_PRESERVE,
                preserve_counts=True
            ),
            'web_search': ToolPolicy(
                max_chars=400, strategy=TruncationStrategy.STRUCTURED_PRESERVE,
                preserve_counts=True
            ),

            # File operations - preserve content structure
            'read_text': ToolPolicy(
                max_chars=600, strategy=TruncationStrategy.ERROR_PRIORITY,
                preserve_errors=True
            ),
            'list_dir': ToolPolicy(
                max_chars=200, strategy=TruncationStrategy.STRUCTURED_PRESERVE,
                preserve_counts=True
            ),

            # Analysis tools - preserve key insights
            'analyze_code': ToolPolicy(
                max_chars=400, strategy=TruncationStrategy.ERROR_PRIORITY,
                preserve_errors=True
            ),
            'check_syntax': ToolPolicy(
                max_chars=300, strategy=TruncationStrategy.ERROR_PRIORITY,
                preserve_errors=True
            ),

            # Simple tools - minimal truncation needed
            'calculate': ToolPolicy(max_chars=50, strategy=TruncationStrategy.HARD_CUTOFF),
            'get_weather': ToolPolicy(max_chars=100, strategy=TruncationStrategy.HARD_CUTOFF),
            'get_time': ToolPolicy(max_chars=50, strategy=TruncationStrategy.HARD_CUTOFF),
        }

    async def process_tool_result(
        self,
        tool_name: str,
        raw_result: str,
        quality_tier: QualityTier = QualityTier.MEDIUM,
        force_full: bool = False,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process a tool result with quality-aware truncation

        Args:
            tool_name: Name of the tool
            raw_result: Raw result string
            quality_tier: Quality requirements
            force_full: Force full result retention
            conversation_context: Current conversation state

        Returns:
            (processed_result, metadata)
        """
        self.quality_metrics["total_processed"] += 1

        # Check if we should retain full result
        if force_full or self._should_retain_full(tool_name, raw_result, conversation_context):
            self.quality_metrics["full_retained"] += 1
            return raw_result, {
                "truncated": False,
                "strategy": "full_retention",
                "reason": "force_full" if force_full else "policy_based"
            }

        # Get tool policy and adjust for quality tier
        policy = self.tool_policies.get(tool_name, ToolPolicy())
        adjusted_policy = self._adjust_policy_for_tier(policy, quality_tier)

        # Apply truncation strategy
        processed_result, metadata = await self._apply_truncation_strategy(
            raw_result, adjusted_policy, tool_name
        )

        # Track metrics
        if metadata["truncated"]:
            self.quality_metrics["truncated"] += 1
            if metadata.get("adaptive_improved"):
                self.quality_metrics["adaptive_improvements"] += 1

        if self._contains_errors(raw_result):
            self.quality_metrics["error_cases"] += 1

        metadata.update({
            "tool_name": tool_name,
            "original_length": len(raw_result),
            "processed_length": len(processed_result),
            "quality_tier": quality_tier.value
        })

        return processed_result, metadata

    def _should_retain_full(self, tool_name: str, result: str, context: Optional[Dict[str, Any]]) -> bool:
        """Determine if result should be retained in full"""
        policy = self.tool_policies.get(tool_name, ToolPolicy())

        # Critical tools always retain full results
        if policy.critical:
            return True

        # Error cases retain full results
        if self._contains_errors(result):
            return True

        # Short results don't need truncation
        if len(result) < 50:
            return True

        # Conversation context indicates detailed analysis needed
        if context and any(keyword in context.get("current_task", "").lower()
                          for keyword in ["debug", "analyze", "investigate", "troubleshoot"]):
            return True

        return False

    def _adjust_policy_for_tier(self, policy: ToolPolicy, quality_tier: QualityTier) -> ToolPolicy:
        """Adjust policy based on quality tier requirements"""
        tier_multipliers = {
            QualityTier.LOW: 0.5,
            QualityTier.MEDIUM: 1.0,
            QualityTier.HIGH: 2.0,
            QualityTier.MAX: 4.0
        }

        multiplier = tier_multipliers[quality_tier]

        return ToolPolicy(
            max_chars=int(policy.max_chars * multiplier),
            strategy=policy.strategy,
            preserve_errors=policy.preserve_errors,
            preserve_counts=policy.preserve_counts,
            preserve_structure=policy.preserve_structure,
            critical=policy.critical
        )

    async def _apply_truncation_strategy(
        self, result: str, policy: ToolPolicy, tool_name: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Apply the appropriate truncation strategy"""

        if len(result) <= policy.max_chars:
            return result, {"truncated": False, "strategy": "no_truncation_needed"}

        if policy.strategy == TruncationStrategy.HARD_CUTOFF:
            return self._hard_cutoff_truncation(result, policy.max_chars)

        elif policy.strategy == TruncationStrategy.ADAPTIVE_CONTENT:
            return await self._adaptive_content_truncation(result, policy, tool_name)

        elif policy.strategy == TruncationStrategy.STRUCTURED_PRESERVE:
            return self._structured_preserve_truncation(result, policy)

        elif policy.strategy == TruncationStrategy.ERROR_PRIORITY:
            return self._error_priority_truncation(result, policy)

        else:
            # Default to adaptive
            return self._adaptive_content_truncation(result, policy)

    def _hard_cutoff_truncation(self, result: str, max_chars: int) -> Tuple[str, Dict[str, Any]]:
        """Simple character limit truncation"""
        truncated = result[:max_chars - 3] + "..." if len(result) > max_chars else result
        return truncated, {
            "truncated": len(result) > max_chars,
            "strategy": "hard_cutoff"
        }

    async def _adaptive_content_truncation(self, result: str, policy: ToolPolicy, tool_name: str = "") -> Tuple[str, Dict[str, Any]]:
        """Content-aware adaptive truncation with AI summarization"""
        if len(result) <= policy.max_chars:
            return result, {"truncated": False, "strategy": "adaptive_no_cut"}

        # Try AI summarization first (if available and result is complex)
        if len(result) > 500:  # Only for substantial results
            ai_summary = await self.summarize_with_ai(tool_name, result, policy.max_chars)
            if ai_summary:
                return ai_summary, {
                    "truncated": True,
                    "strategy": "ai_summarization",
                    "adaptive_improved": True,
                    "ai_generated": True
                }

        # Try structured preservation
        if policy.preserve_structure and self._is_structured_content(result):
            return await self._structured_preserve_truncation(result, policy)

        # Prioritize error information
        if policy.preserve_errors and self._contains_errors(result):
            return await self._error_priority_truncation(result, policy)

        # Look for summary-worthy content
        summary_content = await self._extract_summary_content(result, policy.max_chars)

        if summary_content and len(summary_content) >= policy.max_chars * 0.8:
            return summary_content, {
                "truncated": True,
                "strategy": "adaptive_content",
                "adaptive_improved": True
            }

        # Fall back to smart cutoff
        return await self._smart_cutoff_truncation(result, policy.max_chars)

    async def _structured_preserve_truncation(self, result: str, policy: ToolPolicy) -> Tuple[str, Dict[str, Any]]:
        """Preserve JSON/list structure while truncating"""
        try:
            # Try JSON parsing
            if result.strip().startswith(('{', '[')):
                parsed = json.loads(result)
                if isinstance(parsed, list) and len(parsed) > 3:
                    truncated = parsed[:3]
                    return json.dumps(truncated) + f" ... and {len(parsed)-3} more items", {
                        "truncated": True,
                        "strategy": "structured_preserve",
                        "structure_type": "json_array",
                        "adaptive_improved": True
                    }
                elif isinstance(parsed, dict):
                    # Keep essential keys
                    essential_keys = ['error', 'status', 'count', 'total', 'success', 'message']
                    truncated = {k: v for k, v in parsed.items() if k in essential_keys}
                    if len(truncated) < len(parsed):
                        return json.dumps(truncated) + " ... (truncated)", {
                            "truncated": True,
                            "strategy": "structured_preserve",
                            "structure_type": "json_object",
                            "adaptive_improved": True
                        }
        except:
            pass

        # Fall back to adaptive
        return await self._adaptive_content_truncation(result, policy, tool_name)

    async def _error_priority_truncation(self, result: str, policy: ToolPolicy) -> Tuple[str, Dict[str, Any]]:
        """Prioritize error and critical information"""
        lines = result.split('\n')
        critical_lines = []
        normal_lines = []

        for line in lines:
            line_lower = line.lower()
            is_critical = any(keyword in line_lower for keyword in
                             ['error', 'failed', 'exception', 'critical', 'warning',
                              'cannot', 'unable', 'denied', 'invalid', 'not found',
                              'failed', 'timeout', 'connection refused'])

            if is_critical:
                # Keep more of critical lines
                critical_lines.append(line[:200])
            else:
                normal_lines.append(line[:100])

        # Prioritize critical content
        combined = critical_lines + normal_lines
        result = '\n'.join(combined)

        if len(result) > policy.max_chars:
            result = result[:policy.max_chars - 3] + "..."

        return result, {
            "truncated": len(result) < len('\n'.join(lines)),
            "strategy": "error_priority",
            "critical_lines": len(critical_lines),
            "adaptive_improved": len(critical_lines) > 0
        }

    async def _extract_summary_content(self, result: str, max_chars: int) -> Optional[str]:
        """Extract summary-worthy content from result"""
        lines = result.split('\n')

        # Look for summary patterns
        summary_patterns = [
            r'(?:found|returned|processed|total|summary)\s+(\d+)',
            r'(\d+)\s+(?:files?|items?|results?|entries?|errors?)',
            r'(?:completed|finished|done)\s+in\s+[\d\.]+',
        ]

        summary_lines = []
        for line in lines[:10]:  # Check first 10 lines
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in summary_patterns):
                summary_lines.append(line)

        if summary_lines:
            result = '\n'.join(summary_lines)
            if len(result) <= max_chars:
                return result

        return None

    async def _smart_cutoff_truncation(self, result: str, max_chars: int) -> Tuple[str, Dict[str, Any]]:
        """Smart cutoff that tries to end at sentence/word boundaries"""
        if len(result) <= max_chars:
            return result, {"truncated": False, "strategy": "smart_no_cut"}

        # Try to cut at sentence boundary
        truncated = result[:max_chars]
        sentence_end = max(
            truncated.rfind('. '),
            truncated.rfind('! '),
            truncated.rfind('? ')
        )

        if sentence_end > max_chars * 0.8:  # If we can keep most of the content
            truncated = result[:sentence_end + 1]
        else:
            # Try word boundary
            word_end = max(
                truncated.rfind(' '),
                truncated.rfind('\n'),
                truncated.rfind('\t')
            )
            if word_end > max_chars * 0.9:
                truncated = result[:word_end]

        return truncated + "...", {
            "truncated": True,
            "strategy": "smart_cutoff",
            "boundary_type": "sentence" if sentence_end > 0 else "word"
        }

    def _is_structured_content(self, content: str) -> bool:
        """Check if content appears to be structured (JSON, CSV, etc.)"""
        content = content.strip()
        return (
            content.startswith(('{', '[')) or
            ',' in content.split('\n')[0] or  # CSV-like
            ':' in content.split('\n')[0]     # Key-value
        )

    def _contains_errors(self, content: str) -> bool:
        """Check if content contains error indicators"""
        error_keywords = [
            'error', 'failed', 'exception', 'critical', 'warning',
            'cannot', 'unable', 'denied', 'invalid', 'not found',
            'failed', 'timeout', 'connection refused', 'permission'
        ]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in error_keywords)

    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get quality processing metrics"""
        metrics = self.quality_metrics.copy()

        if metrics["total_processed"] > 0:
            metrics["truncation_rate"] = metrics["truncated"] / metrics["total_processed"]
            metrics["full_retention_rate"] = metrics["full_retained"] / metrics["total_processed"]
            metrics["error_processing_rate"] = metrics["error_cases"] / metrics["total_processed"]
            if metrics["truncated"] > 0:
                metrics["adaptive_improvement_rate"] = metrics["adaptive_improvements"] / metrics["truncated"]

        return metrics

    def update_tool_policy(self, tool_name: str, policy: ToolPolicy):
        """Update policy for a specific tool"""
        self.tool_policies[tool_name] = policy
        logger.info(f"Updated policy for tool {tool_name}: max_chars={policy.max_chars}, strategy={policy.strategy.value}")

    def get_tool_policy(self, tool_name: str) -> ToolPolicy:
        """Get current policy for a tool"""
        return self.tool_policies.get(tool_name, ToolPolicy())

    async def summarize_with_ai(self, tool_name: str, full_result: str, max_chars: int) -> Optional[str]:
        """Use AI to create an intelligent summary of tool results"""
        if not self.summarizer_client or len(full_result) < 200:
            return None  # Don't use AI for short results

        try:
            # Create a focused summarization prompt
            summary_prompt = f"""
            Summarize this {tool_name} tool result in {max_chars} characters or less.
            Preserve the most important information, especially errors, counts, and key data.
            Be concise but informative.

            Result: {full_result[:1500]}  # Limit input size
            """

            # Use a lightweight model for summarization (could be a small Ollama model)
            if hasattr(self.summarizer_client, 'call_fast_model'):
                summary = await self.summarizer_client.call_fast_model(
                    [{"role": "user", "content": summary_prompt}],
                    max_tokens=100
                )
                summary_text = summary.get("content", "").strip()
                if summary_text and len(summary_text) <= max_chars:
                    self.quality_metrics["ai_summaries"] += 1
                    return summary_text

        except Exception as e:
            logger.debug(f"AI summarization failed: {e}")

        return None

    def reset_metrics(self):
        """Reset quality metrics"""
        self.quality_metrics = {k: 0 for k in self.quality_metrics.keys()}
        logger.info("Quality metrics reset")