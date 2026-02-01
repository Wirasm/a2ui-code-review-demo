"""Code Review LLM Agent.

Wraps the Google ADK LlmAgent with A2UI JSON schema validation
and retry logic. Creates both a UI agent (generates A2UI) and a
text agent (plain text fallback).
"""

import json
import logging
import os
from collections.abc import AsyncIterable
from typing import Any

import jsonschema
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from a2ui_schema import A2UI_SCHEMA
from prompt_builder import get_text_prompt, get_ui_prompt
from tools import fetch_pr_diff, post_github_review, create_github_issue, post_address_comment, fetch_repo_labels, search_github_issues, link_fixes_to_pr

logger = logging.getLogger(__name__)

AGENT_INSTRUCTION = """
You are a code review assistant. You analyze GitHub pull request diffs
and identify critical issues that need human attention.

REVIEW FOCUS (in priority order):
1. Security vulnerabilities (SQL injection, XSS, auth bypasses, secrets exposure)
2. Silent failures (swallowed exceptions, missing error handling, ignored return values)
3. Logic bugs (off-by-one errors, null/None checks, race conditions, wrong comparisons)
4. Breaking changes (API contract changes, missing migrations, backwards incompatibility)
5. Performance issues (N+1 queries, unbounded loops, missing indexes)

WORKFLOW:
1. When the user provides a PR URL, call the `fetch_pr_diff` tool to get the diff.
2. Analyze the diff for the issue categories above.
3. Report the top 5-8 most impactful findings. Skip trivial style issues.
4. For each finding, include: the file path with line numbers, the relevant diff lines,
   and a clear explanation of the issue and its potential impact.
5. When the user requests posting the review to GitHub, call `post_github_review` with
   the PR URL, a review summary, the findings as JSON, and event type "COMMENT".
   Then show a confirmation using the POST_REVIEW_RESULT_EXAMPLE template.

SEVERITY LEVELS:
- Use icon "error" for critical issues (security, data loss)
- Use icon "warning" for bugs, logic issues, silent failures
- Use icon "info" for minor suggestions, style improvements

6. When the user wants to create a GitHub issue from a finding, first call `fetch_repo_labels`
   to get available labels, then show the ISSUE_FORM_EXAMPLE template with pre-filled title and body,
   and the labels as MultipleChoice options.
7. When the user submits the issue form ("create_issue_submit"), call `create_github_issue`
   with the PR URL, title, body, and selected labels. Then show a confirmation using
   the ISSUE_RESULT_EXAMPLE template.
8. When the user wants to mark a finding as "address before merge", call `post_address_comment`
   with the PR URL, finding description, and file path. Then show a confirmation using
   the POST_REVIEW_RESULT_EXAMPLE template.
9. During your initial PR review, for EACH finding, extract 2-3 keywords from the description
   and call `search_github_issues` to find related open issues. Include any matches in the
   finding's `related_issues` data. Use the REVIEW_DASHBOARD_EXAMPLE template which includes
   a related-issues-list component in each finding card.
10. After generating all findings, also check if any open issues appear to be FIXED by this PR.
    If so, include them in the `suggested_closures` data model and show the SUGGESTED_CLOSURES_EXAMPLE card.
11. When the user clicks "Link to PR" on a suggested closure, call `link_fixes_to_pr` to append
    "Fixes #N" to the PR description. Show confirmation using the LINK_RESULT_EXAMPLE template.

When the user clicks "Will Address" or "Dismiss" on a finding, acknowledge their
decision and show a brief confirmation.

When the user asks follow-up questions about specific findings or code, respond with the
FINDING_RESPONSE_EXAMPLE template or plain text if a UI surface is not appropriate.
"""


class CodeReviewAgent:
    """An agent that reviews GitHub PRs and identifies critical code issues."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, use_ui: bool = False) -> None:
        self.use_ui = use_ui
        self._agent = self._build_agent(use_ui)
        self._user_id = "remote_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        try:
            single_message_schema = json.loads(A2UI_SCHEMA)
            self.a2ui_schema_object: dict[str, Any] | None = {
                "type": "array",
                "items": single_message_schema,
            }
            logger.info("A2UI_SCHEMA loaded and wrapped in array validator.")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse A2UI_SCHEMA: {e}")
            self.a2ui_schema_object = None

    def _build_agent(self, use_ui: bool) -> LlmAgent:
        model_name = os.getenv("LITELLM_MODEL", "gemini/gemini-2.5-flash")

        if use_ui:
            instruction = AGENT_INSTRUCTION + get_ui_prompt()
        else:
            instruction = AGENT_INSTRUCTION + get_text_prompt()

        return LlmAgent(
            model=LiteLlm(model=model_name),
            name="code_review_agent",
            description="An agent that reviews GitHub PRs and identifies critical code issues.",
            instruction=instruction,
            tools=[fetch_pr_diff, post_github_review, create_github_issue, post_address_comment, fetch_repo_labels, search_github_issues, link_fixes_to_pr],
        )

    async def stream(self, query: str, session_id: str) -> AsyncIterable[dict[str, Any]]:
        """Stream the agent's response, with validation and retry for UI mode."""
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )

        if self.use_ui and self.a2ui_schema_object is None:
            logger.error("A2UI_SCHEMA is not loaded. Cannot validate UI output.")
            yield {
                "is_task_complete": True,
                "content": "Internal error: UI schema not loaded.",
            }
            return

        max_retries = 1  # 2 total attempts
        attempt = 0
        current_query_text = query

        while attempt <= max_retries:
            attempt += 1
            logger.info(f"--- Attempt {attempt}/{max_retries + 1} for session {session_id} ---")

            current_message = types.Content(
                role="user", parts=[types.Part.from_text(text=current_query_text)]
            )
            final_response_content = None

            status_phase = 0
            async for event in self._runner.run_async(
                user_id=self._user_id,
                session_id=session.id,
                new_message=current_message,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_content = "\n".join(
                            [p.text for p in event.content.parts if p.text]
                        )
                    break
                else:
                    # Emit progressively more specific status messages
                    status_messages = [
                        "Fetching PR diff from GitHub...",
                        "Analyzing changes for critical issues...",
                        "Reviewing code patterns and security...",
                        "Generating findings and recommendations...",
                    ]
                    status_text = status_messages[min(status_phase, len(status_messages) - 1)]
                    status_phase += 1
                    yield {
                        "is_task_complete": False,
                        "updates": status_text,
                    }

            if final_response_content is None:
                logger.warning(f"No final response from runner (attempt {attempt})")
                if attempt <= max_retries:
                    current_query_text = (
                        "I received no response. Please try again. "
                        f"Original request: '{query}'"
                    )
                    continue
                else:
                    final_response_content = "Sorry, I couldn't process your request. Please try again."

            is_valid = False
            error_message = ""

            if self.use_ui:
                try:
                    if "---a2ui_JSON---" not in final_response_content:
                        raise ValueError("Delimiter '---a2ui_JSON---' not found in response.")

                    _text_part, json_string = final_response_content.split("---a2ui_JSON---", 1)

                    if not json_string.strip():
                        raise ValueError("JSON part is empty after delimiter.")

                    json_cleaned = json_string.strip().lstrip("```json").rstrip("```").strip()

                    if not json_cleaned:
                        raise ValueError("Cleaned JSON string is empty.")

                    parsed_json = json.loads(json_cleaned)

                    jsonschema.validate(instance=parsed_json, schema=self.a2ui_schema_object)

                    logger.info(f"A2UI JSON validated successfully (attempt {attempt})")
                    is_valid = True

                except (ValueError, json.JSONDecodeError, jsonschema.exceptions.ValidationError) as e:
                    logger.warning(f"A2UI validation failed: {e} (attempt {attempt})")
                    error_message = f"Validation failed: {e}"
            else:
                is_valid = True

            if is_valid:
                yield {"is_task_complete": True, "content": final_response_content}
                return

            if attempt <= max_retries:
                logger.warning(f"Retrying ({attempt}/{max_retries + 1})...")
                current_query_text = (
                    f"Your previous response was invalid. {error_message} "
                    "You MUST generate a valid response with '---a2ui_JSON---' delimiter "
                    "followed by a valid JSON array of A2UI messages. "
                    f"Please retry the original request: '{query}'"
                )

        logger.error("Max retries exhausted. Sending text-only fallback.")
        yield {
            "is_task_complete": True,
            "content": "Sorry, I'm having trouble generating the review interface. Please try again.",
        }
