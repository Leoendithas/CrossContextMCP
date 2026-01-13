"""
Calendar fetching tool for CrossContext MCP Server
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

# Mock calendar data with Singapore government context
MOCK_EVENTS = [
    {
        "id": "event-001",
        "title": "Procurement Policy Review Meeting",
        "start_time": "2025-01-15T14:00:00+08:00",
        "end_time": "2025-01-15T15:30:00+08:00",
        "attendees": [
            {"name": "John Tan", "email": "john.tan@mof.gov.sg", "role": "organizer"},
            {"name": "Sarah Lee", "email": "sarah.lee@moh.gov.sg", "role": "attendee"},
            {"name": "You", "email": "you@agency.gov.sg", "role": "attendee"}
        ],
        "location": "Conference Room A, Level 5",
        "description": "Review of updated procurement policy. Budget allocation discussion for Q1 2025."
    },
    {
        "id": "event-002",
        "title": "Healthcare Financing Working Group",
        "start_time": "2025-01-16T10:00:00+08:00",
        "end_time": "2025-01-16T12:00:00+08:00",
        "attendees": [
            {"name": "David Chen", "email": "david.chen@moh.gov.sg", "role": "organizer"},
            {"name": "John Tan", "email": "john.tan@mof.gov.sg", "role": "attendee"},
            {"name": "You", "email": "you@agency.gov.sg", "role": "attendee"}
        ],
        "location": "Virtual Meeting (Zoom)",
        "description": "Cross-agency discussion on healthcare financing model. Contact procurement lead at 92345678 for agenda."
    },
    {
        "id": "event-003",
        "title": "Staff Town Hall - Smart Nation Update",
        "start_time": "2025-01-17T15:00:00+08:00",
        "end_time": "2025-01-17T16:30:00+08:00",
        "attendees": [
            {"name": "Communications Director", "email": "comm@gov.sg", "role": "organizer"}
        ],
        "location": "Auditorium, Level 2",
        "description": "Monthly town hall to update staff on Smart Nation 2.0 progress. Open to all government officers."
    },
    {
        "id": "event-004",
        "title": "Vendor Evaluation Session",
        "start_time": "2025-01-14T09:00:00+08:00",
        "end_time": "2025-01-14T11:00:00+08:00",
        "attendees": [
            {"name": "Procurement Lead", "email": "procurement@agency.gov.sg", "role": "organizer"},
            {"name": "You", "email": "you@agency.gov.sg", "role": "attendee"}
        ],
        "location": "Meeting Room B",
        "description": "Evaluation of vendor proposals for IT infrastructure upgrade. Contract value up to $750k."
    }
]

def fetch_calendar(date_range: str = "upcoming", meeting_title: str = "", max_results: int = 10):
    """
    Fetch calendar events with Singapore government classification and PII redaction.

    Args:
        date_range: Time range filter ("today", "upcoming", "this_week")
        meeting_title: Search for specific meeting by title keywords
        max_results: Maximum number of events to return

    Returns:
        Dict containing events array with classification and redaction info
    """
    # Simple filtering implementation
    results = MOCK_EVENTS[:max_results]  # For demo, return all events

    # Apply flexible title filtering if specified (OR logic for multiple terms)
    if meeting_title:
        query_terms = meeting_title.lower().split()
        filtered_results = []
        for event in results:
            searchable_text = (
                event["title"].lower() + " " +
                event["description"].lower() + " " +
                " ".join(attendee.get("name", "").lower() for attendee in event.get("attendees", []))
            )
            # Match if ANY search term is found
            if any(term in searchable_text for term in query_terms):
                filtered_results.append(event)
        results = filtered_results

    # Apply trust/safety processing
    processed_events = []
    for event in results:
        # Classify the event
        classified = classify_data(event.copy())
        # Redact PII with meeting_participant context (don't redact attendee emails)
        redacted = redact_pii(classified, context="meeting_participant")
        processed_events.append(redacted)

    # Prepare response
    response = {
        "events": processed_events,
        "total_count": len(processed_events),
        "redaction_policy": "Meeting participant contact information is preserved to enable follow-up communications"
    }

    # Audit log the access (server-side only, not returned to user)
    log_tool_invocation("fetch_calendar", {
        "date_range": date_range,
        "meeting_title": meeting_title,
        "max_results": max_results
    }, response)

    return response
