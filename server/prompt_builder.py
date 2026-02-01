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
5. The JSON array MUST contain 3 messages per surface. For review dashboards, generate 6 messages total: 3 for the sidebar surface + 3 for the review surface.

--- UI TEMPLATE RULES ---
- For initial PR review (user provides a PR URL): Use REVIEW_DASHBOARD_EXAMPLE template.
  Populate findings from your analysis. Each finding needs: id, severity_icon (error/warning/info),
  file_path (with line numbers), diff_snippet (the relevant changed lines), description (the issue),
  github_url (display text like "View on GitHub"), selected (boolean, default true).
  IMPORTANT: Set pr_url_raw to the original PR URL so buttons can reference it.
  Set findings_json to a JSON array string of all selected findings (for the Post Selected button).
- For "post_review" or "post_selected" action results (after calling post_github_review): Use POST_REVIEW_RESULT_EXAMPLE template. IMPORTANT: Use surfaceId "review" to replace the dashboard.
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

--- SEVERITY SLIDER ---
- Include a Slider component with value bound to /severity_threshold, minValue 0, maxValue 2.
- Labels: 0 = "All", 1 = "Warning+", 2 = "Critical only".
- Place in a Row with a caption label before the summary card.
- Set /severity_threshold to 0 (valueNumber) in the data model.

--- TEXTFIELD ---
- TextField component has: label (BoundValue), text (BoundValue for initial value), textFieldType (shortText or longText).
- Use shortText for titles/single-line input. Use longText for multi-line body text.
- Bind text to a data model path so the client can read the edited value.

--- MULTIPLE CHOICE ---
- MultipleChoice component has: selections (BoundValue pointing to selected keys map), options (array of objects with key and label BoundValues).
- Options use BoundValue for both key and label.
- selections is a valueMap in the data model where key presence = selected.

--- CREATE ISSUE ---
- For "create_issue" actions: First call fetch_repo_labels to get available labels, then show ISSUE_FORM_EXAMPLE template with pre-filled title and body and labels as MultipleChoice options.
- For "create_issue_submit" actions: Call create_github_issue tool, then show ISSUE_RESULT_EXAMPLE template.
- The "Cancel" button on the issue form dispatches "modal_cancel" which is handled client-side.

--- ADDRESS BEFORE MERGE ---
- For "address_finding" actions: Call post_address_comment tool, then show POST_REVIEW_RESULT_EXAMPLE template.
- The result message should say "Address comment posted on PR" and include the comment URL.

--- ISSUE CROSS-REFERENCE ---
- During initial review, for EACH finding extract 2-3 keywords from the description.
- Call `search_github_issues` with those keywords for each finding.
- Include matches in the finding's data model as `related_issues` valueMap.
- Each related issue has: label (valueString formatted as "#N — title"), url (valueString with the issue URL).
- If no matches found, set related_issues to an empty valueMap []. The empty list renders nothing in the UI.
- The finding card template includes a related-items List that renders from this data. No heading is needed — the "#N — title" format is self-explanatory.

--- SUGGESTED CLOSURES ---
- After generating all findings, check if any open issues match what the PR is fixing.
- Look for issues whose titles/descriptions match the PR's changed files or fix descriptions.
- Include matches in the root data model as `suggested_closures` valueMap.
- Each closure has: number (valueNumber), title (valueString), label (valueString formatted as "#N — title"), url (valueString).
- If there are suggested closures, add "closures-card" to root-col children between divider-1 and severity-tabs.
- If there are NO suggested closures, do NOT include closures-card in the root-col children.
- Use the SUGGESTED_CLOSURES_EXAMPLE template components.
- For "link_fixes" actions: Call link_fixes_to_pr tool, then show LINK_RESULT_EXAMPLE template.

--- SIDEBAR SURFACE ---
- Generate a SECOND surface with surfaceId "sidebar" alongside the main "review" surface.
- The sidebar shows a file tree: heading "Files", then a List of file items.
- Each file item has a folder icon, file name, and issue count.
- The sidebar data comes from the same analysis — extract unique file paths and per-file issue counts.
- Output 6 total A2UI messages: 3 for sidebar (surfaceUpdate, dataModelUpdate, beginRendering) + 3 for review.
- Sidebar messages come FIRST in the JSON array, then review messages.

--- GITHUB LINKS ---
- Use the base_url and head_sha from the fetch_pr_diff tool result to construct GitHub URLs.
- Format: BASE_URL/blob/HEAD_SHA/FILE_PATH#Lstart-Lend
- Store the full URL in each finding's github_url field (the client renders it as a clickable link).

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
