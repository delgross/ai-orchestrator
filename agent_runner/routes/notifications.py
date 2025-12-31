import logging
from fastapi import APIRouter

from common.notifications import get_notification_manager, NotificationLevel

router = APIRouter()
logger = logging.getLogger("agent_runner.notifications")

@router.get("/admin/notifications")
async def get_notifications(priority: str = None, unread: bool = False, limit: int = 50):
    nm = get_notification_manager()
    
    level_filter = None
    if priority:
        try:
            level_filter = NotificationLevel(priority.lower())
        except: pass
        
    notifs = nm.get_notifications(
        level=level_filter,
        unacknowledged_only=unread,
        limit=limit
    )
    
    # Convert to JSON-able dicts
    return {"ok": True, "notifications": [
        {
            "level": n.level.value,
            "title": n.title,
            "message": n.message,
            "category": n.category,
            "timestamp": n.timestamp,
            "acknowledged": n.acknowledged,
            "id": i 
        } 
        for i, n in enumerate(nm.notifications)
        if n in notifs
    ]}

@router.post("/admin/notifications/acknowledge")
async def acknowledge_all_notifications():
    nm = get_notification_manager()
    # Acknowledge all currently unread
    for n in nm.notifications:
        n.acknowledged = True
    return {"ok": True, "message": "All notifications acknowledged"}
