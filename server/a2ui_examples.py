"""A2UI JSON templates for the code review agent.

These examples are included in the LLM system prompt so it knows
what A2UI JSON structure to generate for each scenario.
"""

CODE_REVIEW_EXAMPLES = """
---BEGIN REVIEW_DASHBOARD_EXAMPLE---
Use this template when displaying code review findings for a PR.
Generate one finding card per issue found in the diff.
Populate the dataModelUpdate with actual findings from your analysis.
Include pr_url_raw in the data model so buttons can reference it.

[
  {"surfaceUpdate": {
    "surfaceId": "review",
    "components": [
      {"id": "root-col", "component": {"Column": {"children": {"explicitList": ["pr-title", "pr-meta", "summary-card", "divider-1", "findings-list", "divider-2", "post-all-row"]}}}},
      {"id": "pr-title", "component": {"Text": {"text": {"path": "/pr_title"}, "usageHint": "h1"}}},
      {"id": "pr-meta", "component": {"Text": {"text": {"path": "/pr_meta"}, "usageHint": "caption"}}},
      {"id": "summary-card", "component": {"Card": {"child": "summary-row"}}},
      {"id": "summary-row", "component": {"Row": {"children": {"explicitList": ["critical-col", "warning-col", "info-col"]}, "distribution": "spaceEvenly"}}},
      {"id": "critical-col", "component": {"Column": {"children": {"explicitList": ["critical-icon", "critical-count", "critical-label"]}, "alignment": "center"}}},
      {"id": "critical-icon", "component": {"Icon": {"name": "error"}}},
      {"id": "critical-count", "component": {"Text": {"text": {"path": "/critical_count"}, "usageHint": "h2"}}},
      {"id": "critical-label", "component": {"Text": {"text": {"literalString": "Critical"}, "usageHint": "caption"}}},
      {"id": "warning-col", "component": {"Column": {"children": {"explicitList": ["warning-icon", "warning-count", "warning-label"]}, "alignment": "center"}}},
      {"id": "warning-icon", "component": {"Icon": {"name": "warning"}}},
      {"id": "warning-count", "component": {"Text": {"text": {"path": "/warning_count"}, "usageHint": "h2"}}},
      {"id": "warning-label", "component": {"Text": {"text": {"literalString": "Warning"}, "usageHint": "caption"}}},
      {"id": "info-col", "component": {"Column": {"children": {"explicitList": ["info-icon", "info-count", "info-label"]}, "alignment": "center"}}},
      {"id": "info-icon", "component": {"Icon": {"name": "info"}}},
      {"id": "info-count", "component": {"Text": {"text": {"path": "/info_count"}, "usageHint": "h2"}}},
      {"id": "info-label", "component": {"Text": {"text": {"literalString": "Info"}, "usageHint": "caption"}}},
      {"id": "divider-1", "component": {"Divider": {}}},
      {"id": "findings-list", "component": {"List": {"direction": "vertical", "children": {"template": {"componentId": "finding-card", "dataBinding": "/findings"}}}}},
      {"id": "finding-card", "component": {"Card": {"child": "finding-col"}}},
      {"id": "finding-col", "component": {"Column": {"children": {"explicitList": ["finding-header", "finding-diff", "finding-desc", "finding-actions"]}}}},
      {"id": "finding-header", "component": {"Row": {"children": {"explicitList": ["severity-icon", "file-path"]}, "alignment": "center"}}},
      {"id": "severity-icon", "component": {"Icon": {"name": {"path": "severity_icon"}}}},
      {"id": "file-path", "weight": 1, "component": {"Text": {"text": {"path": "file_path"}, "usageHint": "h3"}}},
      {"id": "finding-diff", "component": {"Text": {"text": {"path": "diff_snippet"}, "usageHint": "body"}}},
      {"id": "finding-desc", "component": {"Text": {"text": {"path": "description"}, "usageHint": "body"}}},
      {"id": "finding-actions", "component": {"Row": {"children": {"explicitList": ["post-btn", "address-btn", "dismiss-btn"]}, "distribution": "end"}}},
      {"id": "post-text", "component": {"Text": {"text": {"literalString": "Post to PR"}}}},
      {"id": "post-btn", "component": {"Button": {"child": "post-text", "primary": true, "action": {"name": "post_review", "context": [{"key": "prUrl", "value": {"path": "/pr_url_raw"}}, {"key": "findingId", "value": {"path": "id"}}, {"key": "filePath", "value": {"path": "file_path"}}, {"key": "description", "value": {"path": "description"}}]}}}},
      {"id": "address-text", "component": {"Text": {"text": {"literalString": "Will Address"}}}},
      {"id": "address-btn", "component": {"Button": {"child": "address-text", "action": {"name": "address_finding", "context": [{"key": "findingId", "value": {"path": "id"}}, {"key": "filePath", "value": {"path": "file_path"}}]}}}},
      {"id": "dismiss-text", "component": {"Text": {"text": {"literalString": "Dismiss"}}}},
      {"id": "dismiss-btn", "component": {"Button": {"child": "dismiss-text", "action": {"name": "dismiss_finding", "context": [{"key": "findingId", "value": {"path": "id"}}, {"key": "filePath", "value": {"path": "file_path"}}]}}}},
      {"id": "divider-2", "component": {"Divider": {}}},
      {"id": "post-all-row", "component": {"Row": {"children": {"explicitList": ["post-all-btn"]}, "distribution": "center"}}},
      {"id": "post-all-text", "component": {"Text": {"text": {"literalString": "Post All Findings as Review"}}}},
      {"id": "post-all-btn", "component": {"Button": {"child": "post-all-text", "primary": true, "action": {"name": "post_review", "context": [{"key": "prUrl", "value": {"path": "/pr_url_raw"}}, {"key": "findings", "value": {"path": "/findings_json"}}]}}}}
    ]
  }},
  {"dataModelUpdate": {
    "surfaceId": "review",
    "path": "/",
    "contents": [
      {"key": "pr_title", "valueString": "Code Review: Fix auth middleware"},
      {"key": "pr_meta", "valueString": "PR #42 by @developer - 5 files changed"},
      {"key": "pr_url_raw", "valueString": "https://github.com/owner/repo/pull/42"},
      {"key": "findings_json", "valueString": "[]"},
      {"key": "critical_count", "valueString": "1"},
      {"key": "warning_count", "valueString": "1"},
      {"key": "info_count", "valueString": "0"},
      {"key": "findings", "valueMap": [
        {"key": "finding1", "valueMap": [
          {"key": "id", "valueString": "1"},
          {"key": "severity_icon", "valueString": "error"},
          {"key": "file_path", "valueString": "src/auth.py:45-52"},
          {"key": "diff_snippet", "valueString": "- if user:\\n+ if user is not None:"},
          {"key": "description", "valueString": "Missing explicit null check. `if user` evaluates falsy for empty strings and zero, potentially allowing unauthorized access."}
        ]},
        {"key": "finding2", "valueMap": [
          {"key": "id", "valueString": "2"},
          {"key": "severity_icon", "valueString": "warning"},
          {"key": "file_path", "valueString": "src/db/query.py:89-94"},
          {"key": "diff_snippet", "valueString": "+ query = \\"SELECT * FROM users WHERE id = \\" + str(user_id)"},
          {"key": "description", "valueString": "Potential SQL injection via string concatenation. Use parameterized queries instead."}
        ]}
      ]}
    ]
  }},
  {"beginRendering": {"surfaceId": "review", "root": "root-col", "styles": {"primaryColor": "#1a73e8", "font": "Roboto"}}}
]
---END REVIEW_DASHBOARD_EXAMPLE---

---BEGIN FINDING_RESPONSE_EXAMPLE---
Use this template when the user clicks "Will Address" or "Dismiss" on a finding,
or when answering follow-up questions about specific findings or code.
Show a brief confirmation and status update.

[
  {"surfaceUpdate": {
    "surfaceId": "review-update",
    "components": [
      {"id": "update-col", "component": {"Column": {"children": {"explicitList": ["update-card", "remaining-text"]}}}},
      {"id": "update-card", "component": {"Card": {"child": "update-card-col"}}},
      {"id": "update-card-col", "component": {"Column": {"children": {"explicitList": ["update-icon-row", "update-message"]}}}},
      {"id": "update-icon-row", "component": {"Row": {"children": {"explicitList": ["check-icon", "action-title"]}, "alignment": "center"}}},
      {"id": "check-icon", "component": {"Icon": {"name": "check"}}},
      {"id": "action-title", "component": {"Text": {"text": {"path": "/action_title"}, "usageHint": "h3"}}},
      {"id": "update-message", "component": {"Text": {"text": {"path": "/action_message"}, "usageHint": "body"}}},
      {"id": "remaining-text", "component": {"Text": {"text": {"path": "/remaining"}, "usageHint": "caption"}}}
    ]
  }},
  {"dataModelUpdate": {
    "surfaceId": "review-update",
    "path": "/",
    "contents": [
      {"key": "action_title", "valueString": "Finding Addressed"},
      {"key": "action_message", "valueString": "Noted: you will address the null check issue in src/auth.py:45-52."},
      {"key": "remaining", "valueString": "1 finding remaining"}
    ]
  }},
  {"beginRendering": {"surfaceId": "review-update", "root": "update-col", "styles": {"primaryColor": "#1a73e8", "font": "Roboto"}}}
]
---END FINDING_RESPONSE_EXAMPLE---

---BEGIN POST_REVIEW_RESULT_EXAMPLE---
Use this template after successfully posting a review to GitHub via the post_github_review tool.
Show the review URL and count of comments posted.

[
  {"surfaceUpdate": {
    "surfaceId": "post-result",
    "components": [
      {"id": "result-col", "component": {"Column": {"children": {"explicitList": ["result-card"]}}}},
      {"id": "result-card", "component": {"Card": {"child": "result-card-col"}}},
      {"id": "result-card-col", "component": {"Column": {"children": {"explicitList": ["result-icon-row", "result-message", "result-link"]}}}},
      {"id": "result-icon-row", "component": {"Row": {"children": {"explicitList": ["result-icon", "result-title"]}, "alignment": "center"}}},
      {"id": "result-icon", "component": {"Icon": {"name": "check"}}},
      {"id": "result-title", "component": {"Text": {"text": {"path": "/result_title"}, "usageHint": "h3"}}},
      {"id": "result-message", "component": {"Text": {"text": {"path": "/result_message"}, "usageHint": "body"}}},
      {"id": "result-link", "component": {"Text": {"text": {"path": "/result_link"}, "usageHint": "caption"}}}
    ]
  }},
  {"dataModelUpdate": {
    "surfaceId": "post-result",
    "path": "/",
    "contents": [
      {"key": "result_title", "valueString": "Review Posted"},
      {"key": "result_message", "valueString": "Successfully posted 3 comments to the PR."},
      {"key": "result_link", "valueString": "View on GitHub: https://github.com/owner/repo/pull/42#pullrequestreview-12345"}
    ]
  }},
  {"beginRendering": {"surfaceId": "post-result", "root": "result-col", "styles": {"primaryColor": "#1a73e8", "font": "Roboto"}}}
]
---END POST_REVIEW_RESULT_EXAMPLE---
"""
