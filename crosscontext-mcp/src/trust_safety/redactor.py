"""
PII Redaction Engine for Singapore Government Data
Redacts NRIC, phone numbers, email addresses, and other sensitive information
"""

import re

# Singapore-specific PII patterns
PII_PATTERNS = {
    "nric": r'\b[STFG]\d{7}[A-Z]\b',  # Singapore NRIC format
    "phone": r'\b(?:\+?65[-\s]?)?[689]\d{7}\b',  # Singapore phone numbers
    "email": r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    "postal_code": r'\b\d{6}\b',  # Singapore postal codes (6 digits)
}

def redact_pii(content: dict, context: str = "general") -> dict:
    """
    Redact personally identifiable information from content with smart context-aware logic.

    Args:
        content: Dictionary containing text content to redact
        context: Context for smart redaction decisions ("meeting_participant", "general", etc.)

    Returns:
        Content dict with PII redacted, redaction tracking, and metadata
    """
    redacted = False
    content_copy = content.copy()
    redaction_log = []

    # Redact PII in all string fields
    for key, value in content_copy.items():
        if isinstance(value, str):
            original_value = value
            redacted_value = value

            # Apply smart redaction based on context
            for pii_type, pattern in PII_PATTERNS.items():
                matches = re.findall(pattern, redacted_value)
                if matches:
                    for match in matches:
                        # Smart redaction decisions
                        should_redact = should_redact_pii(match, pii_type, key, context, content)

                        if should_redact:
                            placeholder = f'[REDACTED {pii_type.upper()}]'
                            redacted_value = redacted_value.replace(match, placeholder, 1)

                            redaction_log.append({
                                "field": key,
                                "pii_type": pii_type,
                                "redacted_value": placeholder,
                                "reason": get_redaction_reason(pii_type, context)
                            })
                            redacted = True

            # Update the field if redaction occurred
            if redacted_value != original_value:
                content_copy[key] = redacted_value

    # Add redaction metadata
    content_copy["redacted"] = redacted
    if redaction_log:
        content_copy["redaction_log"] = redaction_log

    return content_copy

def should_redact_pii(match: str, pii_type: str, field: str, context: str, full_content: dict) -> bool:
    """
    Determine if PII should be redacted based on smart context-aware rules.

    Args:
        match: The PII match found
        pii_type: Type of PII (email, phone, nric)
        field: Field where PII was found
        context: Usage context
        full_content: Full content dictionary

    Returns:
        True if PII should be redacted
    """
    # Always redact NRIC regardless of context (most sensitive)
    if pii_type == "nric":
        return True

    # Always redact phone numbers (privacy protection)
    if pii_type == "phone":
        return True

    # Smart email redaction
    if pii_type == "email":
        # Don't redact meeting participants' emails (users need to contact them)
        if context == "meeting_participant" or field == "attendees":
            return False

        # Don't redact user's own email
        if field == "to" and "you@agency.gov.sg" in str(full_content.get("to", [])):
            return False

        # Redact external emails in general communications
        if "@" in match and not match.endswith("@agency.gov.sg"):
            return True

    # Always redact postal codes for privacy
    if pii_type == "postal_code":
        return True

    return False

def get_redaction_reason(pii_type: str, context: str) -> str:
    """
    Get human-readable reason for PII redaction.

    Args:
        pii_type: Type of PII redacted
        context: Usage context

    Returns:
        Explanation of why redaction was applied
    """
    reasons = {
        "nric": "Singapore National Registration Identity Card number (highly sensitive)",
        "phone": "Personal phone number (privacy protection)",
        "email": "Email address (privacy protection for non-meeting participants)",
        "postal_code": "Residential postal code (location privacy)"
    }

    return reasons.get(pii_type, "Personal identifiable information protection")

def contains_pii(text: str) -> bool:
    """
    Check if text contains any PII patterns.

    Args:
        text: Text to check for PII

    Returns:
        True if PII patterns are found
    """
    for pattern in PII_PATTERNS.values():
        if re.search(pattern, text):
            return True
    return False
