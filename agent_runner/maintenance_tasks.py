"""
Maintenance tasks for system health and validation.
"""

import asyncio
import logging
from typing import Dict, Any, List
from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer
from agent_runner.db_utils import run_query

logger = logging.getLogger("agent_runner.maintenance")

async def validate_registry_integrity(state: AgentState) -> Dict[str, Any]:
    """
    Validate all registry components for integrity and consistency.
    
    Checks:
    1. Permanent memory files in database
    2. Advice registry structure
    3. Database sync status
    4. File corruption detection
    
    Returns:
        Dict with validation status and issues found
    """
    issues: List[str] = []
    warnings: List[str] = []
    
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not available", "issues": [], "warnings": []}
        
        await state.memory.ensure_connected()
        
        # 1. Check permanent memory files in database
        logger.info("Validating permanent memory files...")
        sovereign_files = await state.memory.list_sovereign_files()
        
        if not sovereign_files:
            warnings.append("No permanent memory files found in database")
        else:
            logger.info(f"Found {len(sovereign_files)} permanent memory files")
            
            # Validate each file can be retrieved
            for file_info in sovereign_files:
                kb_id = file_info.get("kb_id")
                if not kb_id:
                    issues.append(f"Invalid file entry: missing kb_id")
                    continue
                
                # Try to retrieve content
                content = await state.memory.get_sovereign_file_content(kb_id)
                if content is None:
                    issues.append(f"File '{kb_id}' exists in index but content cannot be retrieved")
                elif not content.strip():
                    warnings.append(f"File '{kb_id}' is empty")
                else:
                    # Basic validation: check for reasonable content length
                    if len(content) < 10:
                        warnings.append(f"File '{kb_id}' has very short content ({len(content)} chars)")
        
        # 2. Check advice registry
        logger.info("Validating advice registry...")
        try:
            advice_count = await run_query(state, "SELECT count() FROM advice GROUP ALL")
            if advice_count and len(advice_count) > 0:
                count = advice_count[0].get("count", 0)
                if count == 0:
                    warnings.append("Advice registry is empty")
                else:
                    logger.info(f"Found {count} advice entries")
                    
                    # Check for orphaned advice (no topic)
                    orphaned = await run_query(state, "SELECT count() FROM advice WHERE topic IS NONE OR topic = '' GROUP ALL")
                    if orphaned and orphaned[0].get("count", 0) > 0:
                        issues.append(f"Found {orphaned[0].get('count')} advice entries without topic")
        except Exception as e:
            issues.append(f"Failed to validate advice registry: {e}")
        
        # 3. Check database connectivity
        logger.info("Validating database connectivity...")
        try:
            # Use a simple query that works with SurrealDB syntax
            test_query = await run_query(state, "SELECT count() FROM fact GROUP ALL")
            if not test_query:
                issues.append("Database connectivity test failed")
        except Exception as e:
            issues.append(f"Database connectivity error: {e}")
        
        # 4. Check for duplicate kb_ids (shouldn't happen but validate)
        logger.info("Checking for duplicate entries...")
        try:
            # Check for duplicate SovereignFile entries
            duplicates = await run_query(state, """
                SELECT target as kb_id, count() as cnt
                FROM fact 
                WHERE entity = 'SovereignFile' AND relation = 'has_content'
                GROUP BY target
            """)
            if duplicates and len(duplicates) > 0:
                for dup in duplicates:
                    try:
                        if dup.get("cnt", 0) > 1:
                            issues.append(f"Duplicate SovereignFile entry for kb_id: {dup.get('kb_id')}")
                    except Exception:
                        continue
        except Exception as e:
            warnings.append(f"Could not check for duplicates: {e}")
        
        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "files_checked": len(sovereign_files) if sovereign_files else 0
        }
        
    except Exception as e:
        logger.error(f"Registry validation error: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e),
            "issues": issues,
            "warnings": warnings
        }
