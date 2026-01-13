"""
Document fetching tool for CrossContext MCP Server
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

# Mock document data with Singapore government context
MOCK_DOCUMENTS = [
    {
        "id": "doc-001",
        "title": "Procurement Policy 2024 - Final Version",
        "url": "https://drive.gov.sg/procurement-policy-2024",
        "snippet": "This policy establishes guidelines for government procurement processes. Section 4.2 covers vendor evaluation criteria including sustainability metrics.",
        "last_modified": "2025-01-08T10:30:00+08:00",
        "owner": "Procurement Division, MOF",
        "file_type": "PDF",
        "folder_path": "/Policies/Procurement/"
    },
    {
        "id": "doc-002",
        "title": "Healthcare Financing Model Proposal",
        "url": "https://drive.gov.sg/healthcare-financing-proposal",
        "snippet": "Proposal for restructuring healthcare financing to improve cost efficiency. Includes budget impact analysis for S$2.5B annual healthcare expenditure.",
        "last_modified": "2025-01-12T14:20:00+08:00",
        "owner": "Healthcare Policy Division, MOH",
        "file_type": "DOCX",
        "folder_path": "/Proposals/Healthcare/"
    },
    {
        "id": "doc-003",
        "title": "Smart Nation 2.0 Implementation Roadmap",
        "url": "https://drive.gov.sg/smart-nation-roadmap",
        "snippet": "Comprehensive roadmap for Smart Nation 2.0 implementation. Covers digital infrastructure upgrades and citizen engagement initiatives.",
        "last_modified": "2025-01-10T09:15:00+08:00",
        "owner": "Smart Nation Office",
        "file_type": "PPTX",
        "folder_path": "/Strategy/Smart Nation/"
    },
    {
        "id": "doc-004",
        "title": "Vendor Evaluation Criteria - IT Infrastructure",
        "url": "https://drive.gov.sg/vendor-evaluation-it",
        "snippet": "Detailed criteria for evaluating IT infrastructure vendors. Includes technical requirements, compliance checks, and cost-benefit analysis framework.",
        "last_modified": "2025-01-09T16:45:00+08:00",
        "owner": "IT Procurement Team",
        "file_type": "XLSX",
        "folder_path": "/Procurement/IT/"
    },
    {
        "id": "doc-005",
        "title": "Staff Town Hall Presentation - Q4 2024",
        "url": "https://drive.gov.sg/town-hall-q4-2024",
        "snippet": "Presentation materials for quarterly staff town hall. Includes updates on ongoing projects, organizational changes, and upcoming initiatives.",
        "last_modified": "2025-01-06T11:00:00+08:00",
        "owner": "Communications Division",
        "file_type": "PPTX",
        "folder_path": "/Communications/Town Halls/"
    }
]

def fetch_documents(query: str = "", document_type: str = "", max_results: int = 5):
    """
    Fetch documents matching the query with Singapore government classification and PII redaction.

    Args:
        query: Search terms to find relevant documents
        document_type: Filter by document type (policy, proposal, report, etc.)
        max_results: Maximum number of documents to return

    Returns:
        Dict containing documents array with classification and redaction info
    """
    # Flexible search implementation - match ANY term (OR logic)
    if not query:
        results = MOCK_DOCUMENTS[:max_results]
    else:
        query_terms = query.lower().split()
        results = []
        for doc in MOCK_DOCUMENTS:
            searchable_text = (
                doc["title"].lower() + " " +
                doc["snippet"].lower() + " " +
                doc["owner"].lower() + " " +
                doc["folder_path"].lower()
            )
            # Match if ANY search term is found
            if any(term in searchable_text for term in query_terms):
                results.append(doc)
                if len(results) >= max_results:
                    break

    # Apply document type filtering if specified
    if document_type:
        type_filter = document_type.lower()
        filtered_results = []
        for doc in results:
            # Simple document type inference from content/folder
            doc_types = {
                "policy": ["policy", "guidelines", "/policies/"],
                "proposal": ["proposal", "/proposals/"],
                "report": ["analysis", "evaluation", "/reports/"],
                "presentation": ["presentation", "pptx", "/communications/"],
                "spreadsheet": ["xlsx", "criteria"]
            }

            if type_filter in doc_types:
                keywords = doc_types[type_filter]
                if any(keyword.lower() in (doc["title"] + doc["snippet"] + doc["folder_path"]).lower() for keyword in keywords):
                    filtered_results.append(doc)
            else:
                filtered_results.append(doc)  # Include if type filter doesn't match our categories

        results = filtered_results[:max_results]

    # Apply trust/safety processing
    processed_docs = []
    for doc in results:
        # Classify the document
        classified = classify_data(doc.copy())
        # Redact PII with general context
        redacted = redact_pii(classified, context="general")
        processed_docs.append(redacted)

    # Prepare response
    response = {
        "documents": processed_docs,
        "total_count": len(processed_docs)
    }

    # Audit log the access (server-side only, not returned to user)
    log_tool_invocation("fetch_documents", {
        "query": query,
        "document_type": document_type,
        "max_results": max_results
    }, response)

    return response
