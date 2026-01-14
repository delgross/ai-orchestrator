"""
System Clock Time Tools

Provides time functionality using the system clock (no internet dependency).
Replaces the mcp-server-time MCP server.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("agent_runner.tools.time")

# Try to use zoneinfo (Python 3.9+), fallback to pytz
try:
    from zoneinfo import ZoneInfo
    _tz_class = ZoneInfo
except ImportError:
    try:
        import pytz
        _tz_class = pytz.timezone
    except ImportError:
        _tz_class = None


async def tool_get_current_time(state, timezone: Optional[str] = "America/New_York", **kwargs) -> Dict[str, Any]:
    """
    Get current time in a specific timezone using the system clock.
    
    Args:
        state: AgentState instance
        timezone: IANA timezone name (e.g., 'America/New_York', 'Europe/London')
    
    Returns:
        Dict with time information
    """
    if _tz_class is None:
        return {
            "ok": False,
            "error": "No timezone library available. Install pytz or use Python 3.9+ with zoneinfo."
        }
    
    # Robust Defaulting for safety against 'null' arguments
    if not timezone:
        timezone = "America/New_York"
    
    try:
        if _tz_class == ZoneInfo:
            tz = ZoneInfo(timezone)
            now = datetime.now(tz)
        else:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
        
        return {
            "ok": True,
            "time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "date": now.strftime("%Y-%m-%d"),
            "timezone": timezone,
            "timestamp": now.timestamp(),
            "day_of_week": now.strftime("%A"),
            "day_of_year": now.timetuple().tm_yday,
            "week_number": now.isocalendar()[1],
            "source": "system_clock"
        }
    except (ValueError, KeyError) as e:
        # zoneinfo raises ValueError, pytz raises KeyError/UnknownTimeZoneError
        return {
            "ok": False,
            "error": f"Unknown timezone: {timezone}",
            "suggestion": "Use IANA timezone names (e.g., 'America/New_York', 'Europe/London')"
        }
    except Exception as e:
        logger.error(f"Failed to get current time: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e)
        }


async def tool_convert_time(state, source_timezone: str, time: str, target_timezone: str) -> Dict[str, Any]:
    """
    Convert time between timezones using the system clock.
    
    Args:
        state: AgentState instance
        source_timezone: Source IANA timezone name
        time: Time to convert in 24-hour format (HH:MM)
        target_timezone: Target IANA timezone name
    
    Returns:
        Dict with converted time information
    """
    if _tz_class is None:
        return {
            "ok": False,
            "error": "No timezone library available. Install pytz or use Python 3.9+ with zoneinfo."
        }
    
    try:
        if _tz_class == ZoneInfo:
            source_tz = ZoneInfo(source_timezone)
            target_tz = ZoneInfo(target_timezone)
        else:
            source_tz = pytz.timezone(source_timezone)
            target_tz = pytz.timezone(target_timezone)
        
        # Parse time (HH:MM format)
        hour, minute = map(int, time.split(":"))
        
        # Get current date in source timezone
        now_source = datetime.now(source_tz)
        
        # Create datetime with specified time
        if _tz_class == ZoneInfo:
            dt_source = datetime(
                now_source.year,
                now_source.month,
                now_source.day,
                hour,
                minute,
                tzinfo=source_tz
            )
        else:
            dt_source = source_tz.localize(datetime(
                now_source.year,
                now_source.month,
                now_source.day,
                hour,
                minute
            ))
        
        # Convert to target timezone
        dt_target = dt_source.astimezone(target_tz)
        
        return {
            "ok": True,
            "source_time": dt_source.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "target_time": dt_target.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "source_timezone": source_timezone,
            "target_timezone": target_timezone,
            "time_difference_hours": (dt_target.utcoffset() - dt_source.utcoffset()).total_seconds() / 3600,
            "source": "system_clock"
        }
    except (ValueError, KeyError) as e:
        error_str = str(e)
        # Check if it's a timezone error or time format error
        if "timezone" in error_str.lower() or "zone" in error_str.lower():
            return {
                "ok": False,
                "error": f"Unknown timezone: {error_str}",
                "suggestion": "Use IANA timezone names (e.g., 'America/New_York', 'Europe/London')"
            }
        else:
            return {
                "ok": False,
                "error": f"Invalid time format: {error_str}",
                "suggestion": "Use 24-hour format (HH:MM), e.g., '14:30'"
            }
    except Exception as e:
        logger.error(f"Failed to convert time: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e)
        }

