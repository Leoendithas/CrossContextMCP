"""
Policy search tool for CrossContext MCP Server
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

# Mock policy data with Singapore government context
MOCK_POLICIES = [
    {
        "id": "policy-001",
        "title": "Government Procurement Policy 2024",
        "policy_number": "FIN-PROC-2024-001",
        "effective_date": "2024-01-01",
        "summary": "Establishes guidelines for government procurement processes, including vendor evaluation criteria, contract approval thresholds, and sustainability requirements.",
        "url": "https://policies.gov.sg/procurement-2024",
        "policy_type": "procurement",
        "ministry": "Ministry of Finance",
        "relevant_sections": [
            {
                "section_number": "4.2",
                "heading": "Vendor Evaluation Criteria",
                "excerpt": "Vendors must demonstrate compliance with sustainability standards and provide cost-benefit analysis for contracts exceeding S$250,000."
            },
            {
                "section_number": "6.1",
                "heading": "Contract Approval Thresholds",
                "excerpt": "Contracts above S$750,000 require deputy director approval. All IT infrastructure contracts require technical evaluation."
            }
        ]
    },
    {
        "id": "policy-002",
        "title": "Healthcare Financing Framework",
        "policy_number": "MOH-HC-2024-002",
        "effective_date": "2024-03-15",
        "summary": "Framework for healthcare financing and cost management, including subsidy structures, co-payment mechanisms, and budget allocation guidelines.",
        "url": "https://policies.gov.sg/healthcare-financing",
        "policy_type": "healthcare",
        "ministry": "Ministry of Health",
        "relevant_sections": [
            {
                "section_number": "2.3",
                "heading": "Subsidy Eligibility Criteria",
                "excerpt": "Citizens with monthly household income below S$3,000 qualify for full subsidies. Income assessment based on IRAS data."
            },
            {
                "section_number": "5.2",
                "heading": "Annual Budget Allocation",
                "excerpt": "Healthcare expenditure not to exceed 4.5% of GDP. S$2.5B allocated for FY2025 preventive care initiatives."
            }
        ]
    },
    {
        "id": "policy-003",
        "title": "Digital Government Security Policy",
        "policy_number": "SNDGO-SEC-2024-003",
        "effective_date": "2024-06-01",
        "summary": "Comprehensive security framework for digital government services, including data classification, access controls, and incident response procedures.",
        "url": "https://policies.gov.sg/digital-security",
        "policy_type": "security",
        "ministry": "Smart Nation and Digital Government Office",
        "relevant_sections": [
            {
                "section_number": "3.1",
                "heading": "Data Classification Levels",
                "excerpt": "Four classification levels: Official (Open), Official (Closed), Restricted, and Confidential Cloud-Eligible. All data must be labeled."
            },
            {
                "section_number": "7.4",
                "heading": "Audit Requirements",
                "excerpt": "All system access must be logged. Audit logs retained for minimum 7 years. Annual security audits mandatory."
            }
        ]
    },
    {
        "id": "policy-004",
        "title": "Human Resource Management Policy",
        "policy_number": "PSD-HR-2024-004",
        "effective_date": "2024-04-01",
        "summary": "HR policies covering recruitment, performance management, leave entitlements, and workplace conduct standards for public officers.",
        "url": "https://policies.gov.sg/hr-management",
        "policy_type": "hr",
        "ministry": "Public Service Division",
        "relevant_sections": [
            {
                "section_number": "8.2",
                "heading": "Medical Leave Entitlements",
                "excerpt": "Officers receive 14 days medical leave annually. Certification from government panel clinics required for leaves exceeding 3 days."
            },
            {
                "section_number": "12.1",
                "heading": "Performance Management",
                "excerpt": "Annual performance reviews mandatory. Performance bonuses capped at 3 months salary for outstanding performance."
            }
        ]
    },
    {
        "id": "policy-005",
        "title": "Smart Nation 2.0 Implementation Guidelines",
        "policy_number": "SNDGO-SN2-2024-005",
        "effective_date": "2024-09-01",
        "summary": "Implementation guidelines for Smart Nation 2.0 initiatives, including digital infrastructure development and citizen engagement frameworks.",
        "url": "https://policies.gov.sg/smart-nation-2",
        "policy_type": "digital",
        "ministry": "Smart Nation and Digital Government Office",
        "relevant_sections": [
            {
                "section_number": "1.4",
                "heading": "Key Objectives",
                "excerpt": "Achieve 100% digital government services by 2027. Implement AI-driven citizen services and predictive maintenance systems."
            },
            {
                "section_number": "9.3",
                "heading": "Vendor Partnerships",
                "excerpt": "Strategic partnerships with technology vendors encouraged. Joint development projects eligible for accelerated procurement approval."
            }
        ]
    }
]

def search_policies(query: str = "", policy_type: str = "", max_results: int = 5):
    """
    Search government policies with Singapore classification and PII redaction.

    Args:
        query: Search terms to find relevant policies
        policy_type: Filter by policy type (procurement, healthcare, security, hr, digital)
        max_results: Maximum number of policies to return

    Returns:
        Dict containing policies array with classification and redaction info
    """
    # Flexible search implementation - match ANY term (OR logic)
    if not query:
        results = MOCK_POLICIES[:max_results]
    else:
        query_terms = query.lower().split()
        results = []
        for policy in MOCK_POLICIES:
            searchable_text = (
                policy["title"].lower() + " " +
                policy["summary"].lower() + " " +
                policy["policy_type"].lower() + " " +
                policy["ministry"].lower() + " " +
                " ".join(section["excerpt"].lower() for section in policy.get("relevant_sections", []))
            )
            # Match if ANY search term is found
            if any(term in searchable_text for term in query_terms):
                results.append(policy)
                if len(results) >= max_results:
                    break

    # Apply policy type filtering if specified
    if policy_type:
        type_filter = policy_type.lower()
        filtered_results = []
        for policy in results:
            if type_filter in policy["policy_type"].lower() or type_filter in policy["title"].lower():
                filtered_results.append(policy)
        results = filtered_results[:max_results]

    # Apply trust/safety processing
    processed_policies = []
    for policy in results:
        # Classify the policy
        classified = classify_data(policy.copy())
        # Redact PII with general context
        redacted = redact_pii(classified, context="general")
        processed_policies.append(redacted)

    # Prepare response
    response = {
        "policies": processed_policies,
        "total_count": len(processed_policies)
    }

    # Audit log the access (server-side only, not returned to user)
    log_tool_invocation("search_policies", {
        "query": query,
        "policy_type": policy_type,
        "max_results": max_results
    }, response)

    return response
