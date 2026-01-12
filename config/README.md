# Configuration System

This directory contains the shared configuration system for the AI Orchestrator, designed to support both current multi-file configuration and future unified configuration.

## Current State

Currently, configuration is loaded from:
1. **Environment variables** (highest priority)
2. **Service-specific .env files**:
   - `router.env` - Router configuration
   - `agent_runner/agent_runner.env` - Agent-runner configuration
3. **Future: Unified config.yaml** (not yet implemented, lowest priority)

## Usage

### Basic Usage

```python
from config import load_config, get_config_value

# Load all configuration
config = load_config(service="all")

# Load router-specific config
router_config = load_config(service="router")

# Get a single value
model = get_config_value("AGENT_MODEL", default="openai:gpt-4o")
```

### In Router

```python
from config import get_config_value

OLLAMA_BASE = get_config_value("OLLAMA_BASE", "http://127.0.0.1:11434")
AGENT_RUNNER_URL = get_config_value("AGENT_RUNNER_URL", "http://127.0.0.1:5460")
```

### In Agent-Runner

```python
from config import get_config_value

AGENT_MODEL = get_config_value("AGENT_MODEL", "openai:gpt-4.1-mini")
GATEWAY_BASE = get_config_value("GATEWAY_BASE", "http://127.0.0.1:5455")
```

## Migration Path

### Phase 1: Current (Multi-file)
- ✅ Services use their own .env files
- ✅ Environment variables override .env files
- ✅ Shared config loader available but optional

### Phase 2: Transition (Hybrid)
- Services can use shared config loader
- Unified config.yaml supported but optional
- .env files still work for backward compatibility

### Phase 3: Unified (Future)
- Single `config.yaml` file
- .env files deprecated but still supported
- All services use shared config loader

## Configuration Schema

See `schema.py` for the complete configuration schema with types and defaults.

## Benefits

1. **Backward Compatible**: Current .env files continue to work
2. **Gradual Migration**: Can adopt shared loader incrementally
3. **Future Ready**: Prepared for unified config.yaml
4. **Type Safety**: Schema defines all options and types
5. **Priority System**: Clear precedence (env > .env > unified)




















