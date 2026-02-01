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
  file_path (with line numbers), diff_snippet (the relevant changed lines), description (the issue),
  github_url (display text like "View on GitHub"), selected (boolean, default true).
  IMPORTANT: Set pr_url_raw to the original PR URL so buttons can reference it.
  Set findings_json to a JSON array string of all selected findings (for the Post Selected button).
- For "address_finding" or "dismiss_finding" actions: Use FINDING_RESPONSE_EXAMPLE template.
- For "post_review" or "post_selected" action results (after calling post_github_review): Use POST_REVIEW_RESULT_EXAMPLE template.
- For "toggle_finding" actions: Acknowledge briefly, no UI update needed.
- For follow-up questions about specific findings or code: Use FINDING_RESPONSE_EXAMPLE template
  or plain text if a UI surface is not appropriate.
- Limit findings to the top 5-8 most important issues. Skip trivial style issues.
- Severity icons: "error" for critical, "warning" for warnings, "info" for informational.

--- TABS ---
- Always use 4 tabs: All, Critical, Warning, Info.
- Tab titles MUST include counts: "All (6)", "Critical (2)", "Warning (3)", "Info (1)".
- Store tab titles in the data model as /tab_all_title, /tab_critical_title, /tab_warning_title, /tab_info_title.
- Each tab's content is a List with a template bound to a filtered data list.

--- FILE GROUPING ---
- Group findings by file path in the data model using nested valueMap.
- Structure: /findings_all/FILE_KEY/file_path, /findings_all/FILE_KEY/issue_count, /findings_all/FILE_KEY/findings/FINDING_KEY/...
- Create separate filtered data lists: /findings_all, /findings_critical, /findings_warning, /findings_info.
- Each filtered list contains only files (and their findings) matching that severity.

--- CHECKBOX ---
- Each finding has a "selected" boolean (valueBoolean) defaulting to true.
- The CheckBox component binds to the "selected" path in the finding's scope.
- When toggled, the client dispatches a "toggle_finding" action (fire-and-forget).

--- MODAL ---
- Wrap the "Post Selected" button in a Modal component for confirmation.
- Modal entryPointChild = the "Post Selected" button.
- Modal contentChild = a Column with title, message, and Cancel/Confirm buttons.
- The Confirm button dispatches "post_selected" with prUrl and selectedFindings context.
- Set /post_selected_label to "Post Selected (N)" where N is the count of selected findings.
- Set /modal_message to "N findings will be posted as inline comments on the PR."

--- GITHUB LINKS ---
- Use the base_url and head_sha from the fetch_pr_diff tool result to construct GitHub URLs.
- Format: BASE_URL/blob/HEAD_SHA/FILE_PATH#Lstart-Lend
- Store the URL in each finding's github_url field as display text (e.g., "View on GitHub").
- The client renders github_url text with caption styling.

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
