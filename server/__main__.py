"""A2UI Code Review Agent - Server entry point.

Starts the A2A server with A2UI extension support.
Run with: uv run .
"""

import logging
import os

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2ui_helpers import get_a2ui_agent_extension
from agent import CodeReviewAgent
from agent_executor import CodeReviewAgentExecutor
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host: str, port: int) -> None:
    if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE":
        if not os.getenv("GEMINI_API_KEY"):
            logger.error(
                "GEMINI_API_KEY environment variable not set. "
                "Get one at https://aistudio.google.com/apikey"
            )
            exit(1)

    capabilities = AgentCapabilities(
        streaming=True,
        extensions=[get_a2ui_agent_extension()],
    )

    skill = AgentSkill(
        id="review_pr",
        name="Review Pull Request",
        description="Analyzes a GitHub PR diff and identifies critical code issues.",
        tags=["code-review", "github", "pr"],
        examples=[
            "Review https://github.com/owner/repo/pull/123",
            "Check this PR for security issues: https://github.com/org/project/pull/42",
        ],
    )

    base_url = f"http://{host}:{port}"

    agent_card = AgentCard(
        name="Code Review Agent",
        description="AI-powered code review that identifies security vulnerabilities, silent failures, and logic bugs in GitHub PRs.",
        url=base_url,
        version="0.1.0",
        default_input_modes=CodeReviewAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=CodeReviewAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )

    executor = CodeReviewAgentExecutor()

    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    app = server.build()

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://localhost:\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info(f"Starting Code Review Agent at {base_url}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
