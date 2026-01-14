"""
Comprehensive Startup Validation System

Validates all dependencies, resources, and configurations before system initialization.
Catches failures early and provides clear diagnostics.
"""
import os
import sys
import socket
import logging
import importlib
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import asyncio

logger = logging.getLogger("agent_runner.startup_validator")


class StartupValidator:
    """Validates system state before startup."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    async def validate_all(self) -> Tuple[List[str], List[str]]:
        """Run all validation checks."""
        logger.info("🔍 Starting comprehensive startup validation...")
        
        # Critical validations (must pass)
        self._validate_imports()
        self._validate_critical_methods()
        self._validate_dependencies()
        self._validate_ports()
        self._validate_file_system()
        self._validate_permissions()
        self._validate_config_files()
        self._validate_environment_variables()
        self._validate_resources()
        
        # Non-critical validations (warnings only)
        self._validate_optional_components()
        
        if self.errors:
            logger.error(f"❌ Validation failed with {len(self.errors)} critical errors")
            for error in self.errors:
                logger.error(f"  - {error}")
        if self.warnings:
            logger.warning(f"⚠️ Validation found {len(self.warnings)} warnings")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        
        return self.errors, self.warnings
    
    def _validate_imports(self):
        """Validate all critical imports."""
        logger.debug("Validating imports...")
        critical_imports = [
            ("common.logging_utils", "log_time"),
            ("agent_runner.state", "AgentState"),
            ("agent_runner.executor", "ToolExecutor"),
            ("agent_runner.memory_server", "MemoryServer"),
            ("router.routes.chat", "chat_completions"),
            ("fastapi", "FastAPI"),
            ("httpx", "AsyncClient"),
            ("yaml", "safe_load"),
            ("asyncio", None),
        ]
        
        for module_name, attr_name in critical_imports:
            try:
                module = importlib.import_module(module_name)
                if attr_name and not hasattr(module, attr_name):
                    self.errors.append(f"Missing attribute '{attr_name}' in module '{module_name}'")
            except ImportError as e:
                self.errors.append(f"Missing import '{module_name}': {e}")
            except Exception as e:
                self.errors.append(f"Import error for '{module_name}': {e}")
    
    def _validate_critical_methods(self):
        """Validate critical methods exist."""
        logger.debug("Validating critical methods...")
        try:
            from agent_runner.executor import ToolExecutor
            from agent_runner.state import AgentState
            
            # Create minimal state for validation
            state = AgentState()
            executor = ToolExecutor(state)
            
            required_methods = [
                ('ToolExecutor', '_disable_failed_server'),
                ('ToolExecutor', 'discover_mcp_tools'),
                ('ToolExecutor', 'execute_tool_call'),
                ('ToolExecutor', 'get_all_tools'),
                ('AgentState', 'initialize'),
                ('AgentState', 'toggle_mcp_server'),
            ]
            
            for class_name, method_name in required_methods:
                obj = executor if class_name == 'ToolExecutor' else state
                if not hasattr(obj, method_name):
                    self.errors.append(f"Missing method '{class_name}.{method_name}'")
                elif not callable(getattr(obj, method_name)):
                    self.errors.append(f"'{class_name}.{method_name}' is not callable")
        except Exception as e:
            self.errors.append(f"Failed to validate methods: {e}")
    
    def _validate_dependencies(self):
        """Validate required dependencies are available."""
        logger.debug("Validating dependencies...")
        required_packages = [
            "httpx",
            "yaml",
            "fastapi",
            "uvicorn",
            "asyncio",
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.errors.append(f"Missing required dependency: {package}")
    
    def _validate_ports(self):
        """Validate required ports are available."""
        logger.debug("Validating ports...")
        required_ports = [
            # Only check ports that THIS process (Agent Runner) needs to bind to.
            # Do NOT check external services (Router/DB) as they are likely running and valid.
            (5460, "Agent-runner"),
        ]
        
        for port, service in required_ports:
            if not self._is_port_available(port):
                self.errors.append(f"Port {port} ({service}) is in use. Please stop the existing process.")

    def _reclaim_port(self, port: int, service_name: str) -> bool:
        """
        Attempt to identify and kill the process holding a port.
        Returns True if port is successfully reclaimed (freed).
        """
        try:
            import subprocess
            import signal
            
            # Find PID using lsof
            # -t: terse (PID only), -i: internet files
            result = subprocess.run(
                ["lsof", "-t", f"-i:{port}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                # lsof failed or found nothing (maybe check failed due to race condition?)
                # Verify port again
                return self._is_port_available(port)
                
            pids = result.stdout.strip().split('\n')
            current_pid = os.getpid()
            
            killed_something = False
            for pid_str in pids:
                try:
                    pid = int(pid_str)
                    if pid == current_pid:
                        logger.warning(f"⚠️ Port {port} is held by CURRENT process ({pid}). Cannot kill self.")
                        continue
                        
                    logger.warning(f"🔨 Killing zombie process {pid} holding port {port} ({service_name})...")
                    os.kill(pid, signal.SIGKILL) # Aggressive Kill
                    killed_something = True
                except ValueError:
                    continue
                except ProcessLookupError:
                    continue # Already gone
                except PermissionError:
                    logger.error(f"❌ Permission denied killing PID {pid} on port {port}")
                    return False
            
            if not killed_something:
                return self._is_port_available(port)
            
            # Wait briefly for OS to release port
            import time
            for _ in range(10): # Wait up to 1 second
                if self._is_port_available(port):
                    return True
                time.sleep(0.1)
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to reclaim port {port}: {e}")
            return False

    def _reclaim_zombies(self):
        """
        [NUCLEAR] Kill all known Antigravity components that aren't THIS process.
        This ensures a clean slate on startup, removing 'zombies' that didn't die gracefully.
        """
        logger.info("☢️ Running Nuclear Zombie Sweep...")
        import os
        import signal
        import time
        
        # Patterns to search for in command lines
        zombie_patterns = [
            "router.main",
            "rag_server.py",
            "system_control_server",
            "mcp-server-",
            "@modelcontextprotocol",
            "ollama_server.py",
            "uvx mcp-server",
            "node .*mcp-server",
        ]
        
        current_pid = os.getpid()
        killed_count = 0
        
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.pid == current_pid:
                        continue
                        
                    cmdline = " ".join(proc.info['cmdline'] or [])
                    
                    # Check matches
                    matched = False
                    for pattern in zombie_patterns:
                        if pattern in cmdline:
                            matched = True
                            break
                    
                    if matched:
                        logger.warning(f"🧟 Found Zombie: [{proc.pid}] {cmdline[:50]}...")
                        proc.kill()
                        killed_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except ImportError:
            logger.warning("psutil not available for Zombie Sweep. Falling back to pgrep...")
            import subprocess
            for pattern in zombie_patterns:
                try:
                    # pgrep -f matches full command line
                    subprocess.run(["pkill", "-9", "-f", pattern], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            # Can't count easily with pkill, assume we tried.
            
        if killed_count > 0:
            logger.info(f"☢️ Nuclear Sweep: Killed {killed_count} zombie processes. Waiting for cleanup...")
            time.sleep(1.0) # Allow OS to reclaim resources
        else:
            logger.info("✅ No zombies found.")

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return True  # Assume available if check fails
    
    def _validate_file_system(self):
        """Validate file system accessibility."""
        logger.debug("Validating file system...")
        critical_paths = [
            (self.project_root / "config", "Config directory", True),
            (self.project_root / "config" / "config.yaml", "Config file", False),
            (self.project_root / "config" / "mcp.yaml", "MCP config", False),
            (self.project_root / ".env", "Environment file", False),
        ]
        
        for path, description, is_dir in critical_paths:
            if not path.exists():
                if is_dir:
                    self.warnings.append(f"{description} does not exist: {path}")
                else:
                    self.warnings.append(f"{description} does not exist: {path} (will use defaults)")
            else:
                # Check readability
                if not os.access(path, os.R_OK):
                    self.errors.append(f"Cannot read {description}: {path} (permission denied)")
    
    def _validate_permissions(self):
        """Validate file and directory permissions."""
        logger.debug("Validating permissions...")
        
        # Check log directory
        log_dir = Path.home() / "Library" / "Logs" / "ai"
        if log_dir.exists():
            if not os.access(log_dir, os.W_OK):
                self.errors.append(f"Log directory not writable: {log_dir}")
        else:
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.warnings.append(f"Cannot create log directory: {e}")
        
        # Check data directory
        data_dir = self.project_root / "data"
        if data_dir.exists() and not os.access(data_dir, os.W_OK):
            self.warnings.append(f"Data directory not writable: {data_dir}")
    
    def _validate_config_files(self):
        """Validate config file syntax."""
        logger.debug("Validating config files...")
        if yaml is None:
            self.warnings.append("yaml library not available - skipping YAML validation")
        if json is None:
            self.warnings.append("json library not available - skipping JSON validation")
        
        config_files = []
        if yaml:
            config_files.extend([
                (self.project_root / "config" / "config.yaml", yaml.safe_load, "YAML"),
                (self.project_root / "config" / "mcp.yaml", yaml.safe_load, "YAML"),
            ])
        if json:
            config_files.append((self.project_root / "system_config.json", json.load, "JSON"))
        
        for config_path, parser, file_type in config_files:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        parser(f)
                except Exception as e:
                    if file_type == "YAML":
                        self.errors.append(f"Invalid YAML in {config_path}: {e}")
                    elif file_type == "JSON":
                        self.errors.append(f"Invalid JSON in {config_path}: {e}")
                    else:
                        self.warnings.append(f"Error reading {config_path}: {e}")
    
    def _validate_environment_variables(self):
        """Validate environment variables."""
        logger.debug("Validating environment variables...")
        
        # Required vars (system won't work without these)
        required_vars = []
        
        # Optional vars (features disabled if missing)
        optional_vars = [
            # ("OPENWEATHER_API_KEY", "Weather MCP server"),
            # ("SURREAL_URL", "SurrealDB connection"),
            # ("SURREAL_USER", "SurrealDB authentication"),
            # ("SURREAL_PASS", "SurrealDB authentication"),
        ]
        
        for var_name, description in required_vars:
            if var_name not in os.environ:
                self.errors.append(f"Missing required environment variable: {var_name}")
        
        for var_name, description in optional_vars:
            if var_name not in os.environ:
                self.warnings.append(f"Missing optional environment variable: {var_name} ({description} will be unavailable)")
            else:
                # Validate format for some vars
                value = os.environ[var_name]
                if var_name == "SURREAL_URL" and not (value.startswith("ws://") or value.startswith("http://")):
                    self.warnings.append(f"Invalid SURREAL_URL format: {value}")
    
    def _validate_resources(self):
        """Validate system resources."""
        logger.debug("Validating system resources...")
        
        try:
            import resource
        except ImportError:
            resource = None
        
        try:
            import psutil
        except ImportError:
            psutil = None
        
        if resource:
            try:
                # Check file descriptor limit
                soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                if soft < 1024:
                    self.warnings.append(f"Low file descriptor limit: {soft} (recommended: 1024+)")
            except Exception as e:
                self.warnings.append(f"File descriptor check failed: {e}")
        
        if psutil:
            try:
                # Check available memory
                mem = psutil.virtual_memory()
                if mem.available < 500 * 1024 * 1024:  # 500MB
                    self.warnings.append(f"Low available memory: {mem.available / 1024 / 1024:.0f}MB")
                
                # Check process count
                process_count = len(psutil.pids())
                if process_count > 1000:
                    self.warnings.append(f"High process count: {process_count} (may indicate resource issues)")
            except Exception as e:
                self.warnings.append(f"Resource check failed: {e}")
        else:
            self.warnings.append("psutil not available - skipping resource checks")
    
    def _validate_optional_components(self):
        """Validate optional components (warnings only)."""
        logger.debug("Validating optional components...")
        
        # Check if optional services are available
        optional_services = [
            ("ollama", "Ollama local models"),
        ]
        
        for service, description in optional_services:
            # This would check if service is running
            # For now, just note it's optional
            pass


async def validate_startup_dependencies(project_root: Optional[Path] = None) -> Tuple[List[str], List[str]]:
    """Main entry point for startup validation."""
    if project_root is None:
        project_root = Path(__file__).parent.parent
    
    validator = StartupValidator(project_root)
    return await validator.validate_all()

