"""A2A AgentExecutor for the code review agent.

Handles incoming A2A requests, extracts user input (text or UI actions),
delegates to the LLM agent, and returns A2UI responses.
"""

import json
import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import DataPart, Part, Task, TaskState, TextPart, UnsupportedOperationError
from a2a.utils import new_agent_parts_message, new_agent_text_message, new_task
from a2a.utils.errors import ServerError
from a2ui_helpers import create_a2ui_part, try_activate_a2ui_extension
from agent import CodeReviewAgent

logger = logging.getLogger(__name__)


class CodeReviewAgentExecutor(AgentExecutor):
    """Handles A2A protocol requests for the code review agent."""

    def __init__(self) -> None:
        self.ui_agent = CodeReviewAgent(use_ui=True)
        self.text_agent = CodeReviewAgent(use_ui=False)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = ""
        ui_event_part = None

        use_ui = try_activate_a2ui_extension(context)
        agent = self.ui_agent if use_ui else self.text_agent

        if use_ui:
            logger.info("A2UI extension active. Using UI agent.")
        else:
            logger.info("A2UI extension not active. Using text agent.")

        if context.message and context.message.parts:
            for i, part in enumerate(context.message.parts):
                if isinstance(part.root, DataPart):
                    if "userAction" in part.root.data:
                        logger.info(f"  Part {i}: A2UI userAction")
                        ui_event_part = part.root.data["userAction"]
                    else:
                        logger.info(f"  Part {i}: DataPart")
                elif isinstance(part.root, TextPart):
                    logger.info(f"  Part {i}: TextPart: {part.root.text[:100]}")

        if ui_event_part:
            action = ui_event_part.get("name", ui_event_part.get("actionName", ""))
            ctx = ui_event_part.get("context", {})
            logger.info(f"UI action: {action}, context: {ctx}")

            if action == "post_review":
                pr_url = ctx.get("prUrl", "")
                findings = ctx.get("findings", "[]")
                query = (
                    f"The user wants to post your review findings to the GitHub PR. "
                    f"Call the `post_github_review` tool with pr_url='{pr_url}', "
                    f"review_body='AI Code Review - automated findings from analysis', "
                    f"findings_json='{findings}', "
                    f"event='COMMENT'. "
                    "After posting, show a confirmation using the POST_REVIEW_RESULT_EXAMPLE template."
                )
            elif action == "toggle_finding":
                finding_id = ctx.get("findingId", "unknown")
                selected = ctx.get("selected", True)
                status = "selected" if selected else "deselected"
                query = (
                    f"The user {status} finding #{finding_id} for review posting. "
                    "No UI update needed — just acknowledge."
                )
            elif action == "post_selected":
                pr_url = ctx.get("prUrl", "")
                findings = ctx.get("selectedFindings", "[]")
                query = (
                    f"The user wants to post SELECTED review findings to the GitHub PR. "
                    f"Call the `post_github_review` tool with pr_url='{pr_url}', "
                    f"review_body='AI Code Review - selected findings from analysis', "
                    f"findings_json='{findings}', "
                    f"event='COMMENT'. "
                    "After posting, show a confirmation using the POST_REVIEW_RESULT_EXAMPLE template."
                )
            elif action == "create_issue":
                finding_desc = ctx.get("description", "")
                finding_path = ctx.get("filePath", "")
                pr_url = ctx.get("prUrl", "")
                query = (
                    f"The user wants to create a GitHub issue from a finding. "
                    f"First call `fetch_repo_labels` with pr_url='{pr_url}' to get available labels. "
                    f"Then show an issue creation form using the ISSUE_FORM_EXAMPLE template. "
                    f"Pre-fill title with 'Fix: {finding_desc[:60]}', "
                    f"body with 'Found during code review.\\n\\n{finding_desc}\\n\\nFile: {finding_path}'. "
                    f"Include the fetched labels as MultipleChoice options. "
                    f"Set pr_url_raw to '{pr_url}'."
                )
            elif action == "create_issue_submit":
                pr_url = ctx.get("prUrl", "")
                title = ctx.get("title", "")
                body = ctx.get("body", "")
                labels = ctx.get("labels", "[]")
                query = (
                    f"The user wants to submit a GitHub issue. "
                    f"Call the `create_github_issue` tool with pr_url='{pr_url}', "
                    f"title='{title}', body='{body}', labels_json='{labels}'. "
                    "After creating, show a confirmation using the ISSUE_RESULT_EXAMPLE template."
                )
            elif action == "address_finding":
                pr_url = ctx.get("prUrl", "")
                description = ctx.get("description", "")
                file_path = ctx.get("filePath", "")
                query = (
                    f"The user wants to mark a finding as 'must address before merge'. "
                    f"Call the `post_address_comment` tool with pr_url='{pr_url}', "
                    f"finding_description='{description}', file_path='{file_path}'. "
                    "After posting, show a confirmation using the POST_REVIEW_RESULT_EXAMPLE template."
                )
            else:
                query = f"User action: {action} with context: {ctx}"
        else:
            query = context.get_user_input()

        logger.info(f"Final query: {query[:200]}")

        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        async for item in agent.stream(query, task.context_id):
            if not item["is_task_complete"]:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(item["updates"], task.context_id, task.id),
                )
                continue

            content = item["content"]
            final_parts: list[Part] = []

            if "---a2ui_JSON---" in content:
                logger.info("Splitting response into text and A2UI parts.")
                text_content, json_string = content.split("---a2ui_JSON---", 1)

                if text_content.strip():
                    final_parts.append(Part(root=TextPart(text=text_content.strip())))

                if json_string.strip():
                    try:
                        json_cleaned = (
                            json_string.strip().lstrip("```json").rstrip("```").strip()
                        )
                        json_data = json.loads(json_cleaned)

                        if isinstance(json_data, list):
                            logger.info(f"Found {len(json_data)} A2UI messages.")
                            for message in json_data:
                                final_parts.append(create_a2ui_part(message))
                        else:
                            logger.info("Single A2UI message (not a list).")
                            final_parts.append(create_a2ui_part(json_data))

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse A2UI JSON: {e}")
                        final_parts.append(Part(root=TextPart(text=json_string)))
            else:
                final_parts.append(Part(root=TextPart(text=content.strip())))

            await updater.update_status(
                TaskState.input_required,
                new_agent_parts_message(final_parts, task.context_id, task.id),
                final=False,
            )
            break

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
