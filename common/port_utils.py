"""
Port utility functions for checking port availability.
"""
import socket
from typing import Optional


def port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """
    Check if a port is in use.
    
    Args:
        port: Port number to check
        host: Host address (default: 127.0.0.1)
    
    Returns:
        True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def get_port_pid(port: int, host: str = "127.0.0.1") -> Optional[int]:
    """
    Get the PID of the process using a port.
    
    Args:
        port: Port number to check
        host: Host address (default: 127.0.0.1)
    
    Returns:
        PID if found, None otherwise
    """
    import subprocess
    try:
        result = subprocess.run(
            ["lsof", "-t", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
            capture_output=True,
            text=True,
            timeout=1.0
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split('\n')[0])
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        pass
    return None








