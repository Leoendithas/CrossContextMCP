"""
Stakeholder context fetching tool for CrossContext MCP Server
"""

# Handle imports for both direct execution and module imports
try:
    # Try relative imports (when run as module)
    from ..trust_safety.classifier import classify_data
    from ..trust_safety.redactor import redact_pii
    from ..trust_safety.audit_logger import log_tool_invocation
except ImportError:
    # Fall back to absolute imports (when run directly by Claude Desktop)
    import sys
    from pathlib import Path
    # Add the parent directory to Python path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))

    from trust_safety.classifier import classify_data
    from trust_safety.redactor import redact_pii
    from trust_safety.audit_logger import log_tool_invocation

# Mock stakeholder data with Singapore government context
MOCK_STAKEHOLDERS = [
    {
        "id": "stakeholder-001",
        "name": "John Tan",
        "email": "john.tan@mof.gov.sg",
        "organization": "Ministry of Finance",
        "role": "Director, Procurement Division",
        "department": "Public Sector Procurement",
        "interaction_history": [
            {
                "date": "2025-01-10T09:30:00+08:00",
                "type": "email",
                "summary": "Sent procurement policy update requiring budget approval"
            },
            {
                "date": "2024-12-15T14:00:00+08:00",
                "type": "meeting",
                "summary": "Discussed vendor evaluation criteria changes"
            }
        ],
        "preferences": "Prefers data-driven discussions, brings detailed cost-benefit analyses to meetings",
        "org_chart_context": "Reports to Deputy Director of Finance, oversees $2.5B annual procurement budget"
    },
    {
        "id": "stakeholder-002",
        "name": "Sarah Lee",
        "email": "sarah.lee@moh.gov.sg",
        "organization": "Ministry of Health",
        "role": "Deputy Director, Healthcare Financing",
        "department": "Healthcare Policy & Financing",
        "interaction_history": [
            {
                "date": "2025-01-11T14:00:00+08:00",
                "type": "email",
                "summary": "Shared healthcare financing meeting agenda"
            },
            {
                "date": "2024-11-20T10:00:00+08:00",
                "type": "meeting",
                "summary": "Cross-agency healthcare financing working group"
            }
        ],
        "preferences": "Focuses on long-term policy implications, prefers advance preparation of materials",
        "org_chart_context": "Leads healthcare financing policy development, coordinates with MOF on budgets"
    },
    {
        "id": "stakeholder-003",
        "name": "David Chen",
        "email": "david.chen@moh.gov.sg",
        "organization": "Ministry of Health",
        "role": "Senior Manager, Healthcare Systems",
        "department": "Digital Health Division",
        "interaction_history": [
            {
                "date": "2025-01-08T11:00:00+08:00",
                "type": "email",
                "summary": "Discussed IT infrastructure requirements for healthcare systems"
            }
        ],
        "preferences": "Technical focus on system implementation, prefers detailed technical specifications",
        "org_chart_context": "Manages digital transformation initiatives, oversees vendor contracts for health tech"
    }
]

def fetch_stakeholder(name: str = "", email: str = ""):
    """
    Fetch stakeholder context information with Singapore government classification and PII redaction.

    Args:
        name: Stakeholder name to search for
        email: Stakeholder email to search for

    Returns:
        Dict containing stakeholder information with classification and redaction info
    """
    # Find matching stakeholder
    stakeholder = None

    if email:
        stakeholder = next((s for s in MOCK_STAKEHOLDERS if s["email"].lower() == email.lower()), None)
    elif name:
        # Simple name matching
        stakeholder = next((s for s in MOCK_STAKEHOLDERS if name.lower() in s["name"].lower()), None)

    if not stakeholder:
        # Return default response if no match found
        response = {
            "stakeholder": None,
            "message": f"No stakeholder found matching name: {name} or email: {email}"
        }
        # Audit log the access (server-side only, not returned to user)
        log_tool_invocation("fetch_stakeholder", {"name": name, "email": email}, response)
        return response

    # Apply trust/safety processing
    classified = classify_data(stakeholder.copy())
    redacted = redact_pii(classified, context="general")

    # Prepare response
    response = {
        "stakeholder": redacted
    }

    # Audit log the access (server-side only, not returned to user)
    log_tool_invocation("fetch_stakeholder", {"name": name, "email": email}, response)

    return response
