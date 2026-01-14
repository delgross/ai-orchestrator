import json
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger("agent_runner.formatter")

class ResponseFormatter:
    """
    Universal formatting engine for tool outputs.
    Converts raw Python structures (lists, dicts) into human-readable Markdown.
    Used by Nexus, Executor, and Maître d'.
    """

    @staticmethod
    def format_tool_output(data: Any) -> str:
        """
        Main entry point for formatting tool output.
        Intelligently determines the best Markdown representation.
        """
        try:
            # 1. Handle Pre-formatted Strings
            if isinstance(data, str):
                # [SMART PATTERN] Mermaid Diagram
                stripped = data.strip()
                if any(stripped.startswith(k) for k in ["graph ", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram", "gantt", "pie", "flowchart", "mindmap"]):
                     return f"```mermaid\n{data}\n```"

                # If it looks like JSON, try to parse it to format it better
                if stripped.startswith(("{", "[")):
                    try:
                        parsed = json.loads(data)
                        return ResponseFormatter.format_tool_output(parsed)
                    except json.JSONDecodeError:
                        pass
                return data

            # 2. Unwrap Common Wrappers ("result", "content", "data")
            if isinstance(data, dict):
                # If single key "result" or "content", unwrap it
                if len(data) == 1:
                    key = next(iter(data))
                    if key in ["result", "content", "data", "items"]:
                        return ResponseFormatter.format_tool_output(data[key])
                
                # Special Case: MCP Error wrapping
                if "error" in data:
                    return ResponseFormatter._format_error(data)

                # aggresive unwrapping for MCP tool results
                # unwraps 'result' even if 'ok' is present
                if "result" in data:
                    return ResponseFormatter.format_tool_output(data["result"])
                
                # unwraps 'content' (MCP legacy/sdk)
                if "content" in data:
                    return ResponseFormatter.format_tool_output(data["content"])

                # unwraps 'text' (TextContent)
                if "type" in data and data["type"] == "text" and "text" in data:
                     return ResponseFormatter.format_tool_output(data["text"])

            # 3. Handle Lists (Table or List)
            if isinstance(data, list):
                if not data:
                    return "_Empty List_"

                # [FIX] Special Handling for MCP Content Lists (TextContent, ImageContent)
                # Don't tabulate these! Unwrap them.
                if len(data) > 0 and isinstance(data[0], dict) and "type" in data[0] and ("text" in data[0] or "data" in data[0]):
                    return "\n\n".join([ResponseFormatter.format_tool_output(item) for item in data])
                
                # Check if List of Dicts (Table candidate)
                if all(isinstance(item, dict) for item in data):
                    return ResponseFormatter._format_table(data)
                
                # Simple List
                return "\n".join(f"- {ResponseFormatter.format_tool_output(item)}" for item in data)

            # 4. Handle Dictionaries (Smart Patterns & Key-Value)
            if isinstance(data, dict):
                # [SMART PATTERN] Image (Base64)
                # Structure: {mimeType: "image/...", data: "..."} or {blob: "..."}
                if "mimeType" in data and data["mimeType"].startswith("image/") and ("data" in data or "blob" in data):
                    b64 = data.get("data", data.get("blob"))
                    mime = data["mimeType"]
                    # If we have a URI, use it as alt text, otherwise "Embedded Image"
                    alt = data.get("uri", "Embedded Image").split("/")[-1]
                    return f"![{alt}](data:{mime};base64,{b64})"

                # [SMART PATTERN] Resource Card (Source-First)
                # Structure: {uri: "...", mimeType: "...", text/blob: "..."}
                if "uri" in data and "mimeType" in data:
                    uri = data["uri"]
                    mime = data["mimeType"]
                    name = uri.split("/")[-1]
                    
                    # Header: 📄 [filename.ext](uri)
                    card = f"### 📄 [{name}]({uri})\n_{mime}_"
                    
                    # Content Preview
                    if "text" in data and data["text"]:
                        preview = data["text"]
                        # If huge, maybe truncate? For now, we trust the agent/user relation.
                        # Wrap in code block for safety if it looks like code
                        if mime in ["application/json", "text/x-python", "text/javascript"] or len(preview) > 100:
                             card += f"\n\n```\n{preview}\n```"
                        else:
                             card += f"\n\n> {preview}"
                    
                    return card

                # [SMART PATTERN] Web Link / Search Result
                # Structure: {url: "...", title: "...", description/snippet: "..."}
                if "url" in data and ("title" in data or "name" in data):
                    url = data["url"]
                    title = data.get("title", data.get("name", "Link"))
                    desc = data.get("description", data.get("snippet", ""))
                    
                    link = f"### 🔗 [{title}]({url})"
                    if desc:
                        link += f"\n> {desc}"
                    return link
                    
                # [SMART PATTERN] System Clock / Time
                if "source" in data and data["source"] == "system_clock":
                    # Variant A: Timezone Conversion (Has 'target_time')
                    if "target_time" in data:
                        src_time = data.get("source_time", "").split(" ")[0] # Just time part usually? No, it's full string
                        tgt_time = data.get("target_time", "")
                        src_tz = data.get("source_timezone", "")
                        tgt_tz = data.get("target_timezone", "")
                        diff = data.get("time_difference_hours", 0)
                        
                        # Format: NYC ➡️ LON (+5h)
                        return (
                            f"### 🌍 Time Conversion\n"
                            f"**{src_tz}** ➡️ **{tgt_tz}**\n"
                            f"> {tgt_time}\n\n"
                            f"_{diff}h difference_"
                        )
                        
                    # Variant B: Standard Clock (Time + Date)
                    if "time" in data:
                        time_full = data["time"] # "2026-01-13 16:35:00 EST"
                        # Try to parse strict parts for cleaner UI
                        try:
                            # Split "YYYY-MM-DD HH:MM:SS ZONE"
                            parts = time_full.split(" ")
                            t_part = parts[1] if len(parts) > 1 else time_full
                            z_part = parts[2] if len(parts) > 2 else ""
                        except:
                            t_part = time_full
                            z_part = ""

                        date_str = data.get("date", "")
                        day = data.get("day_of_week", "")
                        tz = data.get("timezone", "")
                        
                        return (
                            f"### 🕒 {t_part} {z_part}\n"
                            f"**{day}, {date_str}**\n"
                            f"_{tz}_"
                        )

                return ResponseFormatter._format_dict(data)

            # 5. Handle Objects (CallToolResult, TextContent, etc.)
            if hasattr(data, "content") and data.content is not None:
                return ResponseFormatter.format_tool_output(data.content)
            
            if hasattr(data, "text") and data.text is not None:
                return ResponseFormatter.format_tool_output(data.text)

            # Fallback
            return str(data)

        except Exception as e:
            logger.error(f"Formatting failed: {e}")
            return f"**Formatting Error:** {str(data)}"

    @staticmethod
    def _format_table(data: List[Dict[str, Any]]) -> str:
        """Format a list of dictionaries as a Markdown table."""
        if not data:
            return ""

        # Collect all unique keys to form headers
        headers = set()
        for item in data:
            headers.update(item.keys())
        
        # Sort headers for consistency (put 'name', 'id' first if present)
        sorted_headers = sorted(headers)
        if "name" in sorted_headers:
            sorted_headers.insert(0, sorted_headers.pop(sorted_headers.index("name")))
        if "id" in sorted_headers and "id" != sorted_headers[0]:
            sorted_headers.insert(0, sorted_headers.pop(sorted_headers.index("id")))

        # Build Header Row
        md = "| " + " | ".join(sorted_headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(sorted_headers)) + " |\n"

        # Build Data Rows
        for item in data:
            row = []
            for h in sorted_headers:
                val = item.get(h, "")
                # Format value simply
                if isinstance(val, (dict, list)):
                    # Minify complex nested data, but maybe we should format it?
                    # For tables, minified JSON is usually best to keep rows compact
                    val = json.dumps(val) 
                row.append(str(val))
            md += "| " + " | ".join(row) + " |\n"

        return md

    @staticmethod
    def _format_dict(data: Dict[str, Any]) -> str:
        """Format a dictionary as a bulleted list."""
        lines = []
        for k, v in data.items():
            # Recursively format values to handle nested structures
            formatted_v = ResponseFormatter.format_tool_output(v)
            
            # Indent multi-line values
            if "\n" in formatted_v:
                formatted_v = "\n  " + formatted_v.replace("\n", "\n  ")
            
            lines.append(f"- **{k}:** {formatted_v}")
        return "\n".join(lines)

    @staticmethod
    def _format_error(data: Dict[str, Any]) -> str:
        """Format an error response consistently."""
        error = data.get("error", "Unknown Error")
        return f"### ❌ Error\n\n> {error}"
