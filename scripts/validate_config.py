#!/usr/bin/env python3
"""
Configuration validation system for AI orchestrator.
Validates MCP server API keys and other critical configurations at startup.
"""

import os
import sys
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

logger = logging.getLogger("config_validator")

class ConfigValidator:
    """Validates critical configuration settings."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = Path(__file__).parent.parent

    def validate_mcp_api_keys(self) -> bool:
        """Validate MCP server API keys from providers.env."""
        providers_env = self.project_root / "providers.env"

        if not providers_env.exists():
            self.errors.append("providers.env file not found")
            return False

        # Load environment variables from providers.env
        env_vars = {}
        try:
            with open(providers_env, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            self.errors.append(f"Failed to read providers.env: {e}")
            return False

        # Core required API keys (essential for basic functionality)
        required_keys = {}

        # Optional MCP API keys (services work without them)
        optional_keys = {
            'OPENWEATHER_API_KEY': 'Weather MCP server',
            'BRAVE_API_KEY': 'Brave Search MCP server',
            'TAVILY_API_KEY': 'Tavily Search MCP server',
            'XAI_API_KEY': 'xAI API (optional)',
            'OPENAI_API_KEY': 'OpenAI API (optional)',
            'OPENROUTER_API_KEY': 'OpenRouter API (optional)',
            'PERPLEXITY_API_KEY': 'Perplexity API (optional)'
        }

        missing_required = []
        missing_optional = []

        for key, description in required_keys.items():
            value = os.getenv(key) or env_vars.get(key)
            if not value or value.startswith('your_') or value == '':
                missing_required.append(f"{key} ({description})")

        for key, description in optional_keys.items():
            value = os.getenv(key) or env_vars.get(key)
            if not value or value.startswith('your_') or value == '':
                missing_optional.append(f"{key} ({description})")

        if missing_required:
            self.errors.append(f"Missing required API keys: {', '.join(missing_required)}")
            self.errors.append("Set these in providers.env or environment variables")

        if missing_optional:
            self.warnings.append(f"Missing optional API keys: {', '.join(missing_optional)}")
            self.warnings.append("Some MCP servers may not function without these keys")

        return len(missing_required) == 0

    def validate_service_connectivity(self) -> bool:
        """Validate connectivity to required services."""
        import asyncio
        import httpx

        async def check_service(name: str, url: str, timeout: float = 5.0) -> Tuple[bool, str]:
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
                    response = await client.get(url)
                    if response.status_code < 400:
                        return True, "OK"
                    else:
                        return False, f"HTTP {response.status_code}"
            except Exception as e:
                return False, str(e)

        async def run_checks():
            services = [
                ("Router", "http://127.0.0.1:5455/health"),
                ("Agent Runner", "http://127.0.0.1:5460/health"),
                ("SurrealDB", "http://127.0.0.1:8000/health"),
                ("Ollama", "http://127.0.0.1:11434/api/tags")
            ]

            for name, url in services:
                success, status = await check_service(name, url)
                if not success:
                    if name in ["Router", "Agent Runner", "Ollama"]:  # Critical services
                        self.errors.append(f"{name} service unavailable: {status}")
                    else:  # Optional services
                        self.warnings.append(f"{name} service unavailable: {status}")

        # Run async checks
        try:
            asyncio.run(run_checks())
        except Exception as e:
            self.errors.append(f"Service connectivity check failed: {e}")

        return len([e for e in self.errors if "service unavailable" in e]) == 0

    def validate_sovereign_config(self) -> bool:
        """Validate sovereign configuration file."""
        sovereign_yaml = self.project_root / "config" / "sovereign.yaml"

        if not sovereign_yaml.exists():
            self.errors.append("sovereign.yaml configuration file not found")
            return False

        try:
            import yaml
            with open(sovereign_yaml, 'r') as f:
                config = yaml.safe_load(f)

            if not config:
                self.errors.append("sovereign.yaml is empty or invalid")
                return False

            # Check for required sections
            required_sections = ['models', 'network', 'policies']
            for section in required_sections:
                if section not in config:
                    self.warnings.append(f"Missing section in sovereign.yaml: {section}")

            # Validate models section
            models = config.get('models', {})
            if not models:
                self.warnings.append("No models defined in sovereign.yaml")
            else:
                # Check for common model roles (using short form keys as defined in YAML)
                # The system maps short keys (agent) to long keys (agent_model) internally
                expected_short_roles = ['agent', 'router']  # Core models defined in sovereign.yaml
                for role in expected_short_roles:
                    if role not in models:
                        self.warnings.append(f"Missing model role in sovereign.yaml: {role}")
                        # Note: task_model is not defined in sovereign.yaml but has hardcoded defaults

        except Exception as e:
            self.errors.append(f"Failed to validate sovereign.yaml: {e}")
            return False

        return True

    def validate_python_dependencies(self) -> bool:
        """Validate critical Python dependencies."""
        critical_deps = [
            ('mirascope', 'Mirascope LLM orchestration'),
            ('httpx', 'HTTP client library'),
            ('fastapi', 'Web framework'),
            ('pydantic', 'Data validation')
        ]

        missing_deps = []
        for dep, description in critical_deps:
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(f"{dep} ({description})")

        if missing_deps:
            self.errors.append(f"Missing critical dependencies: {', '.join(missing_deps)}")
            self.errors.append("Install with: pip install -r requirements.txt")

        return len(missing_deps) == 0

    def run_all_validations(self) -> bool:
        """Run all configuration validations."""
        print("🔍 Running configuration validation checks...")

        validations = [
            ("MCP API Keys", self.validate_mcp_api_keys),
            ("Service Connectivity", self.validate_service_connectivity),
            ("Sovereign Config", self.validate_sovereign_config),
            ("Python Dependencies", self.validate_python_dependencies)
        ]

        all_passed = True

        for name, validator in validations:
            print(f"  Checking {name}...", end=" ")
            try:
                passed = validator()
                status = "✅" if passed else "❌"
                print(f"{status}")
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ (Error: {e})")
                self.errors.append(f"{name} validation failed: {e}")
                all_passed = False

        return all_passed

    def report_results(self):
        """Report validation results."""
        if not self.errors and not self.warnings:
            print("\n🎉 All configuration checks passed!")
            return True

        if self.errors:
            print(f"\n❌ CRITICAL ISSUES ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.errors:
            print("\n🚨 System may not function correctly. Please fix critical issues above.")
            return False
        else:
            print("\n✅ System is ready, but consider addressing warnings for optimal performance.")
            return True

def main():
    """Main validation entry point."""
    validator = ConfigValidator()
    success = validator.run_all_validations()
    return validator.report_results()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
