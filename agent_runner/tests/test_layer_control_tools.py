"""
Test Suite for Layer Control Tools

Tests error handling, validation, logging, and edge cases.
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from agent_runner.state import AgentState
from agent_runner.tools.system import (
    tool_set_quality_tier,
    tool_get_quality_tier,
    tool_control_refinement,
    tool_set_context_prune_limit,
    tool_filter_tools_by_category,
    tool_get_layer_status
)


class TestQualityTierTools:
    """Test quality tier control tools."""
    
    @pytest.mark.asyncio
    async def test_set_quality_tier_valid(self):
        """Test setting a valid quality tier."""
        state = Mock(spec=AgentState)
        state.set_quality_tier = Mock()
        
        result = await tool_set_quality_tier(state, "fast")
        
        assert result["ok"] is True
        assert result["tier"] == "fast"
        state.set_quality_tier.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_quality_tier_invalid(self):
        """Test setting an invalid quality tier."""
        state = Mock(spec=AgentState)
        
        result = await tool_set_quality_tier(state, "invalid_tier")
        
        assert result["ok"] is False
        assert "Invalid tier" in result["error"]
    
    @pytest.mark.asyncio
    async def test_set_quality_tier_none_state(self):
        """Test with None state."""
        result = await tool_set_quality_tier(None, "fast")
        
        assert result["ok"] is False
        assert "state not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_set_quality_tier_invalid_type(self):
        """Test with invalid tier type."""
        state = Mock(spec=AgentState)
        
        result = await tool_set_quality_tier(state, 123)
        
        assert result["ok"] is False
        assert "string" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_quality_tier_valid(self):
        """Test getting quality tier."""
        from agent_runner.quality_tiers import QualityTier
        
        state = Mock(spec=AgentState)
        state.quality_tier = QualityTier.BALANCED
        
        result = await tool_get_quality_tier(state)
        
        assert result["ok"] is True
        assert result["current_tier"] == "balanced"
    
    @pytest.mark.asyncio
    async def test_get_quality_tier_none_state(self):
        """Test with None state."""
        result = await tool_get_quality_tier(None)
        
        assert result["ok"] is False
        assert "state not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_quality_tier_missing_attribute(self):
        """Test when quality_tier attribute is missing."""
        state = Mock(spec=AgentState)
        del state.quality_tier  # Remove attribute
        
        result = await tool_get_quality_tier(state)
        
        # Should fallback to BALANCED
        assert result["ok"] is True
        assert result["current_tier"] == "balanced"


class TestRefinementControl:
    """Test refinement control tool."""
    
    @pytest.mark.asyncio
    async def test_control_refinement_enable(self):
        """Test enabling refinement."""
        state = Mock(spec=AgentState)
        state.skip_refinement_default = True
        
        result = await tool_control_refinement(state, enabled=True)
        
        assert result["ok"] is True
        assert state.skip_refinement_default is False
    
    @pytest.mark.asyncio
    async def test_control_refinement_set_limits(self):
        """Test setting memory and arch limits."""
        state = Mock(spec=AgentState)
        state.memory_retrieval_limit = 10
        state.architecture_context_limit = 50
        
        result = await tool_control_refinement(state, memory_limit=5, arch_limit=25)
        
        assert result["ok"] is True
        assert state.memory_retrieval_limit == 5
        assert state.architecture_context_limit == 25
    
    @pytest.mark.asyncio
    async def test_control_refinement_invalid_limit(self):
        """Test with invalid limit values."""
        state = Mock(spec=AgentState)
        
        result = await tool_control_refinement(state, memory_limit=-1)
        
        assert result["ok"] is False
        assert "must be >= 0" in result["error"]
    
    @pytest.mark.asyncio
    async def test_control_refinement_none_state(self):
        """Test with None state."""
        result = await tool_control_refinement(None, enabled=True)
        
        assert result["ok"] is False
        assert "state not available" in result["error"]


class TestContextPruning:
    """Test context pruning control."""
    
    @pytest.mark.asyncio
    async def test_set_context_prune_limit_valid(self):
        """Test setting valid prune limit."""
        state = Mock(spec=AgentState)
        
        result = await tool_set_context_prune_limit(state, limit=10)
        
        assert result["ok"] is True
        assert state.context_prune_limit == 10
    
    @pytest.mark.asyncio
    async def test_set_context_prune_limit_none(self):
        """Test disabling pruning."""
        state = Mock(spec=AgentState)
        
        result = await tool_set_context_prune_limit(state, limit=None)
        
        assert result["ok"] is True
        assert state.context_prune_limit is None
    
    @pytest.mark.asyncio
    async def test_set_context_prune_limit_invalid(self):
        """Test with invalid limit."""
        state = Mock(spec=AgentState)
        
        result = await tool_set_context_prune_limit(state, limit=-1)
        
        assert result["ok"] is False
        assert "must be >= 0" in result["error"]
    
    @pytest.mark.asyncio
    async def test_set_context_prune_limit_none_state(self):
        """Test with None state."""
        result = await tool_set_context_prune_limit(None, limit=10)
        
        assert result["ok"] is False
        assert "state not available" in result["error"]


class TestCategoryFiltering:
    """Test tool category filtering."""
    
    @pytest.mark.asyncio
    async def test_filter_tools_by_category_valid(self):
        """Test filtering with valid categories."""
        state = Mock(spec=AgentState)
        
        result = await tool_filter_tools_by_category(state, categories=["filesystem", "status"])
        
        assert result["ok"] is True
        assert state.tool_category_filter == ["filesystem", "status"]
    
    @pytest.mark.asyncio
    async def test_filter_tools_by_category_invalid(self):
        """Test with invalid categories."""
        state = Mock(spec=AgentState)
        
        result = await tool_filter_tools_by_category(state, categories=["invalid_category"])
        
        assert result["ok"] is False
        assert "Invalid categories" in result["error"]
    
    @pytest.mark.asyncio
    async def test_filter_tools_by_category_disable(self):
        """Test disabling category filtering."""
        state = Mock(spec=AgentState)
        state.tool_category_filter = ["filesystem"]
        
        result = await tool_filter_tools_by_category(state, categories=None, enabled=False)
        
        assert result["ok"] is True
        assert state.tool_category_filter is None
    
    @pytest.mark.asyncio
    async def test_filter_tools_by_category_none_state(self):
        """Test with None state."""
        result = await tool_filter_tools_by_category(None, categories=["filesystem"])
        
        assert result["ok"] is False
        assert "state not available" in result["error"]


class TestLayerStatus:
    """Test layer status tool."""
    
    @pytest.mark.asyncio
    async def test_get_layer_status_valid(self):
        """Test getting layer status."""
        from agent_runner.quality_tiers import QualityTier
        
        state = Mock(spec=AgentState)
        state.quality_tier = QualityTier.BALANCED
        state.skip_refinement_default = False
        state.memory_retrieval_limit = 10
        state.architecture_context_limit = 50
        state.context_prune_limit = 20
        state.tool_category_filter = None
        
        result = await tool_get_layer_status(state)
        
        assert result["ok"] is True
        assert "layers" in result
        assert result["quality_tier"] == "balanced"
    
    @pytest.mark.asyncio
    async def test_get_layer_status_none_state(self):
        """Test with None state."""
        result = await tool_get_layer_status(None)
        
        assert result["ok"] is False
        assert "state not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_layer_status_missing_attributes(self):
        """Test when attributes are missing (should use defaults)."""
        state = Mock(spec=AgentState)
        # Don't set any attributes
        
        result = await tool_get_layer_status(state)
        
        assert result["ok"] is True
        # Should use defaults via getattr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])







