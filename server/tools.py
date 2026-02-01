"""Tools for the code review agent.

Provides the fetch_pr_diff tool that retrieves PR diffs from GitHub API.
"""

import json
import logging
import os
import re

import requests
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


def fetch_pr_diff(pr_url: str, tool_context: ToolContext) -> str:
    """Fetch the diff and metadata for a GitHub pull request.

    Args:
        pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)

    Returns:
        JSON string with PR title, author, stats, and diff content.
    """
    logger.info("--- TOOL CALLED: fetch_pr_diff ---")
    logger.info(f"  - PR URL: {pr_url}")

    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        logger.error(f"  - Invalid PR URL format: {pr_url}")
        return json.dumps({
            "error": f"Invalid GitHub PR URL: {pr_url}. Expected format: https://github.com/owner/repo/pull/123"
        })

    owner, repo, pr_number = match.groups()
    token = os.getenv("GITHUB_TOKEN", "")

    headers: dict[str, str] = {"X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    meta_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    meta_headers = {**headers, "Accept": "application/vnd.github+json"}

    try:
        meta_resp = requests.get(meta_url, headers=meta_headers, timeout=15)
        meta_resp.raise_for_status()
        meta = meta_resp.json()
    except requests.RequestException as e:
        logger.error(f"  - Failed to fetch PR metadata: {e}")
        return json.dumps({"error": f"Failed to fetch PR metadata: {e}"})

    diff_headers = {**headers, "Accept": "application/vnd.github.diff"}

    try:
        diff_resp = requests.get(meta_url, headers=diff_headers, timeout=30)

        if diff_resp.status_code == 406:
            logger.warning("  - Diff too large. Fetching per-file patches instead.")
            return _fetch_pr_files_fallback(owner, repo, pr_number, headers, meta)

        diff_resp.raise_for_status()
        diff_text = diff_resp.text
    except requests.RequestException as e:
        logger.error(f"  - Failed to fetch diff: {e}")
        return json.dumps({"error": f"Failed to fetch PR diff: {e}"})

    max_diff_chars = 15000
    if len(diff_text) > max_diff_chars:
        diff_text = diff_text[:max_diff_chars] + "\n\n... [diff truncated, showing first 15000 chars] ..."
        logger.info(f"  - Diff truncated from {len(diff_resp.text)} to {max_diff_chars} chars")

    result = {
        "title": meta.get("title", f"PR #{pr_number}"),
        "author": meta.get("user", {}).get("login", "unknown"),
        "number": int(pr_number),
        "files_changed": meta.get("changed_files", 0),
        "additions": meta.get("additions", 0),
        "deletions": meta.get("deletions", 0),
        "head_sha": meta.get("head", {}).get("sha", ""),
        "base_url": f"https://github.com/{owner}/{repo}",
        "diff": diff_text,
    }

    logger.info(f"  - Success: {result['files_changed']} files, +{result['additions']}/-{result['deletions']}")
    return json.dumps(result)


def _build_position_map(
    owner: str, repo: str, pr_number: str, headers: dict[str, str],
) -> dict[str, dict[int, int]]:
    """Fetch PR files and build a mapping from (filename, line) to diff position.

    Returns: {filename: {new_file_line_number: diff_position}}
    """
    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    try:
        resp = requests.get(files_url, headers=headers, timeout=30)
        resp.raise_for_status()
        files = resp.json()
    except requests.RequestException as e:
        logger.warning(f"  - Failed to fetch PR files for position map: {e}")
        return {}

    position_map: dict[str, dict[int, int]] = {}
    for f in files:
        filename = f.get("filename", "")
        patch = f.get("patch", "")
        if not patch:
            continue

        file_positions: dict[int, int] = {}
        position = 0
        new_line = 0

        for line in patch.split("\n"):
            if line.startswith("@@"):
                # Parse @@ -old_start,old_count +new_start,new_count @@
                m = re.search(r"\+(\d+)", line)
                if m:
                    new_line = int(m.group(1)) - 1
                position += 1
                continue

            position += 1

            if line.startswith("-"):
                pass  # Deletion — no new file line
            elif line.startswith("+"):
                new_line += 1
                file_positions[new_line] = position
            else:
                # Context line
                new_line += 1
                file_positions[new_line] = position

        position_map[filename] = file_positions

    logger.info(f"  - Position map built for {len(position_map)} files")
    return position_map


def post_github_review(
    pr_url: str,
    review_body: str,
    findings_json: str,
    event: str,
    tool_context: ToolContext,
) -> str:
    """Post a code review to a GitHub pull request with inline comments.

    Args:
        pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
        review_body: Summary text for the overall review
        findings_json: JSON array string of findings, each with file_path, description, severity
        event: Review event type - COMMENT, APPROVE, or REQUEST_CHANGES

    Returns:
        JSON string with success status, review URL, and comment count, or error details.
    """
    logger.info("--- TOOL CALLED: post_github_review ---")
    logger.info(f"  - PR URL: {pr_url}")
    logger.info(f"  - Event: {event}")

    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        logger.error(f"  - Invalid PR URL format: {pr_url}")
        return json.dumps({"error": f"Invalid GitHub PR URL: {pr_url}"})

    owner, repo, pr_number = match.groups()
    token = os.getenv("GITHUB_TOKEN", "")

    if not token:
        logger.error("  - GITHUB_TOKEN not set")
        return json.dumps({"error": "GITHUB_TOKEN environment variable is not set. Cannot post review."})

    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        findings = json.loads(findings_json) if findings_json else []
    except json.JSONDecodeError as e:
        logger.error(f"  - Failed to parse findings_json: {e}")
        findings = []

    # Build position map from actual PR diff
    position_map = _build_position_map(owner, repo, pr_number, headers)

    comments: list[dict[str, str | int]] = []
    body_only_findings: list[str] = []
    for finding in findings:
        file_path_raw = finding.get("file_path", "")
        description = finding.get("description", "")
        severity = finding.get("severity_icon", finding.get("severity", "info"))

        # Parse "src/auth.py:45-52" -> path="src/auth.py", line=52
        path = file_path_raw
        line = None
        if ":" in file_path_raw:
            path, line_range = file_path_raw.rsplit(":", 1)
            try:
                if "-" in line_range:
                    line = int(line_range.split("-")[-1])
                else:
                    line = int(line_range)
            except ValueError:
                line = None

        severity_emoji = {"error": "\u274c", "warning": "\u26a0\ufe0f", "info": "\u2139\ufe0f"}.get(severity, "")
        comment_body = f"{severity_emoji} **{severity.upper()}**: {description}"

        # Look up whether this line is in the diff
        file_positions = position_map.get(path, {})
        resolved_line = line

        if line and not file_positions.get(line) and file_positions:
            # Line not exactly in diff — snap to closest line within 10 lines
            closest = min(file_positions.keys(), key=lambda l: abs(l - line))
            if abs(closest - line) <= 10:
                resolved_line = closest
                logger.info(f"  - Snapped line {line} to {closest} for {path}")
            else:
                resolved_line = None

        if resolved_line and file_positions.get(resolved_line):
            # Use line + side (more reliable than position-based approach)
            comments.append({"path": path, "body": comment_body, "line": resolved_line, "side": "RIGHT"})
        else:
            # Line not in diff — add to review body instead of inline comment
            body_only_findings.append(f"- {severity_emoji} **{path}:{line or '?'}** — {description}")
            logger.info(f"  - Line {line} not in diff for {path}, adding to body")

    # Build a structured review body from findings
    severity_counts: dict[str, int] = {"error": 0, "warning": 0, "info": 0}
    files_affected: set[str] = set()
    for finding in findings:
        sev = finding.get("severity_icon", finding.get("severity", "info"))
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        fp = finding.get("file_path", "")
        if ":" in fp:
            fp = fp.rsplit(":", 1)[0]
        files_affected.add(fp)

    total = len(findings)
    body_lines = [
        "## AI Code Review",
        "",
        f"**{total} issue{'s' if total != 1 else ''}** found across **{len(files_affected)} file{'s' if len(files_affected) != 1 else ''}**",
        "",
        "| Severity | Count |",
        "| --- | --- |",
    ]
    if severity_counts.get("error"):
        body_lines.append(f"| ❌ Critical | {severity_counts['error']} |")
    if severity_counts.get("warning"):
        body_lines.append(f"| ⚠️ Warning | {severity_counts['warning']} |")
    if severity_counts.get("info"):
        body_lines.append(f"| ℹ️ Info | {severity_counts['info']} |")

    if body_only_findings:
        body_lines += ["", "### Additional findings (not in diff)", ""]
        body_lines += body_only_findings

    if comments:
        body_lines += ["", "See inline comments below for details."]
    formatted_body = "\n".join(body_lines)

    review_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    event_value = event if event in ("APPROVE", "REQUEST_CHANGES", "COMMENT") else "COMMENT"

    payload: dict[str, str | list[dict[str, str | int]]] = {
        "body": formatted_body,
        "event": event_value,
    }
    if comments:
        payload["comments"] = comments

    try:
        resp = requests.post(review_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        error_detail = ""
        resp_obj = getattr(e, "response", None)
        if resp_obj is not None:
            error_detail = f" Response: {resp_obj.text[:500]}"
        logger.error(f"  - Failed to post review: {e}{error_detail}")
        return json.dumps({"error": f"Failed to post review: {e}{error_detail}"})

    result = resp.json()
    html_url = result.get("html_url", "")
    logger.info(f"  - Success: Review posted at {html_url}")
    return json.dumps({
        "success": True,
        "review_url": html_url,
        "comments_posted": len(comments),
    })


def create_github_issue(
    pr_url: str,
    title: str,
    body: str,
    labels_json: str,
    tool_context: ToolContext,
) -> str:
    """Create a GitHub issue on the repository associated with a pull request.

    Args:
        pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
        title: Issue title
        body: Issue body text
        labels_json: JSON array string of label names (e.g., '["bug", "security"]')

    Returns:
        JSON string with success status, issue URL, and issue number, or error details.
    """
    logger.info("--- TOOL CALLED: create_github_issue ---")
    logger.info(f"  - PR URL: {pr_url}, Title: {title[:80]}")

    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        return json.dumps({"error": f"Invalid GitHub PR URL: {pr_url}"})

    owner, repo, _pr_number = match.groups()
    token = os.getenv("GITHUB_TOKEN", "")

    if not token:
        return json.dumps({"error": "GITHUB_TOKEN environment variable is not set."})

    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        labels = json.loads(labels_json) if labels_json else []
    except json.JSONDecodeError:
        labels = []

    payload: dict[str, str | list[str]] = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels

    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    try:
        resp = requests.post(issues_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        error_detail = ""
        resp_obj = getattr(e, "response", None)
        if resp_obj is not None:
            error_detail = f" Response: {resp_obj.text[:500]}"
        logger.error(f"  - Failed to create issue: {e}{error_detail}")
        return json.dumps({"error": f"Failed to create issue: {e}{error_detail}"})

    result = resp.json()
    html_url = result.get("html_url", "")
    issue_number = result.get("number", 0)
    logger.info(f"  - Success: Issue #{issue_number} created at {html_url}")
    return json.dumps({
        "success": True,
        "issue_url": html_url,
        "issue_number": issue_number,
    })


def post_address_comment(
    pr_url: str,
    finding_description: str,
    file_path: str,
    tool_context: ToolContext,
) -> str:
    """Post a 'must address before merge' comment on a GitHub pull request.

    Args:
        pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
        finding_description: Description of the finding that must be addressed
        file_path: File path where the finding was identified

    Returns:
        JSON string with success status and comment URL, or error details.
    """
    logger.info("--- TOOL CALLED: post_address_comment ---")
    logger.info(f"  - PR URL: {pr_url}, File: {file_path}")

    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        return json.dumps({"error": f"Invalid GitHub PR URL: {pr_url}"})

    owner, repo, pr_number = match.groups()
    token = os.getenv("GITHUB_TOKEN", "")

    if not token:
        return json.dumps({"error": "GITHUB_TOKEN environment variable is not set."})

    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    comment_body = (
        f"**Must address before merge:**\n\n"
        f"{finding_description}\n\n"
        f"File: {file_path}"
    )

    comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"

    try:
        resp = requests.post(comments_url, headers=headers, json={"body": comment_body}, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        error_detail = ""
        resp_obj = getattr(e, "response", None)
        if resp_obj is not None:
            error_detail = f" Response: {resp_obj.text[:500]}"
        logger.error(f"  - Failed to post comment: {e}{error_detail}")
        return json.dumps({"error": f"Failed to post comment: {e}{error_detail}"})

    result = resp.json()
    html_url = result.get("html_url", "")
    logger.info(f"  - Success: Comment posted at {html_url}")
    return json.dumps({
        "success": True,
        "comment_url": html_url,
    })


def fetch_repo_labels(pr_url: str, tool_context: ToolContext) -> str:
    """Fetch available labels for the repository associated with a pull request.

    Args:
        pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)

    Returns:
        JSON array string of label objects with name and color fields.
    """
    logger.info("--- TOOL CALLED: fetch_repo_labels ---")
    logger.info(f"  - PR URL: {pr_url}")

    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        return json.dumps({"error": f"Invalid GitHub PR URL: {pr_url}"})

    owner, repo, _pr_number = match.groups()
    token = os.getenv("GITHUB_TOKEN", "")

    headers: dict[str, str] = {"X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    headers["Accept"] = "application/vnd.github+json"

    labels_url = f"https://api.github.com/repos/{owner}/{repo}/labels"

    try:
        resp = requests.get(labels_url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"  - Failed to fetch labels: {e}")
        return json.dumps([])

    labels = [{"name": l["name"], "color": l.get("color", "")} for l in resp.json()]
    logger.info(f"  - Success: Found {len(labels)} labels")
    return json.dumps(labels)


def search_github_issues(pr_url: str, keywords: str, tool_context: ToolContext) -> str:
    """Search for open GitHub issues in the repository matching keywords.

    Args:
        pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
        keywords: Space-separated keywords to search for in issue titles/bodies

    Returns:
        JSON array string of matching issues with number, title, and url fields.
    """
    logger.info("--- TOOL CALLED: search_github_issues ---")
    logger.info(f"  - PR URL: {pr_url}, Keywords: {keywords}")

    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        return json.dumps([])

    owner, repo, _pr_number = match.groups()
    token = os.getenv("GITHUB_TOKEN", "")

    headers: dict[str, str] = {"X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    headers["Accept"] = "application/vnd.github+json"

    query = f"repo:{owner}/{repo} type:issue state:open {keywords}"
    search_url = "https://api.github.com/search/issues"

    try:
        resp = requests.get(
            search_url,
            headers=headers,
            params={"q": query, "per_page": 5},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"  - Failed to search issues: {e}")
        return json.dumps([])

    items = resp.json().get("items", [])
    results = [
        {
            "number": item["number"],
            "title": item["title"],
            "url": item["html_url"],
        }
        for item in items
    ]
    logger.info(f"  - Success: Found {len(results)} matching issues")
    return json.dumps(results)


def link_fixes_to_pr(pr_url: str, issue_number: int, tool_context: ToolContext) -> str:
    """Append 'Fixes #N' to a GitHub PR description to auto-close an issue on merge.

    Args:
        pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
        issue_number: The issue number to link as fixed

    Returns:
        JSON string with success status, or error details.
    """
    logger.info("--- TOOL CALLED: link_fixes_to_pr ---")
    logger.info(f"  - PR URL: {pr_url}, Issue: #{issue_number}")

    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        return json.dumps({"error": f"Invalid GitHub PR URL: {pr_url}"})

    owner, repo, pr_number = match.groups()
    token = os.getenv("GITHUB_TOKEN", "")

    if not token:
        return json.dumps({"error": "GITHUB_TOKEN environment variable is not set."})

    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    pr_api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

    # Read current PR body
    try:
        resp = requests.get(pr_api_url, headers=headers, timeout=15)
        resp.raise_for_status()
        pr_data = resp.json()
    except requests.RequestException as e:
        logger.error(f"  - Failed to fetch PR: {e}")
        return json.dumps({"error": f"Failed to fetch PR: {e}"})

    current_body = pr_data.get("body") or ""
    fixes_ref = f"Fixes #{issue_number}"

    if fixes_ref in current_body:
        logger.info(f"  - '{fixes_ref}' already in PR description")
        return json.dumps({
            "success": True,
            "already_linked": True,
            "issue_number": issue_number,
            "pr_url": pr_data.get("html_url", pr_url),
        })

    updated_body = current_body + f"\n\n{fixes_ref}"

    try:
        resp = requests.patch(
            pr_api_url,
            headers=headers,
            json={"body": updated_body},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        error_detail = ""
        resp_obj = getattr(e, "response", None)
        if resp_obj is not None:
            error_detail = f" Response: {resp_obj.text[:500]}"
        logger.error(f"  - Failed to update PR: {e}{error_detail}")
        return json.dumps({"error": f"Failed to update PR: {e}{error_detail}"})

    result = resp.json()
    html_url = result.get("html_url", pr_url)
    logger.info(f"  - Success: Added '{fixes_ref}' to PR description")
    return json.dumps({
        "success": True,
        "already_linked": False,
        "issue_number": issue_number,
        "pr_url": html_url,
    })


def _fetch_pr_files_fallback(
    owner: str, repo: str, pr_number: str, headers: dict[str, str], meta: dict,
) -> str:
    """Fallback for large PRs: fetch per-file patches."""
    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    files_headers = {**headers, "Accept": "application/vnd.github+json"}

    try:
        files_resp = requests.get(files_url, headers=files_headers, timeout=30)
        files_resp.raise_for_status()
        files = files_resp.json()
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch PR files: {e}"})

    diff_parts: list[str] = []
    total_chars = 0
    max_chars = 15000

    for f in files:
        patch = f.get("patch", "")
        header = f"--- a/{f['filename']}\n+++ b/{f['filename']}\n"
        section = header + patch + "\n"

        if total_chars + len(section) > max_chars:
            diff_parts.append("\n... [remaining files truncated] ...")
            break

        diff_parts.append(section)
        total_chars += len(section)

    return json.dumps({
        "title": meta.get("title", f"PR #{pr_number}"),
        "author": meta.get("user", {}).get("login", "unknown"),
        "number": int(pr_number),
        "files_changed": meta.get("changed_files", 0),
        "additions": meta.get("additions", 0),
        "deletions": meta.get("deletions", 0),
        "head_sha": meta.get("head", {}).get("sha", ""),
        "base_url": f"https://github.com/{owner}/{repo}",
        "diff": "\n".join(diff_parts),
    })
