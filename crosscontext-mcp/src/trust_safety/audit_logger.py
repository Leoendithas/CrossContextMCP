"""
Audit Logging System for CrossContext MCP
Logs all tool invocations with sanitized inputs and data access tracking
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Use the directory where the server script is located for audit logs
import os
from pathlib import Path

# Get the directory where this module is located
module_dir = Path(__file__).parent.parent  # Go up two levels to src/
AUDIT_LOG_FILE = module_dir / "audit_log.jsonl"

def log_tool_invocation(tool_name: str, input_data: Dict[str, Any], output_data: Any, user_id: str = "officer_001") -> str:
    """
    Log a tool invocation for audit compliance.

    Args:
        tool_name: Name of the tool being invoked
        input_data: Input parameters (will be sanitized)
        output_data: Tool output data
        user_id: Identifier for the user making the request

    Returns:
        Audit log ID for tracking
    """
    # Generate unique audit ID
    audit_id = str(uuid.uuid4())

    # Sanitize input data (remove any sensitive information from logs)
    sanitized_input = sanitize_input(input_data)

    # Extract data access information
    data_accessed = extract_data_access_info(output_data)

    # Singapore timezone (GMT+8)
    singapore_tz = timezone(timedelta(hours=8))
    current_time_sg = datetime.now(singapore_tz)

    # Create audit log entry
    audit_entry = {
        "audit_id": audit_id,
        "timestamp": current_time_sg.isoformat(),
        "timezone": "Asia/Singapore",
        "user_id": user_id,
        "tool_name": tool_name,
        "input_sanitized": sanitized_input,
        "data_accessed": data_accessed,
        "success": True,  # Could be enhanced to track failures
        "session_id": f"session_{current_time_sg.strftime('%Y%m%d')}"
    }

    # Write to audit log file
    log_file_path = Path(AUDIT_LOG_FILE)
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')

    return audit_id

def sanitize_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data for audit logging by removing sensitive information.

    Args:
        input_data: Raw input data

    Returns:
        Sanitized input data safe for logging
    """
    sanitized = input_data.copy()

    # Remove or mask sensitive fields
    sensitive_fields = ['password', 'token', 'secret', 'key', 'nric', 'phone']
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '[REDACTED]'

    return sanitized

def extract_data_access_info(output_data: Any) -> list:
    """
    Extract information about what data was accessed from tool output.

    Args:
        output_data: Tool output data

    Returns:
        List of data access records
    """
    data_accessed = []

    try:
        # Handle different output formats
        if isinstance(output_data, dict):
            # Extract from email results
            if "emails" in output_data:
                for email in output_data["emails"]:
                    data_accessed.append({
                        "resource_type": "email",
                        "resource_id": email.get("id", "unknown"),
                        "classification": email.get("classification", "unknown"),
                        "redacted": email.get("redacted", False)
                    })

            # Extract from calendar results
            elif "events" in output_data:
                for event in output_data["events"]:
                    data_accessed.append({
                        "resource_type": "calendar_event",
                        "resource_id": event.get("id", "unknown"),
                        "classification": event.get("classification", "unknown"),
                        "redacted": event.get("redacted", False)
                    })

            # Extract from stakeholder results
            elif "stakeholder" in output_data and output_data["stakeholder"]:
                stakeholder = output_data["stakeholder"]
                data_accessed.append({
                    "resource_type": "stakeholder",
                    "resource_id": stakeholder.get("id", "unknown"),
                    "classification": stakeholder.get("classification", "unknown"),
                    "redacted": stakeholder.get("redacted", False)
                })

            # Extract from document results
            elif "documents" in output_data:
                for doc in output_data["documents"]:
                    data_accessed.append({
                        "resource_type": "document",
                        "resource_id": doc.get("id", "unknown"),
                        "classification": doc.get("classification", "unknown"),
                        "redacted": doc.get("redacted", False)
                    })

            # Extract from policy results
            elif "policies" in output_data:
                for policy in output_data["policies"]:
                    data_accessed.append({
                        "resource_type": "policy",
                        "resource_id": policy.get("id", "unknown"),
                        "classification": policy.get("classification", "unknown"),
                        "redacted": policy.get("redacted", False)
                    })

    except Exception:
        # If extraction fails, log minimal info
        data_accessed.append({
            "resource_type": "unknown",
            "resource_id": "error_extracting",
            "classification": "unknown",
            "redacted": False
        })

    return data_accessed

def get_audit_logs(limit: int = 50) -> list:
    """
    Retrieve recent audit logs for review.

    Args:
        limit: Maximum number of logs to return

    Returns:
        List of audit log entries (most recent first)
    """
    log_file_path = Path(AUDIT_LOG_FILE)

    if not log_file_path.exists():
        return []

    logs = []
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line.strip()))

        # Return most recent logs first
        return logs[-limit:] if logs else []

    except Exception:
        return []
