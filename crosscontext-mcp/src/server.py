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
async def fetch_emails_tool(query: str = "", max_results: int = 10):
    """
    Fetch emails matching the query with Singapore government classification and PII redaction.

    Args:
        query: Search term or topic to filter emails
        max_results: Maximum number of emails to return

    Returns:
        Dict containing emails array with classification and redaction info
    """
    return fetch_emails(query=query, max_results=max_results)

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
    Fetch documents matching the query with Singapore government classification and PII redaction.

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
    Search government policies with Singapore classification and PII redaction.

    Args:
        query: Search terms to find relevant policies
        policy_type: Filter by policy type (procurement, healthcare, security, hr, digital)
        max_results: Maximum number of policies to return

    Returns:
        Dict containing policies array with classification and redaction info
    """
    return search_policies(query=query, policy_type=policy_type, max_results=max_results)

if __name__ == "__main__":
    # Run the MCP server
    import asyncio
    asyncio.run(app.run_stdio_async())
