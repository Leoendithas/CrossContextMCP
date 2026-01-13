"""
Singapore Government Data Classification Engine
Based on Singapore Government Classification System
"""

CLASSIFICATION_RULES = {
    "CONFIDENTIAL CLOUD-ELIGIBLE": {
        "keywords": ["budget", "procurement", "tender", "contract", "salary", "financial"],
        "domains": ["vendor.com", "supplier.com", "contractor.gov.sg"],
    },
    "RESTRICTED": {
        "keywords": ["nric", "disciplinary", "investigation", "medical", "personal"],
        "domains": ["external-contractor.com", "medical.gov.sg"],
    },
    "OFFICIAL (CLOSED)": {
        "keywords": ["internal", "draft", "review", "confidential", "restricted"],
        "domains": [],  # Default for .gov.sg internal communications
    },
    "OFFICIAL (OPEN)": {
        "keywords": [],  # Fallback for public information
        "domains": [],
    },
}

def classify_data(content: dict) -> dict:
    """
    Apply Singapore government classification to data content with explanations.

    Args:
        content: Dictionary containing data to classify (email, calendar event, etc.)

    Returns:
        Content dict with 'classification', 'classification_reason', and 'classification_rules_triggered' fields added
    """
    # Convert content to searchable text
    text = str(content).lower()
    triggered_rules = []

    # Check for sensitive classifications first (highest precedence)
    for level in ["CONFIDENTIAL CLOUD-ELIGIBLE", "RESTRICTED", "OFFICIAL (CLOSED)"]:
        rules = CLASSIFICATION_RULES[level]
        level_triggered = False

        # Check keywords
        matched_keywords = [kw for kw in rules["keywords"] if kw in text]
        if matched_keywords:
            triggered_rules.extend(matched_keywords)
            level_triggered = True

        # Check domains (for emails)
        if "from" in content:
            sender_domain = content["from"].split("@")[-1] if "@" in content["from"] else ""
            if sender_domain in rules["domains"]:
                triggered_rules.append(f"sender_domain:{sender_domain}")
                level_triggered = True

        if level_triggered:
            content["classification"] = level
            content["classification_reason"] = get_classification_reason(level, triggered_rules)
            content["classification_rules_triggered"] = triggered_rules
            return content

    # Default to public
    content["classification"] = "OFFICIAL (OPEN)"
    content["classification_reason"] = "No sensitive keywords or restricted domains detected"
    content["classification_rules_triggered"] = []
    return content

def get_classification_reason(level: str, triggered_rules: list) -> str:
    """
    Generate human-readable explanation for classification.

    Args:
        level: Classification level
        triggered_rules: List of rules that triggered this classification

    Returns:
        Human-readable explanation
    """
    reasons = {
        "CONFIDENTIAL CLOUD-ELIGIBLE": "Contains sensitive financial or procurement data",
        "RESTRICTED": "Contains personal data, disciplinary matters, or medical information",
        "OFFICIAL (CLOSED)": "Contains internal communications or draft materials",
        "OFFICIAL (OPEN)": "Public information with no sensitivity markers"
    }

    base_reason = reasons.get(level, "Default classification")

    if triggered_rules:
        rule_descriptions = []
        for rule in triggered_rules:
            if ":" in rule:
                rule_type, rule_value = rule.split(":", 1)
                if rule_type == "sender_domain":
                    rule_descriptions.append(f"external sender ({rule_value})")
            else:
                rule_descriptions.append(f"keyword '{rule}'")

        if rule_descriptions:
            base_reason += f" (triggered by: {', '.join(rule_descriptions)})"

    return base_reason
