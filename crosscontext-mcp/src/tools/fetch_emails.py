"""
Email fetching tool for CrossContext MCP Server
"""

from fastmcp import FastMCP
from typing import Dict, Any

# Handle imports for both direct execution and module imports
try:
    # Try relative imports (when run as module)
    from ..trust_safety.classifier import classify_data
    from ..trust_safety.redactor import redact_pii
    from ..trust_safety.audit_logger import log_tool_invocation
    from ..trust_safety.access_control import check_access_permission, log_access_decision
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
    from trust_safety.access_control import check_access_permission, log_access_decision

# Mock email data with Singapore government context
MOCK_EMAILS = [
    {
        "id": "email-001",
        "subject": "Procurement Policy Update - Action Required",
        "from": "john.tan@mof.gov.sg",
        "to": ["you@agency.gov.sg"],
        "date": "2025-01-10T09:30:00+08:00",
        "snippet": "Following up on the procurement policy review. Budget allocation of $250k for Q1 has been approved."
    },
    {
        "id": "email-002",
        "subject": "Meeting Agenda: Healthcare Financing Review",
        "from": "sarah.lee@moh.gov.sg",
        "to": ["you@agency.gov.sg", "john.tan@mof.gov.sg"],
        "date": "2025-01-11T14:00:00+08:00",
        "snippet": "Attached is the agenda for tomorrow's meeting. Please call me at 91234567 if you have questions."
    },
    {
        "id": "email-003",
        "subject": "Staff Medical Leave Policy Update",
        "from": "hr@agency.gov.sg",
        "to": ["management@agency.gov.sg"],
        "date": "2025-01-09T11:15:00+08:00",
        "snippet": "Regarding the medical certification for employee S1234567D. The policy has been updated to require 3 days medical leave for minor procedures."
    },
    {
        "id": "email-004",
        "subject": "Vendor Contract Status Update",
        "from": "procurement@agency.gov.sg",
        "to": ["you@agency.gov.sg"],
        "date": "2025-01-08T16:45:00+08:00",
        "snippet": "The contract with Acme Solutions for IT infrastructure is ready for final approval. Value: $500k over 2 years."
    },
    {
        "id": "email-005",
        "subject": "Public Consultation on Smart Nation 2.0",
        "from": "communications@gov.sg",
        "to": ["all-staff@gov.sg"],
        "date": "2025-01-07T08:00:00+08:00",
        "snippet": "We are seeking feedback on the Smart Nation 2.0 initiative. Public consultation period ends February 15th."
    }
]

def fetch_emails(query: str = "", max_results: int = 10, user_clearance: str = "officer"):
    """
    Fetch emails matching the query with Singapore government classification and PII redaction.

    Args:
        query: Search term or topic to filter emails
        max_results: Maximum number of emails to return
        user_clearance: User's security clearance level ("officer", "senior_officer", "director", "admin")

    Returns:
        Dict containing emails array with classification and redaction info, or access denied message
    """
    # Flexible search implementation - match ANY term (OR logic)
    if not query:
        results = MOCK_EMAILS[:max_results]
    else:
        query_terms = query.lower().split()
        results = []
        for email in MOCK_EMAILS:
            searchable_text = (
                email["subject"].lower() + " " +
                email["from"].lower() + " " +
                email["snippet"].lower()
            )
            # Match if ANY search term is found
            if any(term in searchable_text for term in query_terms):
                results.append(email)
                if len(results) >= max_results:
                    break

    # Apply trust/safety processing
    processed_emails = []
    access_denied_emails = []

    for email in results:
        # Classify the email
        classified = classify_data(email.copy())

        # Check user access permission for this email's classification
        access_check = check_access_permission(user_clearance, classified["classification"])

        if access_check["access_granted"]:
            # User has access - redact PII and include email
            redacted = redact_pii(classified, context="general")
            processed_emails.append(redacted)
        else:
            # User doesn't have access - record denial and exclude email
            access_denied_emails.append({
                "id": email["id"],
                "classification": classified["classification"],
                "access_denied_reason": access_check["reason"]
            })

            # Log the access denial
            log_access_decision("officer_001", f"fetch_email_{email['id']}", access_check)

    # Prepare response
    response = {
        "emails": processed_emails,
        "total_count": len(processed_emails),
        "access_denials": access_denied_emails,
        "user_clearance": user_clearance
    }

    # Add summary if there were access denials
    if access_denied_emails:
        response["access_summary"] = f"Access granted to {len(processed_emails)} emails, denied to {len(access_denied_emails)} emails due to insufficient clearance level"

    # Audit log the access (server-side only, not returned to user)
    log_tool_invocation("fetch_emails", {
        "query": query,
        "max_results": max_results,
        "user_clearance": user_clearance
    }, response)

    return response
