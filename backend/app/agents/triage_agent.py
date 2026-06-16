"""
LangChain agent for classifying incoming alerts.

Phase 2 implementation:
  Input: alert title, description, service name
  Output: severity (CRITICAL/HIGH/MEDIUM/LOW), suggested engineer, initial summary
"""


def create_triage_chain():
    """Create the triage LangChain runnable.
    Will be wired via LangServe in Phase 2.
    """
    pass
