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

    comments: list[dict[str, str | int]] = []
    for finding in findings:
        file_path_raw = finding.get("file_path", "")
        description = finding.get("description", "")
        severity = finding.get("severity", "info")

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

        severity_prefix = f"[{severity.upper()}] " if severity else ""
        comment: dict[str, str | int] = {
            "path": path,
            "body": f"{severity_prefix}{description}",
        }
        if line is not None:
            comment["position"] = line

        comments.append(comment)

    review_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    payload: dict[str, str | list[dict[str, str | int]]] = {
        "body": review_body,
        "event": event if event in ("APPROVE", "REQUEST_CHANGES", "COMMENT") else "COMMENT",
    }
    if comments:
        payload["comments"] = comments

    try:
        resp = requests.post(review_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        html_url = result.get("html_url", "")
        logger.info(f"  - Success: Review posted at {html_url}")
        return json.dumps({
            "success": True,
            "review_url": html_url,
            "comments_posted": len(comments),
        })
    except requests.RequestException as e:
        error_detail = ""
        if hasattr(e, "response") and e.response is not None:
            error_detail = f" Response: {e.response.text[:500]}"
        logger.error(f"  - Failed to post review: {e}{error_detail}")
        return json.dumps({"error": f"Failed to post review: {e}{error_detail}"})


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
