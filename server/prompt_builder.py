"""Builds the system prompt for the code review agent.

Combines agent instructions, A2UI schema, and UI examples
into the system prompt that tells the LLM how to respond.
"""

from a2ui_schema import A2UI_SCHEMA
from a2ui_examples import CODE_REVIEW_EXAMPLES


def get_ui_prompt() -> str:
    """Returns the full system prompt for the UI-enabled agent."""
    return f"""
To generate the response, you MUST follow these rules:
1. Your response MUST be in two parts, separated by the delimiter: `---a2ui_JSON---`
2. The first part is your brief conversational summary of findings.
3. The second part is a single, raw JSON array of A2UI messages (no markdown fences).
4. The JSON part MUST validate against the A2UI JSON SCHEMA provided below.
5. The JSON array MUST contain exactly 3 messages: surfaceUpdate, dataModelUpdate, beginRendering.

--- UI TEMPLATE RULES ---
- For initial PR review (user provides a PR URL): Use REVIEW_DASHBOARD_EXAMPLE template.
  Populate findings from your analysis. Each finding needs: id, severity_icon (error/warning/info),
  file_path (with line numbers), diff_snippet (the relevant changed lines), description (the issue).
  IMPORTANT: Set pr_url_raw to the original PR URL so buttons can reference it.
  Set findings_json to a JSON array string of all findings (for the Post All button).
- For "address_finding" or "dismiss_finding" actions: Use FINDING_RESPONSE_EXAMPLE template.
- For "post_review" action results (after calling post_github_review): Use POST_REVIEW_RESULT_EXAMPLE template.
- For follow-up questions about specific findings or code: Use FINDING_RESPONSE_EXAMPLE template
  or plain text if a UI surface is not appropriate.
- Limit findings to the top 5-8 most important issues. Skip trivial style issues.
- Severity icons: "error" for critical, "warning" for warnings, "info" for informational.

{CODE_REVIEW_EXAMPLES}

---BEGIN A2UI JSON SCHEMA---
{A2UI_SCHEMA}
---END A2UI JSON SCHEMA---
"""


def get_text_prompt() -> str:
    """Returns the system prompt for the text-only agent (no UI)."""
    return (
        "You are a code review assistant. Analyze GitHub PR diffs and "
        "report your findings as structured plain text with severity levels."
    )
