"""
Access Control System for CrossContext MCP
Implements Singapore government classification-based access controls
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

# Singapore Government Security Classification Hierarchy
# Higher levels include access to lower levels
CLASSIFICATION_HIERARCHY = {
    "OFFICIAL (OPEN)": 1,          # Lowest - public information
    "OFFICIAL (CLOSED)": 2,        # Internal communications
    "RESTRICTED": 3,               # Personal/disciplinary data
    "CONFIDENTIAL CLOUD-ELIGIBLE": 4  # Highest - sensitive financial/procurement
}

# User clearance levels and their allowed classifications
USER_CLEARANCE_LEVELS = {
    "officer": ["OFFICIAL (OPEN)", "OFFICIAL (CLOSED)"],  # Basic government officer
    "senior_officer": ["OFFICIAL (OPEN)", "OFFICIAL (CLOSED)", "RESTRICTED"],  # Senior roles
    "director": ["OFFICIAL (OPEN)", "OFFICIAL (CLOSED)", "RESTRICTED", "CONFIDENTIAL CLOUD-ELIGIBLE"],  # Full access
    "admin": ["ALL"]  # System administrators
}

def check_access_permission(user_clearance: str, data_classification: str) -> Dict[str, any]:
    """
    Check if user has permission to access data of given classification.

    Args:
        user_clearance: User's clearance level ("officer", "senior_officer", "director", "admin")
        data_classification: Data classification level

    Returns:
        Dict with access decision and metadata
    """
    if user_clearance not in USER_CLEARANCE_LEVELS:
        return {
            "access_granted": False,
            "reason": f"Invalid user clearance level: {user_clearance}",
            "required_clearance": None
        }

    allowed_classifications = USER_CLEARANCE_LEVELS[user_clearance]

    # Admin has access to everything
    if "ALL" in allowed_classifications:
        return {
            "access_granted": True,
            "reason": "Administrative access granted",
            "user_clearance": user_clearance,
            "data_classification": data_classification
        }

    # Check if data classification is allowed for this user level
    if data_classification in allowed_classifications:
        return {
            "access_granted": True,
            "reason": f"Access granted for {user_clearance} level user",
            "user_clearance": user_clearance,
            "data_classification": data_classification
        }

    # Find minimum clearance level required
    required_level = None
    data_level = CLASSIFICATION_HIERARCHY.get(data_classification, 0)

    for clearance_level, allowed in USER_CLEARANCE_LEVELS.items():
        if "ALL" in allowed or data_classification in allowed:
            required_level = clearance_level
            break

    return {
        "access_granted": False,
        "reason": f"Insufficient clearance. {data_classification} requires {required_level} level access",
        "user_clearance": user_clearance,
        "data_classification": data_classification,
        "required_clearance": required_level
    }

def get_max_classification(classifications: List[str]) -> str:
    """
    Get the highest classification level from a list.

    Args:
        classifications: List of classification levels

    Returns:
        Highest classification level
    """
    if not classifications:
        return "OFFICIAL (OPEN)"

    max_level = 0
    max_classification = "OFFICIAL (OPEN)"

    for classification in classifications:
        level = CLASSIFICATION_HIERARCHY.get(classification, 0)
        if level > max_level:
            max_level = level
            max_classification = classification

    return max_classification

def generate_consent_request(operation: str, classifications: List[str], tools: List[str]) -> Dict[str, any]:
    """
    Generate a user consent request for sensitive operations.

    Args:
        operation: Description of the operation
        classifications: List of data classifications involved
        tools: List of tools to be used

    Returns:
        Consent request structure
    """
    max_classification = get_max_classification(classifications)

    # Determine if consent is required based on classification
    requires_consent = CLASSIFICATION_HIERARCHY.get(max_classification, 0) >= CLASSIFICATION_HIERARCHY.get("RESTRICTED", 3)

    consent_request = {
        "operation": operation,
        "tools_involved": tools,
        "classifications": list(set(classifications)),  # Remove duplicates
        "highest_classification": max_classification,
        "requires_consent": requires_consent,
        "consent_reason": get_consent_reason(max_classification),
        "estimated_data_count": len(classifications),
        "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat()
    }

    return consent_request

def get_consent_reason(classification: str) -> str:
    """
    Get human-readable reason for requiring consent.

    Args:
        classification: Data classification level

    Returns:
        Reason for consent requirement
    """
    reasons = {
        "OFFICIAL (OPEN)": "No consent required - public information",
        "OFFICIAL (CLOSED)": "Internal communications access",
        "RESTRICTED": "Access to personal or disciplinary information",
        "CONFIDENTIAL CLOUD-ELIGIBLE": "Access to sensitive financial or procurement data"
    }

    return reasons.get(classification, "Access to sensitive government data")

def log_access_decision(user_id: str, operation: str, access_result: Dict[str, any]) -> str:
    """
    Log access control decisions for audit purposes.

    Args:
        user_id: User identifier
        operation: Operation being performed
        access_result: Result from check_access_permission

    Returns:
        Audit log ID
    """
    # Import here to avoid circular imports
    from .audit_logger import log_tool_invocation

    audit_data = {
        "access_control_event": True,
        "user_id": user_id,
        "operation": operation,
        "access_granted": access_result.get("access_granted", False),
        "reason": access_result.get("reason", ""),
        "user_clearance": access_result.get("user_clearance", ""),
        "data_classification": access_result.get("data_classification", ""),
        "required_clearance": access_result.get("required_clearance", "")
    }

    # Log as a special access control event
    return log_tool_invocation("access_control", {}, audit_data)
