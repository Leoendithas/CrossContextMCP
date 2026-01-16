# CrossContext MCP: Government Officer Context Engine
## Architecture & Implementation Guide

---

## Executive Summary

**Project Name:** CrossContext MCP
**Purpose:** Demonstrate MCP expertise for GovTech AI Assistant Product Manager role
**Problem Solved:** Operational fragmentation and context-switching for government officers
**Key Differentiator:** Built-in trust/safety layer with Singapore government data classification (CONFIDENTIAL CLOUD-ELIGIBLE, RESTRICTED, OFFICIAL), DLP-compliant redaction, and audit logging
**Timeline:** 48-hour sprint focusing on working prototype with real Google APIs

---

## 1. Project Overview

### 1.1 The Problem
Government officers juggle multiple disconnected systems:
- Email (Outlook/Gmail) for correspondence
- Document repositories (Google Drive/SharePoint) for policies and briefings
- Calendar systems for meetings and schedules
- Internal databases for stakeholder information

**Result:** Officers spend 30-40% of their time context-switching and manually aggregating information before meetings or decisions.

### 1.2 The Solution
An MCP server that acts as a unified context layer, enabling AI Assistants to:
- Automatically fetch relevant information from multiple systems
- Synthesize briefings with proper citations
- Apply trust/safety controls (classification, redaction, audit logging)
- Reduce context-switching from hours to seconds

### 1.3 Technical Approach
- **MCP Server:** Python (FastMCP) - chosen for faster prototyping and data processing capabilities
- **Agentic Workflow:** Multi-tool orchestration with Claude as the reasoning engine
- **Integration Pattern:** Real Google APIs (Gmail, Calendar, Drive) + mock services for government-specific systems
- **Trust Layer:** Singapore government classification engine (CONFIDENTIAL CLOUD-ELIGIBLE, RESTRICTED, OFFICIAL), DLP-compliant PII redaction, access control, audit logs

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Desktop / Client                  │
│                  (User: Government Officer)                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ MCP Protocol
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   CrossContext MCP Server                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Trust & Safety Layer                     │  │
│  │  • Data Classification Engine                         │  │
│  │  • PII Redaction                                      │  │
│  │  • Access Control                                     │  │
│  │  • Audit Logger                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Tool Orchestration Layer                 │  │
│  │  • Tool registry & routing                            │  │
│  │  • Agentic workflow coordinator                       │  │
│  │  • Context aggregation engine                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   MCP Tools                           │  │
│  │                                                        │  │
│  │  fetch_emails          fetch_documents                │  │
│  │  fetch_calendar        fetch_stakeholder_context      │  │
│  │  generate_briefing     search_policies                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼─────┐      ┌─────▼──────┐     ┌─────▼──────┐
    │  Gmail   │      │   Google   │     │  Google    │
    │   API    │      │  Drive API │     │ Calendar   │
    └──────────┘      └────────────┘     └────────────┘
         │                   │                   │
    ┌────▼──────────────────▼───────────────────▼────┐
    │         Mock Government Systems                 │
    │  • Stakeholder DB                               │
    │  • Policy Repository                            │
    │  • Access Control Service                       │
    └─────────────────────────────────────────────────┘
```

### 2.2 Component Breakdown

#### A. MCP Server Core
- **Framework:** FastMCP (Python) or @modelcontextprotocol/sdk (Node.js)
- **Transport:** stdio (for Claude Desktop) or SSE (for web deployments)
- **Configuration:** Environment variables for API keys, database connections

#### B. Trust & Safety Layer
- **Data Classification Engine:** Tags all retrieved data with sensitivity levels
- **PII Redaction:** Detects and redacts NRIC, phone numbers, addresses, emails
- **Access Control:** Validates officer permissions before data retrieval
- **Audit Logger:** Logs all tool invocations with timestamp, user, data accessed

#### C. Tool Orchestration Layer
- **Tool Registry:** Dynamic tool discovery and schema validation
- **Workflow Coordinator:** Manages multi-tool agentic sequences
- **Context Aggregator:** Merges results from multiple tools into coherent responses

#### D. MCP Tools (11 Total: 6 Core + 5 Consent Management)

---

## 3. MCP Tool Specifications

### 3.1 Tool: `fetch_emails`

**Purpose:** Retrieve relevant emails from officer's inbox

**Input Schema:**
```json
{
  "query": "string (search term or topic)",
  "person": "string (optional - filter by sender/recipient)",
  "date_range": "string (e.g., 'last_7_days', 'last_30_days')",
  "max_results": "integer (default: 10)"
}
```

**Output Schema:**
```json
{
  "emails": [
    {
      "id": "string",
      "subject": "string",
      "from": "string",
      "to": "string[]",
      "date": "ISO8601 timestamp",
      "snippet": "string (first 200 chars)",
      "classification": "PUBLIC | CONFIDENTIAL | RESTRICTED",
      "redacted": "boolean"
    }
  ],
  "total_count": "integer",
  "audit_log_id": "string"
}
```

**Implementation Notes:**
- Use Gmail API (for prototype) or Microsoft Graph API (for production)
- Apply classification rules based on sender domain, subject keywords
- Redact PII in snippets before returning

---

### 3.2 Tool: `fetch_documents`

**Purpose:** Search and retrieve documents from shared drives

**Input Schema:**
```json
{
  "query": "string (search terms)",
  "document_type": "string (optional - 'policy' | 'briefing' | 'report')",
  "date_range": "string (optional)",
  "folder_path": "string (optional - restrict search scope)",
  "max_results": "integer (default: 5)"
}
```

**Output Schema:**
```json
{
  "documents": [
    {
      "id": "string",
      "title": "string",
      "url": "string",
      "snippet": "string (relevant excerpt)",
      "last_modified": "ISO8601 timestamp",
      "owner": "string",
      "classification": "PUBLIC | CONFIDENTIAL | RESTRICTED",
      "access_granted": "boolean"
    }
  ],
  "total_count": "integer",
  "audit_log_id": "string"
}
```

**Implementation Notes:**
- Use Google Drive API or SharePoint API
- Implement classification heuristics (filename patterns, folder structure)
- Check access permissions before returning results

---

### 3.3 Tool: `fetch_calendar`

**Purpose:** Retrieve officer's calendar events and meeting details

**Input Schema:**
```json
{
  "date_range": "string (e.g., 'today', 'next_7_days', 'YYYY-MM-DD to YYYY-MM-DD')",
  "meeting_title": "string (optional - search for specific meeting)",
  "attendee": "string (optional - filter by attendee name/email)",
  "include_past": "boolean (default: false)"
}
```

**Output Schema:**
```json
{
  "events": [
    {
      "id": "string",
      "title": "string",
      "start_time": "ISO8601 timestamp",
      "end_time": "ISO8601 timestamp",
      "attendees": [
        {
          "name": "string",
          "email": "string",
          "role": "organizer | attendee"
        }
      ],
      "location": "string",
      "description": "string (redacted if contains PII)",
      "classification": "PUBLIC | CONFIDENTIAL | RESTRICTED"
    }
  ],
  "audit_log_id": "string"
}
```

**Implementation Notes:**
- Use Google Calendar API or Microsoft Calendar API
- Classify based on attendee list (external attendees = higher classification)
- Redact sensitive meeting notes/descriptions

---

### 3.4 Tool: `fetch_stakeholder_context`

**Purpose:** Retrieve background information on stakeholders/meeting attendees

**Input Schema:**
```json
{
  "name": "string (person's name)",
  "email": "string (optional - for disambiguation)",
  "include_history": "boolean (default: true - past interactions)"
}
```

**Output Schema:**
```json
{
  "stakeholder": {
    "name": "string",
    "email": "string",
    "organization": "string",
    "role": "string",
    "department": "string",
    "classification": "PUBLIC | CONFIDENTIAL | RESTRICTED",
    "interaction_history": [
      {
        "date": "ISO8601 timestamp",
        "type": "meeting | email | document",
        "summary": "string (brief description)"
      }
    ],
    "preferences": "string (optional - communication preferences, past feedback)",
    "org_chart_context": "string (reporting line, team structure)"
  },
  "audit_log_id": "string"
}
```

**Implementation Notes:**
- Use mock database initially (SQLite or JSON file)
- In production: integrate with LDAP/Active Directory or HR systems
- This is the most "government-specific" tool - shows understanding of public service context

---

### 3.5 Tool: `search_policies`

**Purpose:** Search agency policy documents and regulations

**Input Schema:**
```json
{
  "query": "string (policy topic or keyword)",
  "policy_type": "string (optional - 'procurement' | 'hr' | 'financial' | 'security')",
  "effective_date": "string (optional - YYYY-MM-DD)",
  "include_archived": "boolean (default: false)"
}
```

**Output Schema:**
```json
{
  "policies": [
    {
      "id": "string",
      "title": "string",
      "policy_number": "string (e.g., 'FIN-2024-03')",
      "effective_date": "ISO8601 timestamp",
      "summary": "string (key provisions)",
      "url": "string (link to full policy)",
      "classification": "PUBLIC | CONFIDENTIAL | RESTRICTED",
      "relevant_sections": [
        {
          "section_number": "string",
          "heading": "string",
          "excerpt": "string"
        }
      ]
    }
  ],
  "audit_log_id": "string"
}
```

**Implementation Notes:**
- Mock with a structured JSON/SQLite database
- Demonstrates understanding of government compliance needs
- Shows ability to work with structured, versioned documents

---

### 3.6 Tool: `generate_briefing`

**Purpose:** Synthesize briefing from pre-fetched data sources (Claude orchestrates tool calls)

**Input Schema:**
```json
{
  "context": "string (meeting topic or decision context)",
  "briefing_type": "string ('meeting_prep' | 'decision_memo' | 'stakeholder_brief')",
  "emails_data": "string (JSON array of pre-fetched email objects)",
  "calendar_data": "string (JSON array of pre-fetched calendar objects)",
  "policy_data": "string (JSON array of pre-fetched policy objects)",
  "stakeholder_data": "string (JSON object of pre-fetched stakeholder info)"
}
```

**Output Schema:**
```json
{
  "briefing": {
    "title": "string",
    "summary": "string (executive summary)",
    "key_points": "string[] (bulleted list)",
    "background": "string (contextual information)",
    "stakeholder_analysis": "string (who's involved, their positions)",
    "recommendations": "string (optional - suggested talking points and actions)",
    "citations": [
      {
        "source_type": "email | document | calendar",
        "excerpt": "string",
        "classification": "string"
      }
    ],
    "highest_classification": "OFFICIAL (OPEN) | OFFICIAL (CLOSED) | CONFIDENTIAL CLOUD-ELIGIBLE | RESTRICTED"
  },
  "audit_log_id": "string"
}
```

**Implementation Notes:**
- Takes pre-fetched data as input (Claude orchestrates the multi-tool workflow)
- Demonstrates Claude's natural reasoning for complex multi-step tasks
- Applies Singapore government classification rules to final output

---

## 4. Trust & Safety Implementation

### 4.1 Data Classification Engine

**Classification Rules:**
```python
CLASSIFICATION_RULES = {
    "RESTRICTED": [
        "keywords": ["NRIC", "salary", "disciplinary", "investigation"],
        "sender_domains": ["external-*", "contractor-*"],
        "folder_paths": ["/Confidential/", "/HR/"]
    ],
    "CONFIDENTIAL": [
        "keywords": ["budget", "procurement", "tender", "contract"],
        "sender_domains": ["vendor.com", "supplier.com"],
        "folder_paths": ["/Internal/", "/Finance/"]
    ],
    "PUBLIC": [
        "default": True  # Fallback classification
    ]
}
```

**Implementation:**
```python
def classify_data(content: str, metadata: dict) -> str:
    """
    Classify data based on content, metadata, and context
    Returns: "RESTRICTED" | "CONFIDENTIAL" | "PUBLIC"
    """
    # Check RESTRICTED triggers first (highest sensitivity)
    if any(keyword in content.lower() for keyword in CLASSIFICATION_RULES["RESTRICTED"]["keywords"]):
        return "RESTRICTED"
    
    # Check sender domain (for emails)
    if metadata.get("sender_domain") in CLASSIFICATION_RULES["RESTRICTED"]["sender_domains"]:
        return "RESTRICTED"
    
    # Check CONFIDENTIAL triggers
    if any(keyword in content.lower() for keyword in CLASSIFICATION_RULES["CONFIDENTIAL"]["keywords"]):
        return "CONFIDENTIAL"
    
    # Default to PUBLIC
    return "PUBLIC"
```

### 4.2 PII Redaction Engine

**PII Patterns to Detect:**
- **NRIC:** `[STFG]\d{7}[A-Z]` (Singapore National Registration Identity Card)
- **Phone Numbers:** `[+]?65[-\s]?[689]\d{7}`
- **Email Addresses:** `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- **Postal Codes:** `\b\d{6}\b`
- **Names (heuristic):** Proper nouns in specific contexts (e.g., "Mr. John Tan", "Dr. Sarah Lee")

**Implementation:**
```python
import re

def redact_pii(text: str) -> tuple[str, bool]:
    """
    Redact PII from text
    Returns: (redacted_text, was_redacted)
    """
    was_redacted = False
    
    # Redact NRIC
    if re.search(r'[STFG]\d{7}[A-Z]', text):
        text = re.sub(r'[STFG]\d{7}[A-Z]', '[NRIC REDACTED]', text)
        was_redacted = True
    
    # Redact phone numbers
    if re.search(r'[+]?65[-\s]?[689]\d{7}', text):
        text = re.sub(r'[+]?65[-\s]?[689]\d{7}', '[PHONE REDACTED]', text)
        was_redacted = True
    
    # Redact email addresses
    if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', text)
        was_redacted = True
    
    return text, was_redacted
```

### 4.3 Access Control

**Singapore Government Clearance Levels:**
```python
USER_CLEARANCE_LEVELS = {
    "officer": ["OFFICIAL (OPEN)", "OFFICIAL (CLOSED)"],  # Basic government officer
    "senior_officer": ["OFFICIAL (OPEN)", "OFFICIAL (CLOSED)", "RESTRICTED"],  # Senior roles
    "director": ["OFFICIAL (OPEN)", "OFFICIAL (CLOSED)", "RESTRICTED", "CONFIDENTIAL CLOUD-ELIGIBLE"],  # Full access
    "admin": ["ALL"]  # System administrators
}
```

**Classification Hierarchy:**
```python
CLASSIFICATION_HIERARCHY = {
    "OFFICIAL (OPEN)": 1,          # Lowest - public information
    "OFFICIAL (CLOSED)": 2,        # Internal communications
    "RESTRICTED": 3,               # Personal/disciplinary data
    "CONFIDENTIAL CLOUD-ELIGIBLE": 4  # Highest - sensitive financial/procurement
}
```

**Access Control Implementation:**
```python
def check_access_permission(user_clearance: str, data_classification: str) -> Dict[str, any]:
    """
    Check if user has permission to access data of given classification.

    Returns detailed access decision with audit information.
    """
    allowed_classifications = USER_CLEARANCE_LEVELS[user_clearance]

    # Admin has access to everything
    if "ALL" in allowed_classifications:
        return {
            "access_granted": True,
            "reason": "Administrative access granted"
        }

    # Check if data classification is allowed for this user level
    if data_classification in allowed_classifications:
        return {
            "access_granted": True,
            "reason": f"Access granted for {user_clearance} level user"
        }

    # Find minimum clearance level required
    data_level = CLASSIFICATION_HIERARCHY.get(data_classification, 0)
    required_level = None
    for clearance_level, allowed in USER_CLEARANCE_LEVELS.items():
        if "ALL" in allowed or data_classification in allowed:
            required_level = clearance_level
            break

    return {
        "access_granted": False,
        "reason": f"Insufficient clearance. {data_classification} requires {required_level} level access",
        "required_clearance": required_level
    }
```

### 4.4 Progressive Disclosure & User Consent

**Consent Request Generation:**
```python
def generate_consent_request(operation: str, classifications: List[str], tools: List[str]) -> Dict[str, any]:
    """
    Generate a user consent request for sensitive operations.
    """
    max_classification = get_max_classification(classifications)

    # Determine if consent is required based on classification
    requires_consent = CLASSIFICATION_HIERARCHY.get(max_classification, 0) >= CLASSIFICATION_HIERARCHY.get("RESTRICTED", 3)

    return {
        "operation": operation,
        "tools_involved": tools,
        "classifications": list(set(classifications)),
        "highest_classification": max_classification,
        "requires_consent": requires_consent,
        "consent_reason": get_consent_reason(max_classification),
        "consent_id": generate_unique_id()
    }
```

**Consent Workflow States:**
```python
CONSENT_STATES = {
    "pending": "Awaiting user decision",
    "granted": "User approved access",
    "denied": "User denied access",
    "expired": "Consent request timed out"
}
```

**Implementation in Tools:**
```python
# All sensitive tools now include user_clearance parameter
@app.tool()
async def fetch_emails_tool(query: str = "", max_results: int = 10, user_clearance: str = "officer"):
    """
    Enhanced with access control - checks user clearance against data classification
    before returning results. Access denials are logged and reported.
    """
    # Implementation includes access checking and denial reporting
```

### 4.4 Audit Logging

**Audit Log Schema:**
```json
{
  "log_id": "uuid",
  "timestamp": "ISO8601",
  "user_id": "string",
  "tool_name": "string",
  "tool_input": "object (sanitized - no PII)",
  "data_accessed": [
    {
      "resource_type": "email | document | calendar | stakeholder",
      "resource_id": "string",
      "classification": "string"
    }
  ],
  "access_granted": "boolean",
  "redaction_applied": "boolean",
  "client_ip": "string",
  "session_id": "string"
}
```

**Implementation:**
```python
import json
import uuid
from datetime import datetime

class AuditLogger:
    def __init__(self, log_file="audit_log.jsonl"):
        self.log_file = log_file
    
    def log_tool_invocation(self, user_id: str, tool_name: str, 
                           tool_input: dict, data_accessed: list,
                           access_granted: bool, redaction_applied: bool):
        """
        Log every tool invocation for compliance
        """
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "tool_name": tool_name,
            "tool_input": self._sanitize_input(tool_input),
            "data_accessed": data_accessed,
            "access_granted": access_granted,
            "redaction_applied": redaction_applied,
            "session_id": self._get_session_id()
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return log_entry["log_id"]
    
    def _sanitize_input(self, tool_input: dict) -> dict:
        """Remove PII from logged inputs"""
        # Create a copy and redact sensitive fields
        sanitized = tool_input.copy()
        if "email" in sanitized:
            sanitized["email"] = "[EMAIL REDACTED]"
        if "nric" in sanitized:
            sanitized["nric"] = "[NRIC REDACTED]"
        return sanitized
```

---

## 5. Agentic Workflow Examples

### 5.1 Workflow: Meeting Briefing

**User Query:**  
_"Brief me for my 2pm meeting with John Tan about the new procurement policy"_

**Agentic Reasoning Flow:**
1. **Understand context:** Extract key entities (John Tan, procurement policy, 2pm meeting)
2. **Fetch calendar:** Find the 2pm meeting to get full details (attendees, agenda)
3. **Fetch stakeholder context:** Get John Tan's background, role, past interactions
4. **Search policies:** Find relevant procurement policy documents
5. **Fetch emails:** Get recent correspondence with John about procurement
6. **Fetch documents:** Get any shared briefings or reports related to procurement
7. **Synthesize briefing:** Combine all context into structured brief with citations
8. **Apply trust/safety:** Classify final briefing, redact PII, log audit trail

**Tool Call Sequence:**
```
1. fetch_calendar(date_range="today", meeting_title="procurement", attendee="John Tan")
   → Meeting found: 2-3pm, attendees: John Tan, Sarah Lee, you

2. fetch_stakeholder_context(name="John Tan", include_history=true)
   → Role: Director, Procurement Division; Previous meetings: 3 in last 6 months

3. search_policies(query="procurement policy", policy_type="procurement", effective_date="2024-01-01")
   → Found: "Procurement Policy 2024 (Updated)" - key changes in Section 4.2

4. fetch_emails(query="procurement John Tan", date_range="last_30_days", max_results=5)
   → 3 email threads: budget concerns, vendor evaluation, timeline clarification

5. fetch_documents(query="procurement briefing", document_type="briefing", max_results=3)
   → Found: "Q4 Procurement Review.pptx", "Vendor Evaluation Criteria.docx"

6. generate_briefing(
     context="Meeting with John Tan on procurement policy",
     sources=[calendar_id, emails[0-2], documents[0-1], policy[0]],
     briefing_type="meeting_prep",
     include_citations=true
   )
   → Synthesized briefing with key points, citations, recommendations
```

**Final Output to User:**
```markdown
# Meeting Brief: Procurement Policy Discussion with John Tan
**Date:** 2025-01-12, 2:00 PM - 3:00 PM
**Classification:** CONFIDENTIAL

## Executive Summary
John Tan (Director, Procurement Division) is seeking your input on the updated 
Procurement Policy 2024, specifically Section 4.2 regarding vendor evaluation 
criteria. Recent email exchanges indicate concerns about budget allocation 
(15% increase required) and timeline feasibility for Q1 implementation.

## Key Points
1. **Policy Update:** Section 4.2 now requires multi-criteria vendor evaluation 
   including sustainability metrics [Source: Procurement Policy 2024, p.12]

2. **Budget Concerns:** John raised concerns in email (2025-01-08) about the 
   15% budget increase needed for new evaluation framework [CONFIDENTIAL]

3. **Timeline:** Original Q1 2025 rollout may be delayed to Q2 due to vendor 
   onboarding requirements [Source: Email thread "Procurement Timeline"]

## Stakeholder Context
- **John Tan:** 8 years at agency, previous meetings focused on cost optimization
- **Past Interactions:** Prefers data-driven discussions, typically brings detailed 
  cost-benefit analyses

## Recommendations
- Prepare to discuss phased implementation approach
- Bring Q1 vs Q2 cost comparison data
- Address sustainability criteria implementation timeline

## Citations
[1] Email: John Tan → You, 2025-01-08, "Budget concerns for procurement update"
[2] Document: "Q4 Procurement Review.pptx", last modified 2024-12-15
[3] Policy: "Procurement Policy 2024 (Updated)", Section 4.2, effective 2024-01-01

**Audit Log ID:** a7f3c2e1-4b89-4d0c-9e3f-1234567890ab
```

### 5.2 Workflow: Multi-Agency Coordination

**User Query:**  
_"I need to coordinate with MOF and MOH on the joint healthcare financing project. What's the current status across agencies?"_

**Agentic Reasoning Flow:**
1. Search emails for correspondence with MOF and MOH contacts
2. Fetch shared documents in project folders for both agencies
3. Search meeting notes from past cross-agency meetings
4. Fetch stakeholder context for key contacts at MOF and MOH
5. Synthesize current status, identify gaps, flag action items
6. Apply highest classification level (multi-agency = likely CONFIDENTIAL+)

**Key Complexity:** Demonstrates ability to aggregate across organizational boundaries while maintaining proper classification and access controls.

---

## 6. Implementation Phases

### Phase 1: Foundation & Core MCP Server (48-Hour Sprint)
**Goal:** Get working MCP server with real Gmail/Calendar APIs + basic trust/safety for GovTech PM demo

**Day 1 (24 hours): Core Setup & Basic Tools**
1. **Environment Setup (4 hours)**
   - Install Python 3.9+, create virtual environment
   - Install FastMCP: `pip install fastmcp`
   - Install Google APIs: `pip install google-auth google-api-python-client google-auth-oauthlib`
   - Set up Claude Desktop for MCP testing

2. **Basic MCP Server (8 hours)**
   - Create `server.py` with FastMCP server initialization
   - Implement "echo" tool for connection testing
   - Configure stdio transport for Claude Desktop
   - Verify MCP ↔ Claude Desktop connection works

3. **Google API Setup (4 hours)**
   - Create Google Cloud Project, enable Gmail + Calendar APIs
   - Set up OAuth 2.0 credentials (Desktop application type)
   - Implement basic Gmail client with read-only access
   - Implement basic Calendar client with read-only access

4. **First Tool: fetch_emails (4 hours)**
   - Implement `fetch_emails` with Gmail API integration
   - Add basic input validation and error handling
   - Test real email fetching through Claude Desktop

5. **Second Tool: fetch_calendar (4 hours)**
   - Implement `fetch_calendar` with Google Calendar API
   - Add date range handling and attendee filtering
   - Test real calendar event fetching

**Day 2 (24 hours): Trust/Safety Integration & Demo Prep**
1. **Basic Classification Engine (4 hours)**
   - Implement Singapore government classification rules:
     - CONFIDENTIAL CLOUD-ELIGIBLE → "CONFIDENTIAL"
     - RESTRICTED → "RESTRICTED"
     - OFFICIAL (CLOSED) → "RESTRICTED"
     - OFFICIAL (OPEN) → "PUBLIC"
   - Add keyword-based classification for emails/calendar

2. **PII Redaction (4 hours)**
   - Implement regex patterns for Singapore-specific PII:
     - NRIC: `[STFG]\d{7}[A-Z]`
     - Phone: `[+]?65[-\s]?[689]\d{7}`
     - Email addresses
   - Add redaction to email snippets and meeting descriptions

3. **Audit Logging (4 hours)**
   - Create JSONL-based audit logger
   - Log every tool invocation with sanitized inputs
   - Add audit log IDs to all tool responses

4. **Demo Scenarios (8 hours)**
   - Create 2-3 working demo prompts
   - Test end-to-end workflows with real data
   - Ensure trust/safety features are visible
   - Prepare presentation-ready examples

5. **Polish & Testing (4 hours)**
   - Add error handling and user-friendly messages
   - Verify < 5 second latency for demo scenarios
   - Test edge cases and API failures gracefully

**Success Criteria for 48 Hours:**
- ✅ Working MCP server connects to Claude Desktop
- ✅ Real Gmail + Calendar APIs integrated and functional
- ✅ Singapore government classifications applied to outputs
- ✅ NRIC/phone/email automatically redacted in responses
- ✅ Every API call logged with audit trail
- ✅ 2-3 demo scenarios executable in < 2 minutes each
- ✅ Ready for GovTech AI Assistant PM technical interview

---

### Phase 2: Complete Tool Suite & Data Mocking
**Goal:** Implement all 6 tools with realistic mock data

**Tasks:**
1. **Implement Remaining Tools**
   - `fetch_documents`: Google Drive API integration
   - `fetch_stakeholder_context`: Mock database (SQLite or JSON)
   - `search_policies`: Mock policy repository (structured JSON)
   - `generate_briefing`: Orchestration tool (calls other tools)

2. **Create Mock Data Sets**
   - **Stakeholders DB:** 10-15 fictional government officers with roles, interaction history
   - **Policy Repository:** 5-8 sample policies (procurement, HR, security, financial)
   - **Sample Documents:** Create realistic document titles, snippets, classifications
   - **Sample Emails/Calendar:** Seed real APIs with test data

3. **Tool Refinement**
   - Add input validation for all tools
   - Standardize output schemas across tools
   - Implement error responses with helpful messages

4. **Agentic Workflow Testing**
   - Test multi-tool workflows (e.g., calendar → stakeholder → briefing)
   - Verify Claude can chain tools autonomously
   - Identify and fix workflow bottlenecks

**Success Criteria:**
- All 6 tools functional and tested
- Claude can successfully execute multi-step agentic workflows
- Mock data is realistic and comprehensive enough for demos

---

### Phase 3: Trust & Safety Layer
**Goal:** Implement production-grade trust/safety controls

**Tasks:**
1. **Data Classification Engine**
   - Implement classification rules (keyword-based, metadata-based)
   - Add classification to all tool outputs
   - Create classification visualization (tags/labels)

2. **PII Redaction**
   - Implement regex-based PII detection (NRIC, phone, email)
   - Add redaction to email snippets, meeting descriptions
   - Track redaction status in tool outputs (`"redacted": true/false`)

3. **Access Control**
   - Define user roles and permissions matrix
   - Implement pre-tool access checks
   - Add "access denied" responses with clear explanations

4. **Audit Logging**
   - Create audit log schema (JSONL file or SQLite)
   - Log every tool invocation with sanitized inputs
   - Implement audit log viewer (simple CLI tool)

5. **Integration with Tools**
   - Wrap all tools with trust/safety middleware
   - Ensure classification/redaction happens before data returns to Claude
   - Add audit log IDs to all tool responses

**Success Criteria:**
- All data classified correctly based on rules
- PII automatically redacted in outputs
- Audit logs capture every tool invocation
- Access control prevents unauthorized data access

---

### Phase 4: Advanced Features & Polish
**Goal:** Add sophistication and demo-ready polish

**Tasks:**
1. **Enhanced Agentic Workflows**
   - Implement `generate_briefing` as a true orchestrator
     - Calls multiple tools based on context
     - Synthesizes results using LLM
     - Applies trust/safety to final output
   - Add workflow templates (meeting prep, decision memo, stakeholder brief)

2. **Cross-System Intelligence**
   - Implement relationship mapping (e.g., link emails to calendar events)
   - Add temporal awareness (prioritize recent info)
   - Create context scoring (rank sources by relevance)

3. **Trust/Safety Enhancements**
   - Add classification confidence scores
   - Implement manual override for classifications
   - Create classification explainability (why was this classified as X?)

4. **Performance Optimization**
   - Add caching for frequently accessed data
   - Implement parallel API calls where possible
   - Optimize for < 5 second end-to-end latency

5. **Demo Scenario Development**
   - Create 3-4 compelling demo scripts (meeting brief, policy search, multi-agency)
   - Prepare sample data that tells a coherent story
   - Build demo video showing problem → solution

**Success Criteria:**
- `generate_briefing` produces high-quality, cited briefings
- System feels responsive and intelligent
- Trust/safety features are visible and explainable
- Demo ready for technical interview

---

### Phase 5: Documentation & Presentation
**Goal:** Package the project for maximum impact

**Tasks:**
1. **Technical Documentation**
   - **README.md:**
     - Project overview and problem statement
     - Architecture diagram
     - Installation and setup instructions
     - Usage examples with screenshots
   - **ARCHITECTURE.md:**
     - Detailed system design
     - Tool specifications
     - Trust/safety implementation details
   - **API_REFERENCE.md:**
     - Tool schemas with examples
     - Error codes and handling
     - Integration patterns

2. **Design Documentation**
   - **DESIGN_DECISIONS.md:**
     - Why MCP for this problem?
     - Trade-offs in trust/safety implementation
     - Government-specific considerations
     - Scalability and extensibility
   - **TRUST_AND_SAFETY.md:**
     - Classification rationale
     - PII redaction approach
     - Audit logging philosophy
     - Compliance considerations (PDPA, etc.)

3. **Demo Materials**
   - **Demo Video (3-5 minutes):**
     - Problem: Officer juggling 5 systems manually
     - Solution: One conversation with AI Assistant + MCP
     - Trust/Safety: Show classification, redaction, audit log
     - Impact: Time saved, reduced errors
   - **Demo Script:**
     - 3-4 scenarios with prepared prompts
     - Expected outputs and key features to highlight
   - **Slide Deck (10-15 slides):**
     - Problem statement
     - Solution architecture
     - Key features
     - Trust/safety approach
     - Government applicability

4. **Code Quality**
   - Add type hints (Python) or TypeScript types
   - Write docstrings for all functions
   - Add unit tests for trust/safety functions
   - Clean up commented code, TODOs

5. **GitHub Polish**
   - Add LICENSE (MIT or Apache 2.0)
   - Create GitHub repo with clear folder structure
   - Add badges (Python version, license, status)
   - Write contributor guidelines (even if it's just you)

**Success Criteria:**
- Repo looks professional and well-documented
- Demo video clearly shows value proposition
- Documentation answers "why this matters for GovTech"
- Ready to share with hiring manager

---

## 7. Demo Scenarios

### Scenario 1: Meeting Preparation (Core Use Case)

**Context:**  
Officer has a 2pm meeting with Director John Tan about the updated Procurement Policy. Officer hasn't had time to review emails, documents, or prepare talking points.

**User Prompt:**  
_"Brief me for my 2pm meeting with John Tan about the new procurement policy"_

**Expected MCP Workflow:**
1. Fetch calendar → Find 2pm meeting details
2. Fetch stakeholder context → John Tan's background, preferences
3. Search policies → Procurement Policy 2024
4. Fetch emails → Recent correspondence with John
5. Fetch documents → Shared briefings on procurement
6. Generate briefing → Synthesized brief with citations

**Highlighted Features:**
- ✅ Multi-tool agentic orchestration
- ✅ Cross-system context aggregation
- ✅ Structured output with citations
- ✅ Classification (CONFIDENTIAL)
- ✅ Audit logging

**Impact Message:**  
_"What used to take 45 minutes of manual searching across systems now takes 30 seconds in one conversation."_

---

### Scenario 2: Policy Compliance Check

**Context:**  
Officer needs to verify if a proposed vendor contract complies with current procurement policies before approval.

**User Prompt:**  
_"Does the proposed contract with Acme Corp (value: $250k, duration: 2 years) comply with our procurement policy?"_

**Expected MCP Workflow:**
1. Search policies → Find procurement policy thresholds
2. Fetch documents → Retrieve Acme Corp contract draft
3. Generate analysis → Compare contract terms vs policy requirements
4. Flag compliance gaps or approvals needed

**Highlighted Features:**
- ✅ Policy search with structured outputs
- ✅ Compliance verification logic
- ✅ Risk flagging
- ✅ Clear recommendations

**Impact Message:**  
_"Reduces compliance errors and speeds up approval workflows by providing instant policy guidance."_

---

### Scenario 3: Multi-Agency Coordination

**Context:**  
Officer coordinating a joint healthcare financing project between MOH (Ministry of Health) and MOF (Ministry of Finance). Needs status update across both agencies.

**User Prompt:**  
_"What's the status of the healthcare financing project? I need updates from both MOH and MOF."_

**Expected MCP Workflow:**
1. Fetch emails → Filter correspondence from MOH and MOF contacts
2. Fetch documents → Search shared project folders for both agencies
3. Fetch calendar → Find past and upcoming cross-agency meetings
4. Generate status report → Synthesize current status, action items, blockers

**Highlighted Features:**
- ✅ Multi-organization context aggregation
- ✅ Relationship mapping (emails ↔ meetings ↔ documents)
- ✅ Highest classification applied (RESTRICTED for multi-agency)
- ✅ Gap identification (missing info from either agency)

**Impact Message:**  
_"Enables seamless cross-agency coordination without security compromises - proper classification and audit trails maintained."_

---

### Scenario 4: Trust & Safety Showcase

**Context:**  
Officer queries sensitive information that contains PII and confidential data. Demonstrate how trust/safety layer protects this.

**User Prompt:**  
_"What were the key discussion points from my meeting with Dr. Sarah Lee about the pilot program?"_

**Expected MCP Workflow:**
1. Fetch calendar → Find meeting with Dr. Sarah Lee
2. Fetch stakeholder context → Sarah's background (contains NRIC, phone in mock data)
3. Fetch meeting notes → Contains PII in notes
4. Apply redaction → NRIC, phone numbers redacted
5. Apply classification → RESTRICTED (meeting notes)
6. Generate summary → Sanitized output with proper classification

**Highlighted Features:**
- ✅ **PII Redaction:** Show `[NRIC REDACTED]`, `[PHONE REDACTED]` in outputs
- ✅ **Classification Tags:** `"classification": "RESTRICTED"` visible
- ✅ **Audit Log:** Show log entry with data accessed
- ✅ **Access Control:** Demonstrate "access denied" for lower-privilege user

**Impact Message:**  
_"Trust-by-design: Every piece of data is classified, PII is redacted, and all access is logged - building AI that government can trust."_

**Visual for Demo:**  
Show side-by-side comparison:
- **Left:** Raw data from API (contains PII, unclassified)
- **Right:** MCP output to Claude (redacted, classified, logged)

---

## 8. Technology Stack

### Core MCP Framework
- **Python Option:** FastMCP (`pip install fastmcp`)
  - Pros: Simpler, faster prototyping, great for data processing
  - Cons: Fewer examples in official docs
  
- **Node.js Option:** `@modelcontextprotocol/sdk`
  - Pros: Official SDK, more examples, better for SSE transport
  - Cons: More boilerplate, TypeScript overhead

**Recommendation:** Use **FastMCP (Python)** for this project - faster to build, easier to integrate with data processing libraries.

### External APIs
- **Gmail API:** `google-auth`, `google-api-python-client`
- **Google Drive API:** `google-auth`, `google-api-python-client`
- **Google Calendar API:** `google-auth`, `google-api-python-client`

### Data & Storage
- **Mock Database:** SQLite3 (built into Python)
- **Audit Logs:** JSONL file or SQLite table
- **Configuration:** Python-dotenv for environment variables

### Trust & Safety
- **PII Redaction:** Regex (built-in `re` module) or spaCy for advanced NER
- **Classification:** Custom rules engine (Python dicts + functions)
- **Access Control:** Simple role-based access control (RBAC) implementation

### Testing & Quality
- **Unit Tests:** pytest
- **MCP Testing:** Claude Desktop (manual)
- **Code Quality:** ruff (linter), black (formatter)

---

## 9. File Structure

```
crosscontext-mcp/
├── README.md                          # Project overview, installation, usage
├── ARCHITECTURE.md                    # This document
├── DESIGN_DECISIONS.md                # Why certain choices were made
├── TRUST_AND_SAFETY.md                # Trust/safety deep dive
├── requirements.txt                   # Python dependencies
├── .env.example                       # Example environment variables
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── server.py                      # Main MCP server entry point
│   ├── config.py                      # Configuration management
│   │
│   ├── tools/                         # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── fetch_emails.py
│   │   ├── fetch_documents.py
│   │   ├── fetch_calendar.py
│   │   ├── fetch_stakeholder_context.py
│   │   ├── search_policies.py
│   │   └── generate_briefing.py
│   │
│   ├── trust_safety/                  # Trust & safety layer
│   │   ├── __init__.py
│   │   ├── classifier.py              # Data classification engine
│   │   ├── redactor.py                # PII redaction
│   │   ├── access_control.py          # Access control checks
│   │   └── audit_logger.py            # Audit logging
│   │
│   ├── integrations/                  # External API integrations
│   │   ├── __init__.py
│   │   ├── gmail_client.py
│   │   ├── gdrive_client.py
│   │   ├── calendar_client.py
│   │   └── mock_db.py                 # Mock government systems
│   │
│   └── utils/                         # Shared utilities
│       ├── __init__.py
│       ├── schemas.py                 # Pydantic models for tool I/O
│       └── helpers.py                 # Common helper functions
│
├── data/                              # Mock data and policies
│   ├── stakeholders.json              # Fictional government officers
│   ├── policies.json                  # Sample policies
│   └── audit_logs/                    # Audit log storage
│       └── .gitkeep
│
├── tests/                             # Unit tests
│   ├── __init__.py
│   ├── test_classifier.py
│   ├── test_redactor.py
│   ├── test_access_control.py
│   └── test_tools.py
│
├── docs/                              # Additional documentation
│   ├── API_REFERENCE.md
│   ├── DEMO_SCRIPT.md
│   └── diagrams/
│       └── architecture.png
│
└── demo/                              # Demo materials
    ├── demo_video.mp4
    ├── demo_slides.pdf
    └── sample_prompts.md
```

---

## 10. Key Talking Points for Interview

### 1. Why MCP for This Problem?
_"MCP solves the integration problem that plagues government systems. Instead of building N custom integrations for each AI product, MCP creates a universal context layer. One MCP server can serve multiple AI assistants, multiple agencies, multiple use cases. It's the API gateway for the AI era."_

### 2. Trust & Safety From Day One
_"In government, trust isn't optional - it's foundational. I built classification, redaction, and audit logging as core features, not afterthoughts. Every piece of data is tagged with sensitivity, every access is logged, every PII is redacted. This isn't just compliance - it's building AI that public officers can confidently use for critical work."_

### 3. Agentic Workflows in Practice
_"The power of agentic AI isn't just tool use - it's autonomous decision-making. When an officer asks for a meeting brief, the AI doesn't just fetch one data source. It reasons: 'I need the meeting details, so calendar first. Now I know the attendees, so stakeholder context. They mentioned procurement, so policy search.' That multi-step reasoning is what makes AI assistants truly effortless."_

### 4. Government Context Matters
_"I didn't build a generic todo app or weather tool. I built something that speaks to real operational fragmentation in government: juggling emails, policies, stakeholder databases, calendars. The stakeholder context tool, for example, shows I understand public officers need org chart context, interaction history, communication preferences - not just contact info."_

### 5. Scalability & Extensibility
_"This MCP is designed to scale. Add a new agency system? Just write one new tool. Need a new workflow? The agentic coordinator handles it. The trust/safety layer is pluggable - swap classification rules per agency without touching core logic. That's production thinking, not prototype thinking."_

### 6. What I'd Do Next
_"If I were to take this to production: (1) Replace mock data with real LDAP/Active Directory integration, (2) Add federated authentication (SingPass), (3) Implement differential privacy for analytics, (4) Build a monitoring dashboard for audit logs and classification accuracy. But the architecture is already production-ready."_

---

## 11. Success Metrics for This Project

### Technical Metrics
- ✅ All 6 tools functional with < 5 second latency
- ✅ 100% of outputs classified correctly based on rules
- ✅ 100% of PII redacted in test cases
- ✅ Every tool invocation logged with no gaps

### Demo Metrics
- ✅ 3-4 compelling scenarios scripted and tested
- ✅ Demo video < 5 minutes, high production quality
- ✅ Live demo executable in < 10 minutes

### Documentation Metrics
- ✅ README includes clear problem statement and value prop
- ✅ Architecture doc explains "why" not just "what"
- ✅ All code has docstrings and type hints
- ✅ Design decisions doc addresses government constraints

### Interview Impact
- ✅ Demonstrates deep understanding of GovTech's AI Assistant goals
- ✅ Shows technical fluency in MCP, LLMs, and agentic workflows
- ✅ Proves trust/safety is not just theory but implementation
- ✅ Positions you as someone who thinks end-to-end (discovery → production)

---

## 12. Risk Mitigation

### Risk 1: MCP Complexity Overwhelms Timeline
**Mitigation:** Start with 2-3 simple tools in Phase 1. If short on time, skip Phase 4 (advanced features) and focus on a polished demo of Phases 1-3.

### Risk 2: Real API Integration Issues
**Mitigation:** Mock everything that's not Gmail/Calendar. Don't let API auth headaches derail the project. The architecture matters more than live APIs.

### Risk 3: Trust/Safety Overengineering
**Mitigation:** Start with simple regex-based redaction and keyword-based classification. Advanced NLP can come later. Good enough > perfect.

### Risk 4: Demo Doesn't Resonate
**Mitigation:** Test your demo script with a friend or colleague. Get feedback on clarity and impact. Iterate until the value proposition is obvious in 30 seconds.
