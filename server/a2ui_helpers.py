"""Vendored A2UI extension helpers.

These functions are extracted from the a2ui-agent package
(github.com/google/a2ui - a2a_agents/python/a2ui_agent/src/a2ui/extension/a2ui_extension.py)
which is not published to PyPI. We vendor the essential functions here.
"""

import logging
from typing import Any

from a2a.server.agent_execution import RequestContext
from a2a.types import AgentExtension, DataPart, Part

logger = logging.getLogger(__name__)

A2UI_EXTENSION_URI = "https://a2ui.org/a2a-extension/a2ui/v0.8"
MIME_TYPE_KEY = "mimeType"
A2UI_MIME_TYPE = "application/json+a2ui"


def create_a2ui_part(a2ui_data: dict[str, Any]) -> Part:
    """Creates an A2A Part containing A2UI data."""
    return Part(
        root=DataPart(
            data=a2ui_data,
            metadata={
                MIME_TYPE_KEY: A2UI_MIME_TYPE,
            },
        )
    )


def get_a2ui_agent_extension() -> AgentExtension:
    """Creates the A2UI AgentExtension configuration for the agent card."""
    return AgentExtension(
        uri=A2UI_EXTENSION_URI,
        description="Provides agent driven UI using the A2UI JSON format.",
    )


def try_activate_a2ui_extension(context: RequestContext) -> bool:
    """Checks if the client requested A2UI and activates it.

    Returns True if A2UI was activated, False otherwise.
    """
    if A2UI_EXTENSION_URI in context.requested_extensions or (
        context.message
        and context.message.extensions
        and A2UI_EXTENSION_URI in context.message.extensions
    ):
        context.add_activated_extension(A2UI_EXTENSION_URI)
        return True
    return False
