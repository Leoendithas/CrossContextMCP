# CrossContext MCP: Government Officer Context Engine

A Model Context Protocol (MCP) server that provides AI assistants with unified access to government officer's context including emails, calendar, policies, and stakeholder information with built-in trust/safety controls.

## Features

- **Multi-Source Context Aggregation**: Fetch emails, calendar events, documents, and stakeholder info
- **Singapore Government Classification**: CONFIDENTIAL CLOUD-ELIGIBLE, RESTRICTED, OFFICIAL compliance
- **PII Redaction**: Automatic detection and redaction of NRIC, phone numbers, emails
- **Audit Logging**: Complete audit trail for all data access
- **Real API Integration**: Gmail and Google Calendar API integration

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to project
cd crosscontext-mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download credentials JSON file

### 3. Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your Google API credentials
# GOOGLE_CLIENT_ID=your_client_id
# GOOGLE_CLIENT_SECRET=your_client_secret
# GOOGLE_PROJECT_ID=your_project_id
```

### 4. Run OAuth Flow

```bash
# Run the server once to generate OAuth tokens
python src/server.py
# Follow browser prompts to authorize access
```

### 5. Claude Desktop Integration

The MCP server is already configured in Claude Desktop. Restart Claude Desktop to load the new server.

## Available Tools

- `echo_tool`: Test connection
- `fetch_emails`: Search and retrieve emails with classification
- `fetch_calendar`: Get calendar events with PII redaction

## Demo Scenarios

1. **Meeting Preparation**: "Brief me for my 2pm meeting with John Tan about procurement policy"
2. **Email Search**: "Find recent emails about budget approvals"
3. **Calendar Review**: "What meetings do I have today?"

## Trust & Safety

- **Data Classification**: All data tagged with Singapore government security levels
- **PII Redaction**: Automatic detection of sensitive information
- **Access Control**: Role-based permissions (officer/manager/admin)
- **Audit Logging**: Complete trail of all data access with timestamps

## Architecture

```
Claude Desktop → MCP Protocol → CrossContext Server → Trust/Safety Layer → Google APIs
```

## Development

```bash
# Run tests
python test_server.py

# Run server directly
python src/server.py

# Check logs
tail -f audit_log.jsonl
```

## Security Classifications (Singapore Government)

- **CONFIDENTIAL CLOUD-ELIGIBLE**: Budget, procurement data
- **RESTRICTED**: Disciplinary, investigation data
- **OFFICIAL (CLOSED)**: Sensitive internal communications
- **OFFICIAL (OPEN)**: Public information

## License

MIT
