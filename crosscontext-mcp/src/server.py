#!/usr/bin/env python3
"""
CrossContext MCP Server
Government Officer Context Engine with Trust & Safety Layer
"""

import asyncio
import os
from pathlib import Path

from fastmcp import FastMCP
from dotenv import load_dotenv

# Import tools - handle both direct execution and module imports
try:
    # Try relative imports (when run as module)
    from .tools.fetch_emails import fetch_emails
    from .tools.fetch_calendar import fetch_calendar
    from .tools.fetch_stakeholder import fetch_stakeholder
    from .tools.fetch_documents import fetch_documents
    from .tools.search_policies import search_policies
except ImportError:
    # Fall back to absolute imports (when run directly by Claude Desktop)
    import sys
    from pathlib import Path
    # Add the src directory to Python path
    src_dir = Path(__file__).parent
    sys.path.insert(0, str(src_dir))

    from tools.fetch_emails import fetch_emails
    from tools.fetch_calendar import fetch_calendar
    from tools.fetch_stakeholder import fetch_stakeholder
    from tools.fetch_documents import fetch_documents
    from tools.search_policies import search_policies
    from tools.consent_manager import request_user_consent, check_consent_status, grant_consent, deny_consent, get_pending_consents

# Load environment variables
load_dotenv()

# Initialize FastMCP server
app = FastMCP("CrossContext MCP")

@app.tool()
async def echo_tool(message: str) -> str:
    """
    Simple echo tool for testing MCP connection.

    Args:
        message: The message to echo back

    Returns:
        The echoed message
    """
    return f"Echo: {message}"

@app.tool()
async def fetch_emails_tool(query: str = "", max_results: int = 10, user_clearance: str = "officer"):
    """
    Fetch emails matching the query with Singapore government classification and PII redaction.

    Access control is enforced based on user's clearance level:
    - officer: OFFICIAL (OPEN/CLOSED) only
    - senior_officer: Adds RESTRICTED access
    - director: Adds CONFIDENTIAL access
    - admin: Full access

    Args:
        query: Search term or topic to filter emails
        max_results: Maximum number of emails to return
        user_clearance: User's security clearance level

    Returns:
        Dict containing accessible emails with classification info, and access denial details
    """
    return fetch_emails(query=query, max_results=max_results, user_clearance=user_clearance)

@app.tool()
async def fetch_calendar_tool(date_range: str = "upcoming", meeting_title: str = "", max_results: int = 10):
    """
    Fetch calendar events with Singapore government classification and PII redaction.

    Args:
        date_range: Time range filter ("today", "upcoming", "this_week")
        meeting_title: Search for specific meeting by title keywords
        max_results: Maximum number of events to return

    Returns:
        Dict containing events array with classification and redaction info
    """
    return fetch_calendar(date_range=date_range, meeting_title=meeting_title, max_results=max_results)

@app.tool()
async def fetch_stakeholder_tool(name: str = "", email: str = ""):
    """
    Fetch stakeholder context information with Singapore government classification and PII redaction.

    Args:
        name: Stakeholder name to search for
        email: Stakeholder email to search for

    Returns:
        Dict containing stakeholder information with classification and redaction info
    """
    return fetch_stakeholder(name=name, email=email)

@app.tool()
async def fetch_documents_tool(query: str = "", document_type: str = "", max_results: int = 5):
    """
    Search government documents, reports, and guidelines. Use this tool when users need:
    - Detailed policy documents and guidelines
    - Procurement procedures and vendor requirements
    - Budget analysis and financial reports
    - Technical specifications and evaluation criteria
    - Supporting documentation for policies

    Use alongside search_policies_tool for comprehensive policy research.

    Args:
        query: Search terms to find relevant documents
        document_type: Filter by document type (policy, proposal, report, etc.)
        max_results: Maximum number of documents to return

    Returns:
        Dict containing documents array with classification and redaction info
    """
    return fetch_documents(query=query, document_type=document_type, max_results=max_results)

@app.tool()
async def search_policies_tool(query: str = "", policy_type: str = "", max_results: int = 5):
    """
    Search government policies, guidelines, and regulations. Use this tool when users ask about:
    - Approval thresholds and limits (contracts, procurement, budgets)
    - Government policies and procedures
    - Regulatory requirements and compliance
    - Official guidelines and frameworks
    - Policy documents and directives

    Always search policies for questions about vendor contracts, procurement rules, approval processes, compliance requirements, or government regulations.

    Args:
        query: Search terms like "vendor contracts", "approval thresholds", "procurement policy", "budget limits"
        policy_type: Filter by policy type (procurement, healthcare, security, hr, digital)
        max_results: Maximum number of policies to return

    Returns:
        Dict containing policies array with classification and redaction info
    """
    return search_policies(query=query, policy_type=policy_type, max_results=max_results)

@app.tool()
async def request_consent_tool(operation_description: str, tools_involved: str, classifications: str, estimated_data_count: int = 1):
    """
    Request user consent for sensitive operations involving classified data.

    Use this tool when operations will access RESTRICTED or CONFIDENTIAL data to ensure
    user awareness and consent before proceeding with data access.

    Args:
        operation_description: Clear description of what the operation will do
        tools_involved: Comma-separated list of tools to be used (e.g., "fetch_emails,search_policies")
        classifications: Comma-separated list of classifications involved (e.g., "CONFIDENTIAL,RESTRICTED")
        estimated_data_count: Estimated number of data items to be accessed

    Returns:
        Consent request details with unique ID for status checking
    """
    tools_list = [tool.strip() for tool in tools_involved.split(",")]
    classifications_list = [cls.strip() for cls in classifications.split(",")]

    consent_request = request_user_consent(
        operation_description=operation_description,
        tools_involved=tools_list,
        classifications=classifications_list,
        estimated_data_count=estimated_data_count
    )

    return consent_request

@app.tool()
async def check_consent_tool(consent_id: str):
    """
    Check the status of a consent request.

    Args:
        consent_id: The consent request ID to check

    Returns:
        Current status of the consent request
    """
    return check_consent_status(consent_id)

@app.tool()
async def grant_consent_tool(consent_id: str):
    """
    Grant consent for a pending consent request.

    Args:
        consent_id: The consent request ID to grant

    Returns:
        Confirmation of consent grant
    """
    return grant_consent(consent_id)

@app.tool()
async def deny_consent_tool(consent_id: str, reason: str = ""):
    """
    Deny consent for a pending consent request.

    Args:
        consent_id: The consent request ID to deny
        reason: Optional reason for denying consent

    Returns:
        Confirmation of consent denial
    """
    return deny_consent(consent_id, reason)

@app.tool()
async def list_pending_consents_tool():
    """
    List all pending consent requests for the current user.

    Returns:
        List of pending consent requests requiring user action
    """
    return {"pending_consents": get_pending_consents()}

if __name__ == "__main__":
    # Run the MCP server
    import asyncio
    asyncio.run(app.run_stdio_async())
