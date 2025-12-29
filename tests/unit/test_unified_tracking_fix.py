import pytest
from unittest.mock import MagicMock
from common.unified_tracking import track_event, EventCategory, EventSeverity, get_unified_tracker

@pytest.mark.asyncio
async def test_track_event_flow():
    # Reset tracker
    from common import unified_tracking
    unified_tracking._tracker = None
    tracker = get_unified_tracker()
    tracker._ensure_initialized()
    
    # Mock subsystems
    tracker._notification_manager = MagicMock()
    tracker._system_blog = MagicMock()
    tracker._dashboard_tracker = MagicMock()
    
    # Track an event that should trigger all subsystems
    # Note: track_event is sync but it might call async stuff via tasks
    track_event(
        event="test_event",
        message="test message",
        severity=EventSeverity.HIGH,
        category=EventCategory.SYSTEM,
        notify=True,
        write_to_blog=True
    )
    
    # Since these are run in tasks or sync callbacks, we might need a tiny sleep 
    # if they were async, but here I mocked them to be checked immediately if sync.
    # The Notification system, Dashboard and Blog are now called DIRECTLY in track_event
    # (not in tasks, although the callbacks they trigger might be tasks).
    
    # Verify notification manager was called
    assert tracker._notification_manager.notify.called
    
    # Verify system blog was called
    assert tracker._system_blog.write_entry.called

def test_indentation_fix_verification():
    """
    Specifically verify that category=DASHBOARD triggers dashboard_tracker
    even if there's no error/request_id (which was the bug).
    """
    from common import unified_tracking
    unified_tracking._tracker = None
    tracker = get_unified_tracker()
    tracker._ensure_initialized()
    
    tracker._dashboard_tracker = MagicMock()
    
    track_event(
        event="dashboard_event",
        category=EventCategory.DASHBOARD,
        message="dashboard message",
        component="test_ui"
    )
    
    # This would have FAILED before the fix because it was inside _record_error_in_observability
    # which requires a request_id and is only called if certain conditions met.
    assert tracker._dashboard_tracker.record_error.called
