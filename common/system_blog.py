"""
System Blog - Machine and Human Readable Logging

Provides structured blog entries that are both:
- Human-readable: Markdown format for easy reading
- Machine-readable: YAML frontmatter for programmatic access

Designed for anomaly tracking, system events, and decision-making.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml # type: ignore[import-untyped]
except ImportError:
    yaml = None  # Optional dependency

logger = logging.getLogger("system_blog")


class BlogCategory(Enum):
    """Blog entry categories."""
    ANOMALY = "anomaly"
    SYSTEM_EVENT = "system_event"
    DECISION = "decision"
    RESOLUTION = "resolution"
    LEARNING = "learning"
    CONFIG_CHANGE = "config_change"


class BlogSeverity(Enum):
    """Severity levels for blog entries."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class BlogEntry:
    """A single blog entry with both human and machine readable content."""
    # Machine-readable metadata (YAML frontmatter)
    timestamp: float
    category: BlogCategory
    severity: BlogSeverity
    title: str
    source: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Human-readable content (Markdown body)
    content: str = ""
    
    # Machine-readable structured data
    structured_data: Dict[str, Any] = field(default_factory=dict)
    
    # Decision/action fields (for future automation)
    suggested_actions: List[str] = field(default_factory=list)
    resolution_status: str = "open"  # open, investigating, resolved, ignored
    resolution_notes: str = ""
    resolved_at: Optional[float] = None
    
    def to_markdown(self) -> str:
        """Convert blog entry to markdown format with YAML frontmatter."""
        # YAML frontmatter (machine-readable)
        frontmatter = {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "source": self.source,
            "tags": self.tags,
            "resolution_status": self.resolution_status,
            "suggested_actions": self.suggested_actions,
            "metadata": self.metadata,
            "structured_data": self.structured_data,
        }
        
        if self.resolved_at:
            frontmatter["resolved_at"] = self.resolved_at
            frontmatter["resolved_datetime"] = datetime.fromtimestamp(self.resolved_at).isoformat()
        
        if self.resolution_notes:
            frontmatter["resolution_notes"] = self.resolution_notes
        
        # Build markdown
        lines = ["---"]
        if yaml is None:
            raise ImportError("PyYAML is required for blog entries. Install with: pip install pyyaml")
        lines.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip())
        lines.append("---")
        lines.append("")
        lines.append(f"# {self.title}")
        lines.append("")
        
        # Add content
        if self.content:
            lines.append(self.content)
            lines.append("")
        
        # Add structured data section if present
        if self.structured_data:
            lines.append("## Structured Data")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(self.structured_data, indent=2))
            lines.append("```")
            lines.append("")
        
        # Add suggested actions if present
        if self.suggested_actions:
            lines.append("## Suggested Actions")
            lines.append("")
            for i, action in enumerate(self.suggested_actions, 1):
                lines.append(f"{i}. {action}")
            lines.append("")
        
        # Add resolution section if resolved
        if self.resolution_status != "open":
            lines.append("## Resolution")
            lines.append("")
            lines.append(f"**Status**: {self.resolution_status}")
            if self.resolution_notes:
                lines.append("")
                lines.append(self.resolution_notes)
            if self.resolved_at:
                lines.append("")
                lines.append(f"**Resolved at**: {datetime.fromtimestamp(self.resolved_at).isoformat()}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def from_markdown(cls, content: str) -> "BlogEntry":
        """Parse a markdown blog entry with YAML frontmatter."""
        # Split frontmatter and body
        if not content.startswith("---"):
            raise ValueError("Invalid blog entry format: missing YAML frontmatter")
        
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Invalid blog entry format: malformed YAML frontmatter")
        
        frontmatter_str = parts[1].strip()
        body = parts[2].strip()
        
        if yaml is None:
            raise ImportError("PyYAML is required for blog entries. Install with: pip install pyyaml")
        
        # Parse YAML frontmatter
        frontmatter = yaml.safe_load(frontmatter_str)
        
        # Extract title from body (first # heading)
        title = frontmatter.get("title", "Untitled")
        if body.startswith("#"):
            first_line = body.split("\n")[0]
            if first_line.startswith("# "):
                title = first_line[2:].strip()
        
        # Extract content (remove title and structured data sections)
        content_lines = []
        in_structured = False
        in_actions = False
        in_resolution = False
        
        for line in body.split("\n"):
            if line.startswith("## Structured Data"):
                in_structured = True
                continue
            elif line.startswith("## Suggested Actions"):
                in_actions = True
                continue
            elif line.startswith("## Resolution"):
                in_resolution = True
                continue
            elif line.startswith("##"):
                in_structured = False
                in_actions = False
                in_resolution = False
                continue
            elif in_structured or in_actions or in_resolution:
                continue
            elif line.startswith("# "):
                continue  # Skip title
            else:
                content_lines.append(line)
        
        content = "\n".join(content_lines).strip()
        
        # Build entry
        entry = cls(
            timestamp=frontmatter.get("timestamp", time.time()),
            category=BlogCategory(frontmatter.get("category", "system_event")),
            severity=BlogSeverity(frontmatter.get("severity", "info")),
            title=title,
            source=frontmatter.get("source", "system"),
            tags=frontmatter.get("tags", []),
            metadata=frontmatter.get("metadata", {}),
            content=content,
            structured_data=frontmatter.get("structured_data", {}),
            suggested_actions=frontmatter.get("suggested_actions", []),
            resolution_status=frontmatter.get("resolution_status", "open"),
            resolution_notes=frontmatter.get("resolution_notes", ""),
            resolved_at=frontmatter.get("resolved_at"),
        )
        
        return entry


class SystemBlog:
    """Manages system blog entries."""
    
    def __init__(self, blog_dir: Optional[Path] = None):
        """
        Initialize system blog.
        
        Args:
            blog_dir: Directory to store blog entries (default: blogs/ in project root)
        """
        if blog_dir is None:
            blog_dir = Path(__file__).parent.parent / "blogs"
        
        self.blog_dir = Path(blog_dir)
        self.blog_dir.mkdir(parents=True, exist_ok=True)
        
        # Category subdirectories
        for category in BlogCategory:
            (self.blog_dir / category.value).mkdir(exist_ok=True)
    
    def write_entry(self, entry: BlogEntry) -> Path:
        """
        Write a blog entry to disk.
        
        Returns:
            Path to the written file
        """
        # Generate filename: YYYY-MM-DD_HH-MM-SS_category-title-slug.md
        dt = datetime.fromtimestamp(entry.timestamp)
        title_slug = entry.title.lower().replace(" ", "-").replace(":", "").replace("/", "-")[:50]
        filename = f"{dt.strftime('%Y-%m-%d_%H-%M-%S')}_{entry.category.value}_{title_slug}.md"
        
        # Write to category subdirectory
        file_path = self.blog_dir / entry.category.value / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(entry.to_markdown())
        
        logger.info(f"Blog entry written: {file_path}")
        return file_path
    
    def read_entry(self, file_path: Path) -> BlogEntry:
        """Read a blog entry from disk."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return BlogEntry.from_markdown(content)
    
    def list_entries(
        self,
        category: Optional[BlogCategory] = None,
        severity: Optional[BlogSeverity] = None,
        resolution_status: Optional[str] = None,
        limit: int = 100,
    ) -> List[BlogEntry]:
        """
        List blog entries with filters.
        
        Returns:
            List of blog entries (newest first)
        """
        entries = []
        
        # Search in category directory or all categories
        if category:
            search_dirs = [self.blog_dir / category.value]
        else:
            search_dirs = [self.blog_dir / cat.value for cat in BlogCategory]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            for file_path in search_dir.glob("*.md"):
                try:
                    entry = self.read_entry(file_path)
                    
                    # Apply filters
                    if severity and entry.severity != severity:
                        continue
                    if resolution_status and entry.resolution_status != resolution_status:
                        continue
                    
                    entries.append(entry)
                except Exception as e:
                    logger.warning(f"Failed to read blog entry {file_path}: {e}")
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        return entries[:limit]
    
    def get_entry_by_timestamp(self, timestamp: float, category: Optional[BlogCategory] = None) -> Optional[BlogEntry]:
        """Get blog entry closest to a timestamp."""
        entries = self.list_entries(category=category, limit=1000)
        
        # Find closest entry
        closest = None
        min_diff = float('inf')
        
        for entry in entries:
            diff = abs(entry.timestamp - timestamp)
            if diff < min_diff:
                min_diff = diff
                closest = entry
        
        return closest
    
    def update_entry_resolution(
        self,
        entry: BlogEntry,
        status: str,
        notes: str = "",
    ) -> Path:
        """Update resolution status of an entry."""
        entry.resolution_status = status
        entry.resolution_notes = notes
        if status in ("resolved", "ignored"):
            entry.resolved_at = time.time()
        
        # Find and update the file
        dt = datetime.fromtimestamp(entry.timestamp)
        category_dir = self.blog_dir / entry.category.value
        
        # Find matching file
        for file_path in category_dir.glob("*.md"):
            try:
                existing = self.read_entry(file_path)
                if abs(existing.timestamp - entry.timestamp) < 1.0:  # Same timestamp
                    return self.write_entry(entry)
            except Exception:
                continue
        
        # If not found, write new entry
        return self.write_entry(entry)


# Global blog instance
_blog: Optional[SystemBlog] = None


def get_blog() -> SystemBlog:
    """Get or create global system blog instance."""
    global _blog
    if _blog is None:
        _blog = SystemBlog()
    return _blog

