"""
Consent Management Tool for CrossContext MCP Server
Handles user consent for sensitive operations and progressive disclosure
"""

from fastmcp import FastMCP
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

# Handle imports for both direct execution and module imports
try:
    # Try relative imports (when run as module)
    from ..trust_safety.access_control import generate_consent_request, get_max_classification
    from ..trust_safety.audit_logger import log_tool_invocation
except ImportError:
    # Fall back to absolute imports (when run directly by Claude Desktop)
    import sys
    from pathlib import Path
    # Add the parent directory to Python path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))

    from trust_safety.access_control import generate_consent_request, get_max_classification
    from trust_safety.audit_logger import log_tool_invocation

# Store active consent requests (in production, this would be in a database)
ACTIVE_CONSENT_REQUESTS = {}

def request_user_consent(operation_description: str, tools_involved: List[str], classifications: List[str], estimated_data_count: int = 1) -> Dict[str, Any]:
    """
    Request user consent for a sensitive operation.

    Args:
        operation_description: Description of what the operation will do
        tools_involved: List of tools that will be used
        classifications: List of data classifications involved
        estimated_data_count: Estimated number of data items to be accessed

    Returns:
        Consent request structure with unique ID
    """
    consent_request = generate_consent_request(
        operation=operation_description,
        classifications=classifications,
        tools=tools_involved
    )

    # Add additional metadata
    consent_request["estimated_data_count"] = estimated_data_count
    consent_request["status"] = "pending"
    consent_request["consent_id"] = f"consent_{consent_request['timestamp'].replace(':', '').replace('-', '').replace('+', '_').replace('.', '_')}"

    # Store the request
    ACTIVE_CONSENT_REQUESTS[consent_request["consent_id"]] = consent_request

    # Log the consent request
    log_tool_invocation("consent_request", {
        "operation": operation_description,
        "tools": tools_involved,
        "classifications": classifications
    }, consent_request)

    return consent_request

def check_consent_status(consent_id: str) -> Dict[str, Any]:
    """
    Check the status of a consent request.

    Args:
        consent_id: The consent request ID

    Returns:
        Consent status information
    """
    if consent_id not in ACTIVE_CONSENT_REQUESTS:
        return {
            "consent_id": consent_id,
            "status": "not_found",
            "message": f"Consent request {consent_id} not found"
        }

    consent_request = ACTIVE_CONSENT_REQUESTS[consent_id]
    return {
        "consent_id": consent_id,
        "status": consent_request["status"],
        "operation": consent_request["operation"],
        "highest_classification": consent_request["highest_classification"],
        "requires_consent": consent_request["requires_consent"],
        "timestamp": consent_request["timestamp"]
    }

def grant_consent(consent_id: str, user_id: str = "officer_001") -> Dict[str, Any]:
    """
    Grant consent for a pending request.

    Args:
        consent_id: The consent request ID
        user_id: ID of the user granting consent

    Returns:
        Updated consent status
    """
    if consent_id not in ACTIVE_CONSENT_REQUESTS:
        return {
            "consent_id": consent_id,
            "status": "error",
            "message": f"Consent request {consent_id} not found"
        }

    consent_request = ACTIVE_CONSENT_REQUESTS[consent_id]
    consent_request["status"] = "granted"
    consent_request["granted_by"] = user_id
    consent_request["granted_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()

    # Log the consent grant
    log_tool_invocation("consent_granted", {
        "consent_id": consent_id,
        "user_id": user_id
    }, consent_request)

    return {
        "consent_id": consent_id,
        "status": "granted",
        "message": f"Consent granted for: {consent_request['operation']}",
        "operation": consent_request["operation"],
        "tools_involved": consent_request["tools_involved"],
        "highest_classification": consent_request["highest_classification"]
    }

def deny_consent(consent_id: str, reason: str = "", user_id: str = "officer_001") -> Dict[str, Any]:
    """
    Deny consent for a pending request.

    Args:
        consent_id: The consent request ID
        reason: Optional reason for denial
        user_id: ID of the user denying consent

    Returns:
        Updated consent status
    """
    if consent_id not in ACTIVE_CONSENT_REQUESTS:
        return {
            "consent_id": consent_id,
            "status": "error",
            "message": f"Consent request {consent_id} not found"
        }

    consent_request = ACTIVE_CONSENT_REQUESTS[consent_id]
    consent_request["status"] = "denied"
    consent_request["denied_by"] = user_id
    consent_request["denied_reason"] = reason or "User denied consent"
    consent_request["denied_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()

    # Log the consent denial
    log_tool_invocation("consent_denied", {
        "consent_id": consent_id,
        "user_id": user_id,
        "reason": reason
    }, consent_request)

    return {
        "consent_id": consent_id,
        "status": "denied",
        "message": f"Consent denied for: {consent_request['operation']}",
        "reason": consent_request["denied_reason"]
    }

def get_pending_consents(user_id: str = "officer_001") -> List[Dict[str, Any]]:
    """
    Get all pending consent requests for a user.

    Args:
        user_id: User ID to get pending requests for

    Returns:
        List of pending consent requests
    """
    pending_requests = []
    for consent_id, request in ACTIVE_CONSENT_REQUESTS.items():
        if request["status"] == "pending":
            pending_requests.append({
                "consent_id": consent_id,
                "operation": request["operation"],
                "highest_classification": request["highest_classification"],
                "tools_involved": request["tools_involved"],
                "timestamp": request["timestamp"]
            })

    return pending_requests
