"""
Data Processing and Analysis Tools

Provides utilities for parsing, validating, transforming, and analyzing structured data.
"""

import json
import csv
import io
import logging
from typing import Dict, Any, List, Optional, Union
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.data_processing")

async def tool_parse_json(state: AgentState, json_string: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Parse and optionally validate JSON data.

    Args:
        json_string: The JSON string to parse
        schema: Optional JSON schema for validation

    Returns:
        Dict containing parsed data and validation results
    """
    try:
        # Parse JSON
        parsed_data = json.loads(json_string)

        result = {
            "ok": True,
            "data": parsed_data,
            "data_type": type(parsed_data).__name__,
            "validation_passed": True
        }

        # Basic validation if schema provided
        if schema:
            validation_errors = []

            # Simple schema validation (could be enhanced with jsonschema library)
            if "type" in schema:
                expected_type = schema["type"]
                if expected_type == "object" and not isinstance(parsed_data, dict):
                    validation_errors.append(f"Expected object, got {type(parsed_data).__name__}")
                elif expected_type == "array" and not isinstance(parsed_data, list):
                    validation_errors.append(f"Expected array, got {type(parsed_data).__name__}")

            if "required" in schema and isinstance(parsed_data, dict):
                required_fields = schema["required"]
                for field in required_fields:
                    if field not in parsed_data:
                        validation_errors.append(f"Missing required field: {field}")

            if validation_errors:
                result["validation_passed"] = False
                result["validation_errors"] = validation_errors

        return result

    except json.JSONDecodeError as e:
        return {
            "ok": False,
            "error": f"JSON parsing failed: {str(e)}",
            "error_type": "json_decode_error"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected_error"
        }

async def tool_parse_csv(state: AgentState, csv_content: str, delimiter: str = ",", has_header: bool = True) -> Dict[str, Any]:
    """Parse CSV data into structured format.

    Args:
        csv_content: The CSV content as a string
        delimiter: CSV delimiter (default: ",")
        has_header: Whether the CSV has a header row

    Returns:
        Dict containing parsed data and metadata
    """
    try:
        # Parse CSV
        csv_reader = csv.reader(io.StringIO(csv_content), delimiter=delimiter)

        rows = list(csv_reader)
        if not rows:
            return {
                "ok": True,
                "data": [],
                "row_count": 0,
                "column_count": 0,
                "headers": []
            }

        headers = []
        data = []

        if has_header and len(rows) > 0:
            headers = rows[0]
            data_rows = rows[1:]
        else:
            # Generate column names if no header
            headers = [f"col_{i+1}" for i in range(len(rows[0]))]
            data_rows = rows

        # Convert to list of dictionaries
        for row in data_rows:
            if len(row) == len(headers):
                row_dict = dict(zip(headers, row))
                data.append(row_dict)

        return {
            "ok": True,
            "data": data,
            "row_count": len(data),
            "column_count": len(headers),
            "headers": headers,
            "has_header": has_header
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"CSV parsing failed: {str(e)}",
            "error_type": "csv_parse_error"
        }

async def tool_transform_data(state: AgentState, data: Union[List[Dict], Dict], transformations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Transform data according to specified rules.

    Args:
        data: The data to transform (list of dicts or single dict)
        transformations: List of transformation rules

    Returns:
        Dict containing transformed data
    """
    try:
        # Ensure we're working with a list
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            return {
                "ok": False,
                "error": "Data must be a list of dictionaries or a single dictionary",
                "error_type": "invalid_data_format"
            }

        transformed_data = []

        for item in data:
            if not isinstance(item, dict):
                continue

            transformed_item = dict(item)  # Copy original

            for transform in transformations:
                operation = transform.get("operation")
                field = transform.get("field")
                value = transform.get("value")

                if operation == "rename":
                    new_name = transform.get("new_name")
                    if field in transformed_item:
                        transformed_item[new_name] = transformed_item.pop(field)

                elif operation == "set":
                    transformed_item[field] = value

                elif operation == "delete":
                    if field in transformed_item:
                        del transformed_item[field]

                elif operation == "uppercase":
                    if field in transformed_item and isinstance(transformed_item[field], str):
                        transformed_item[field] = transformed_item[field].upper()

                elif operation == "lowercase":
                    if field in transformed_item and isinstance(transformed_item[field], str):
                        transformed_item[field] = transformed_item[field].lower()

                elif operation == "split":
                    separator = transform.get("separator", ",")
                    if field in transformed_item and isinstance(transformed_item[field], str):
                        transformed_item[field] = transformed_item[field].split(separator)

            transformed_data.append(transformed_item)

        return {
            "ok": True,
            "data": transformed_data,
            "original_count": len(data),
            "transformed_count": len(transformed_data),
            "transformations_applied": len(transformations)
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Data transformation failed: {str(e)}",
            "error_type": "transformation_error"
        }

async def tool_generate_report(state: AgentState, data: List[Dict[str, Any]], format: str = "markdown", title: str = "Data Report") -> Dict[str, Any]:
    """Generate a formatted report from data.

    Args:
        data: List of dictionaries to report on
        format: Output format ("markdown", "text", "json")
        title: Report title

    Returns:
        Dict containing the formatted report
    """
    try:
        if not data:
            return {
                "ok": True,
                "report": f"# {title}\n\nNo data available.",
                "format": format,
                "data_points": 0
            }

        # Analyze data structure
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
        else:
            headers = ["value"]

        # Generate report based on format
        if format == "markdown":
            report = f"# {title}\n\n"
            report += f"**Data Points:** {len(data)}\n\n"

            if headers:
                report += "## Summary\n\n"
                # Add basic statistics
                numeric_fields = []
                for header in headers:
                    sample_values = [row.get(header) for row in data[:10] if isinstance(row, dict)]
                    if sample_values and all(isinstance(v, (int, float)) for v in sample_values if v is not None):
                        numeric_fields.append(header)

                if numeric_fields:
                    report += "### Numeric Fields\n\n"
                    for field in numeric_fields:
                        values = [row.get(field) for row in data if isinstance(row, dict) and row.get(field) is not None]
                        if values:
                            report += f"- **{field}**: min={min(values)}, max={max(values)}, avg={sum(values)/len(values):.2f}\n"
                    report += "\n"

                # Sample data table
                report += "## Sample Data\n\n"
                report += "| " + " | ".join(headers) + " |\n"
                report += "|" + "|".join(["---"] * len(headers)) + "|\n"

                for row in data[:5]:  # First 5 rows
                    if isinstance(row, dict):
                        cells = [str(row.get(h, ""))[:30] for h in headers]  # Truncate long values
                        report += "| " + " | ".join(cells) + " |\n"

        elif format == "json":
            report = json.dumps({
                "title": title,
                "data_points": len(data),
                "headers": headers,
                "sample_data": data[:5]
            }, indent=2)

        else:  # text format
            report = f"{title}\n{'='*len(title)}\n\n"
            report += f"Data Points: {len(data)}\n"
            report += f"Fields: {', '.join(headers)}\n\n"

            if data:
                report += "Sample Data:\n"
                for i, row in enumerate(data[:3]):
                    report += f"{i+1}. {row}\n"

        return {
            "ok": True,
            "report": report,
            "format": format,
            "data_points": len(data),
            "fields": headers
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Report generation failed: {str(e)}",
            "error_type": "report_generation_error"
        }