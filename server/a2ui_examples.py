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

Key features:
- Tabs for filtering by severity (All / Critical / Warning / Info) with counts in titles
- Findings grouped by file with a file header card
- CheckBox on each finding for selective posting
- Modal confirmation before posting selected findings
- GitHub links on each finding pointing to the exact file/lines
- Data model uses nested /files/FILE_KEY/findings/FINDING_KEY structure
- Separate filtered lists: /findings_all, /findings_critical, /findings_warning, /findings_info
  each containing the same nested file > findings structure but filtered by severity

[
  {"surfaceUpdate": {
    "surfaceId": "review",
    "components": [
      {"id": "root-col", "component": {"Column": {"children": {"explicitList": ["pr-title", "pr-meta", "summary-card", "divider-1", "severity-tabs", "divider-2", "post-modal"]}}}},
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

      {"id": "severity-tabs", "component": {"Tabs": {"tabItems": [
        {"title": {"path": "/tab_all_title"}, "child": "tab-all-content"},
        {"title": {"path": "/tab_critical_title"}, "child": "tab-critical-content"},
        {"title": {"path": "/tab_warning_title"}, "child": "tab-warning-content"},
        {"title": {"path": "/tab_info_title"}, "child": "tab-info-content"}
      ]}}},

      {"id": "tab-all-content", "component": {"List": {"direction": "vertical", "children": {"template": {"componentId": "file-group-card", "dataBinding": "/findings_all"}}}}},
      {"id": "tab-critical-content", "component": {"List": {"direction": "vertical", "children": {"template": {"componentId": "file-group-card", "dataBinding": "/findings_critical"}}}}},
      {"id": "tab-warning-content", "component": {"List": {"direction": "vertical", "children": {"template": {"componentId": "file-group-card", "dataBinding": "/findings_warning"}}}}},
      {"id": "tab-info-content", "component": {"List": {"direction": "vertical", "children": {"template": {"componentId": "file-group-card", "dataBinding": "/findings_info"}}}}},

      {"id": "file-group-card", "component": {"Card": {"child": "file-group-col"}}},
      {"id": "file-group-col", "component": {"Column": {"children": {"explicitList": ["file-group-header", "file-findings-list"]}}}},
      {"id": "file-group-header", "component": {"Row": {"children": {"explicitList": ["file-icon", "file-group-name", "file-issue-count"]}, "alignment": "center"}}},
      {"id": "file-icon", "component": {"Icon": {"name": "folder"}}},
      {"id": "file-group-name", "weight": 1, "component": {"Text": {"text": {"path": "file_path"}, "usageHint": "h3"}}},
      {"id": "file-issue-count", "component": {"Text": {"text": {"path": "issue_count"}, "usageHint": "caption"}}},

      {"id": "file-findings-list", "component": {"List": {"direction": "vertical", "children": {"template": {"componentId": "finding-card", "dataBinding": "findings"}}}}},

      {"id": "finding-card", "component": {"Card": {"child": "finding-col"}}},
      {"id": "finding-col", "component": {"Column": {"children": {"explicitList": ["finding-header", "finding-diff", "finding-desc"]}}}},
      {"id": "finding-header", "component": {"Row": {"children": {"explicitList": ["finding-checkbox", "severity-icon", "finding-location", "github-link-text"]}, "alignment": "center"}}},
      {"id": "finding-checkbox", "component": {"CheckBox": {"label": {"literalString": ""}, "value": {"path": "selected"}}}},
      {"id": "severity-icon", "component": {"Icon": {"name": {"path": "severity_icon"}}}},
      {"id": "finding-location", "weight": 1, "component": {"Text": {"text": {"path": "file_path"}, "usageHint": "h4"}}},
      {"id": "github-link-text", "component": {"Text": {"text": {"path": "github_url"}, "usageHint": "caption"}}},
      {"id": "finding-diff", "component": {"Text": {"text": {"path": "diff_snippet"}, "usageHint": "body"}}},
      {"id": "finding-desc", "component": {"Text": {"text": {"path": "description"}, "usageHint": "body"}}},
      {"id": "divider-2", "component": {"Divider": {}}},

      {"id": "post-modal", "component": {"Modal": {"entryPointChild": "post-selected-btn", "contentChild": "modal-content-col"}}},
      {"id": "post-selected-text", "component": {"Text": {"text": {"path": "/post_selected_label"}}}},
      {"id": "post-selected-btn", "component": {"Button": {"child": "post-selected-text", "primary": true}}},

      {"id": "modal-content-col", "component": {"Column": {"children": {"explicitList": ["modal-title", "modal-message", "modal-actions"]}, "alignment": "stretch"}}},
      {"id": "modal-title", "component": {"Text": {"text": {"literalString": "Post Review to GitHub?"}, "usageHint": "h3"}}},
      {"id": "modal-message", "component": {"Text": {"text": {"path": "/modal_message"}, "usageHint": "body"}}},
      {"id": "modal-actions", "component": {"Row": {"children": {"explicitList": ["modal-cancel-btn", "modal-confirm-btn"]}, "distribution": "end"}}},
      {"id": "modal-cancel-text", "component": {"Text": {"text": {"literalString": "Cancel"}}}},
      {"id": "modal-cancel-btn", "component": {"Button": {"child": "modal-cancel-text", "action": {"name": "modal_cancel"}}}},
      {"id": "modal-confirm-text", "component": {"Text": {"text": {"literalString": "Confirm & Post"}}}},
      {"id": "modal-confirm-btn", "component": {"Button": {"child": "modal-confirm-text", "primary": true, "action": {"name": "post_selected", "context": [{"key": "prUrl", "value": {"path": "/pr_url_raw"}}, {"key": "selectedFindings", "value": {"path": "/findings_json"}}]}}}}
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
      {"key": "tab_all_title", "valueString": "All (2)"},
      {"key": "tab_critical_title", "valueString": "Critical (1)"},
      {"key": "tab_warning_title", "valueString": "Warning (1)"},
      {"key": "tab_info_title", "valueString": "Info (0)"},
      {"key": "post_selected_label", "valueString": "Post Selected (2)"},
      {"key": "modal_message", "valueString": "2 findings will be posted as inline comments on the PR."},
      {"key": "findings_all", "valueMap": [
        {"key": "file_auth", "valueMap": [
          {"key": "file_path", "valueString": "src/auth.py"},
          {"key": "issue_count", "valueString": "1 issue"},
          {"key": "findings", "valueMap": [
            {"key": "f1", "valueMap": [
              {"key": "id", "valueString": "1"},
              {"key": "severity_icon", "valueString": "error"},
              {"key": "file_path", "valueString": "src/auth.py:45-52"},
              {"key": "github_url", "valueString": "https://github.com/owner/repo/blob/abc123/src/auth.py#L45-L52"},
              {"key": "diff_snippet", "valueString": "- if user:\\n+ if user is not None:"},
              {"key": "description", "valueString": "Missing explicit null check. `if user` evaluates falsy for empty strings and zero, potentially allowing unauthorized access."},
              {"key": "selected", "valueBoolean": true}
            ]}
          ]}
        ]},
        {"key": "file_db", "valueMap": [
          {"key": "file_path", "valueString": "src/db/query.py"},
          {"key": "issue_count", "valueString": "1 issue"},
          {"key": "findings", "valueMap": [
            {"key": "f2", "valueMap": [
              {"key": "id", "valueString": "2"},
              {"key": "severity_icon", "valueString": "warning"},
              {"key": "file_path", "valueString": "src/db/query.py:89-94"},
              {"key": "github_url", "valueString": "https://github.com/owner/repo/blob/abc123/src/auth.py#L45-L52"},
              {"key": "diff_snippet", "valueString": "+ query = \\"SELECT * FROM users WHERE id = \\" + str(user_id)"},
              {"key": "description", "valueString": "Potential SQL injection via string concatenation. Use parameterized queries instead."},
              {"key": "selected", "valueBoolean": true}
            ]}
          ]}
        ]}
      ]},
      {"key": "findings_critical", "valueMap": [
        {"key": "file_auth", "valueMap": [
          {"key": "file_path", "valueString": "src/auth.py"},
          {"key": "issue_count", "valueString": "1 issue"},
          {"key": "findings", "valueMap": [
            {"key": "f1", "valueMap": [
              {"key": "id", "valueString": "1"},
              {"key": "severity_icon", "valueString": "error"},
              {"key": "file_path", "valueString": "src/auth.py:45-52"},
              {"key": "github_url", "valueString": "https://github.com/owner/repo/blob/abc123/src/auth.py#L45-L52"},
              {"key": "diff_snippet", "valueString": "- if user:\\n+ if user is not None:"},
              {"key": "description", "valueString": "Missing explicit null check. `if user` evaluates falsy for empty strings and zero, potentially allowing unauthorized access."},
              {"key": "selected", "valueBoolean": true}
            ]}
          ]}
        ]}
      ]},
      {"key": "findings_warning", "valueMap": [
        {"key": "file_db", "valueMap": [
          {"key": "file_path", "valueString": "src/db/query.py"},
          {"key": "issue_count", "valueString": "1 issue"},
          {"key": "findings", "valueMap": [
            {"key": "f2", "valueMap": [
              {"key": "id", "valueString": "2"},
              {"key": "severity_icon", "valueString": "warning"},
              {"key": "file_path", "valueString": "src/db/query.py:89-94"},
              {"key": "github_url", "valueString": "https://github.com/owner/repo/blob/abc123/src/auth.py#L45-L52"},
              {"key": "diff_snippet", "valueString": "+ query = \\"SELECT * FROM users WHERE id = \\" + str(user_id)"},
              {"key": "description", "valueString": "Potential SQL injection via string concatenation. Use parameterized queries instead."},
              {"key": "selected", "valueBoolean": true}
            ]}
          ]}
        ]}
      ]},
      {"key": "findings_info", "valueMap": []}
    ]
  }},
  {"beginRendering": {"surfaceId": "review", "root": "root-col", "styles": {"primaryColor": "#1a73e8", "font": "Roboto"}}}
]
---END REVIEW_DASHBOARD_EXAMPLE---

---BEGIN FINDING_RESPONSE_EXAMPLE---
Use this template when answering follow-up questions about specific findings or code.
Show a brief response with relevant information.

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
IMPORTANT: Use surfaceId "review" to replace the existing review dashboard in-place.

[
  {"surfaceUpdate": {
    "surfaceId": "review",
    "components": [
      {"id": "result-col", "component": {"Column": {"children": {"explicitList": ["result-card"]}}}},
      {"id": "result-card", "component": {"Card": {"child": "result-card-col"}}},
      {"id": "result-card-col", "component": {"Column": {"children": {"explicitList": ["result-icon-row", "result-message", "result-link"]}}}},
      {"id": "result-icon-row", "component": {"Row": {"children": {"explicitList": ["result-icon", "result-title"]}, "alignment": "center"}}},
      {"id": "result-icon", "component": {"Icon": {"name": "check"}}},
      {"id": "result-title", "component": {"Text": {"text": {"path": "/result_title"}, "usageHint": "h2"}}},
      {"id": "result-message", "component": {"Text": {"text": {"path": "/result_message"}, "usageHint": "body"}}},
      {"id": "result-link", "component": {"Text": {"text": {"path": "/result_link"}, "usageHint": "caption"}}}
    ]
  }},
  {"dataModelUpdate": {
    "surfaceId": "review",
    "path": "/",
    "contents": [
      {"key": "result_title", "valueString": "Review Posted"},
      {"key": "result_message", "valueString": "Successfully posted 3 comments to the PR."},
      {"key": "result_link", "valueString": "https://github.com/owner/repo/pull/42#pullrequestreview-12345"}
    ]
  }},
  {"beginRendering": {"surfaceId": "review", "root": "result-col", "styles": {"primaryColor": "#1a73e8", "font": "Roboto"}}}
]
---END POST_REVIEW_RESULT_EXAMPLE---
"""
