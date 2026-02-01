# A2UI (Agent to UI) Protocol - Build Reference

This document contains everything needed to build A2UI agents from scratch. A2UI is a Google protocol (v0.8) that lets AI agents generate rich, interactive UIs through safe, declarative JSON messages - no code execution required.

## Protocol Overview

A2UI messages flow over the A2A (Agent-to-Agent) protocol. An agent receives user input, calls an LLM, and the LLM generates A2UI JSON that the client renders into native web components.

```
User Input → A2A Agent → LLM → A2UI JSON → Client Renderer → Native UI
```

Key properties:

- **Declarative**: Agents describe WHAT the UI should be, not HOW to render it
- **Safe**: No code execution - just structured JSON
- **Separation of concerns**: Structure (components), Data (data model), and Presentation (styles) are separate messages

## Message Types (Server → Client)

Each message contains exactly ONE of these properties:

### 1. `beginRendering` - Initialize a surface

```json
{
  "beginRendering": {
    "surfaceId": "main",
    "root": "root-column",
    "styles": {
      "primaryColor": "#007BFF",
      "font": "Roboto"
    }
  }
}
```

### 2. `surfaceUpdate` - Define components

```json
{
  "surfaceUpdate": {
    "surfaceId": "main",
    "components": [
      {
        "id": "header",
        "component": {
          "Text": {
            "text": { "literalString": "Hello World" },
            "usageHint": "h1"
          }
        }
      }
    ]
  }
}
```

### 3. `dataModelUpdate` - Populate data

```json
{
  "dataModelUpdate": {
    "surfaceId": "main",
    "path": "/",
    "contents": [
      { "key": "name", "valueString": "John" },
      { "key": "age", "valueNumber": 30 },
      { "key": "active", "valueBoolean": true }
    ]
  }
}
```

### 4. `deleteSurface` - Remove a surface

```json
{ "deleteSurface": { "surfaceId": "main" } }
```

### Standard Message Order

A complete UI response is always 3 messages in a JSON array:

```json
[
  {"surfaceUpdate": {...}},
  {"dataModelUpdate": {...}},
  {"beginRendering": {...}}
]
```

Note: `beginRendering` can come first or last - the client waits for all three before rendering. The examples in the repo typically put it first, but order is flexible.

## Message Types (Client → Server)

### `userAction` - Button clicks and form submissions

```json
{
  "userAction": {
    "name": "book_restaurant",
    "surfaceId": "main",
    "sourceComponentId": "book-btn",
    "timestamp": "2025-01-15T10:30:00Z",
    "context": {
      "restaurantName": "The Fancy Place",
      "partySize": 4
    }
  }
}
```

## Component Catalog (18 Standard Components)

### Display Components

| Component       | Required Props | Optional Props                                                                                                       | Description                       |
| --------------- | -------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| **Text**        | `text`         | `usageHint` (h1-h5, body, caption)                                                                                   | Text display, supports markdown   |
| **Image**       | `url`          | `fit` (contain/cover/fill/none/scale-down), `usageHint` (icon/avatar/smallFeature/mediumFeature/largeFeature/header) | Image display                     |
| **Icon**        | `name`         | -                                                                                                                    | Material icon from predefined set |
| **Video**       | `url`          | -                                                                                                                    | Video player                      |
| **AudioPlayer** | `url`          | `description`                                                                                                        | Audio player                      |
| **Divider**     | -              | `axis` (horizontal/vertical)                                                                                         | Visual separator                  |

### Layout Components

| Component  | Required Props                    | Optional Props                                                                                                 | Description                   |
| ---------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| **Row**    | `children`                        | `distribution` (start/center/end/spaceBetween/spaceAround/spaceEvenly), `alignment` (start/center/end/stretch) | Horizontal layout             |
| **Column** | `children`                        | `distribution`, `alignment`                                                                                    | Vertical layout               |
| **List**   | `children`                        | `direction` (vertical/horizontal), `alignment`                                                                 | Scrollable list               |
| **Card**   | `child`                           | -                                                                                                              | Card container (single child) |
| **Tabs**   | `tabItems`                        | -                                                                                                              | Tabbed interface              |
| **Modal**  | `entryPointChild`, `contentChild` | -                                                                                                              | Modal dialog                  |

### Interactive Components

| Component          | Required Props          | Optional Props                                                                        | Description                           |
| ------------------ | ----------------------- | ------------------------------------------------------------------------------------- | ------------------------------------- |
| **Button**         | `child`, `action`       | `primary`                                                                             | Clickable button with action dispatch |
| **CheckBox**       | `label`, `value`        | -                                                                                     | Boolean toggle                        |
| **TextField**      | `label`                 | `text`, `textFieldType` (shortText/longText/number/date/obscured), `validationRegexp` | Text input                            |
| **DateTimeInput**  | `value`                 | `enableDate`, `enableTime`                                                            | Date/time picker                      |
| **MultipleChoice** | `selections`, `options` | `maxAllowedSelections`                                                                | Multi-select                          |
| **Slider**         | `value`                 | `minValue`, `maxValue`                                                                | Range slider                          |

### Available Icons

`accountCircle`, `add`, `arrowBack`, `arrowForward`, `attachFile`, `calendarToday`, `call`, `camera`, `check`, `close`, `delete`, `download`, `edit`, `event`, `error`, `favorite`, `favoriteOff`, `folder`, `help`, `home`, `info`, `locationOn`, `lock`, `lockOpen`, `mail`, `menu`, `moreVert`, `moreHoriz`, `notificationsOff`, `notifications`, `payment`, `person`, `phone`, `photo`, `print`, `refresh`, `search`, `send`, `settings`, `share`, `shoppingCart`, `star`, `starHalf`, `starOff`, `upload`, `visibility`, `visibilityOff`, `warning`

## Data Binding

Components reference data via paths or literal values:

### String Values

```json
{"literalString": "Fixed text"}
// or
{"path": "/user/name"}
```

### Number Values

```json
{"literalNumber": 42}
// or
{"path": "/data/count"}
```

### Boolean Values

```json
{"literalBoolean": true}
// or
{"path": "/data/enabled"}
```

### Nested Data in `dataModelUpdate`

```json
{
  "dataModelUpdate": {
    "surfaceId": "main",
    "path": "/",
    "contents": [
      {
        "key": "contacts",
        "valueMap": [
          {
            "key": "contact1",
            "valueMap": [
              { "key": "name", "valueString": "Alice" },
              { "key": "email", "valueString": "alice@example.com" }
            ]
          }
        ]
      }
    ]
  }
}
```

This creates paths: `/contacts/contact1/name` → "Alice", `/contacts/contact1/email` → "alice@example.com"

## Children and Templates

### Explicit List (fixed children)

```json
{
  "Column": {
    "children": {
      "explicitList": ["header", "content", "footer"]
    }
  }
}
```

### Template (dynamic list from data)

```json
{
  "List": {
    "direction": "vertical",
    "children": {
      "template": {
        "componentId": "item-card-template",
        "dataBinding": "/contacts"
      }
    }
  }
}
```

Creates one instance of `item-card-template` for each entry in `/contacts`. Inside the template, relative paths like `"path": "name"` resolve to `/contacts/contact1/name`, `/contacts/contact2/name`, etc.

## Button Actions

```json
{
  "id": "book-btn",
  "component": {
    "Button": {
      "child": "book-btn-text",
      "primary": true,
      "action": {
        "name": "book_restaurant",
        "context": [
          { "key": "restaurantName", "value": { "path": "name" } },
          { "key": "partySize", "value": { "literalNumber": 4 } }
        ]
      }
    }
  }
}
```

When clicked, the client resolves data bindings and sends a `userAction` message to the agent with the resolved context values.

## Component Flex Weight

Components can specify `weight` for flex layout in Row/Column:

```json
{
  "id": "sidebar",
  "weight": 1,
  "component": {"Column": {...}}
}
```

## Agent Architecture (Python)

### File Structure

```
my_agent/
├── __main__.py          # Server setup, extension registration
├── agent.py             # LLM agent, prompt construction, validation
├── agent_executor.py    # Request handling, input processing, A2UI part creation
├── prompt_builder.py    # System prompt with schema + examples
├── a2ui_schema.py       # A2UI JSON schema string
├── a2ui_examples.py     # UI template examples for the LLM
├── tools.py             # Domain-specific tool functions
├── data.json            # Sample/mock data
└── pyproject.toml       # Dependencies
```

### Dependencies (`pyproject.toml`)

```toml
[project]
name = "my-a2ui-agent"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
  "a2a-sdk>=0.3.0",
  "google-adk>=1.8.0",
  "google-genai>=1.27.0",
  "jsonschema>=4.0.0",
  "litellm",
  "click",
  "python-dotenv",
  "starlette",
  "uvicorn",
  "a2ui-agent",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

The `a2ui-agent` package comes from the A2UI repo at `a2a_agents/python/a2ui_agent/`. It provides `a2ui.extension.a2ui_extension` with helper functions.

### Server Setup (`__main__.py`)

```python
import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2ui.extension.a2ui_extension import get_a2ui_agent_extension
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host, port):
    capabilities = AgentCapabilities(
        streaming=True,
        extensions=[get_a2ui_agent_extension()],
    )
    skill = AgentSkill(
        id="my_skill",
        name="My Skill",
        description="Description of what this agent does.",
        tags=["tag1", "tag2"],
        examples=["Example prompt 1"],
    )
    base_url = f"http://{host}:{port}"
    agent_card = AgentCard(
        name="My Agent",
        description="Agent description.",
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["text/plain", "application/json"],
        capabilities=capabilities,
        skills=[skill],
    )

    executor = MyAgentExecutor(base_url=base_url)
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
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
```

### Agent Executor Pattern (`agent_executor.py`)

````python
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import DataPart, Part, Task, TaskState, TextPart
from a2a.utils import new_agent_parts_message, new_agent_text_message, new_task
from a2ui.extension.a2ui_extension import create_a2ui_part, try_activate_a2ui_extension

class MyAgentExecutor(AgentExecutor):
    def __init__(self, base_url: str):
        self.ui_agent = MyAgent(base_url=base_url, use_ui=True)
        self.text_agent = MyAgent(base_url=base_url, use_ui=False)

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # 1. Check if client supports A2UI
        use_ui = try_activate_a2ui_extension(context)
        agent = self.ui_agent if use_ui else self.text_agent

        # 2. Extract user input (text or UI action)
        query = ""
        ui_event_part = None
        if context.message and context.message.parts:
            for part in context.message.parts:
                if isinstance(part.root, DataPart) and "userAction" in part.root.data:
                    ui_event_part = part.root.data["userAction"]
                elif isinstance(part.root, TextPart):
                    pass  # handled by get_user_input()

        if ui_event_part:
            action = ui_event_part.get("name")
            ctx = ui_event_part.get("context", {})
            query = f"User action: {action} with context: {ctx}"
        else:
            query = context.get_user_input()

        # 3. Create or get task
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # 4. Stream agent response
        async for item in agent.stream(query, task.context_id):
            if not item["is_task_complete"]:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(item["updates"], task.context_id, task.id),
                )
                continue

            # 5. Parse response - split text and A2UI JSON
            content = item["content"]
            final_parts = []
            if "---a2ui_JSON---" in content:
                text_content, json_string = content.split("---a2ui_JSON---", 1)
                if text_content.strip():
                    final_parts.append(Part(root=TextPart(text=text_content.strip())))
                json_cleaned = json_string.strip().lstrip("```json").rstrip("```").strip()
                json_data = json.loads(json_cleaned)
                if isinstance(json_data, list):
                    for message in json_data:
                        final_parts.append(create_a2ui_part(message))
                else:
                    final_parts.append(create_a2ui_part(json_data))
            else:
                final_parts.append(Part(root=TextPart(text=content.strip())))

            await updater.update_status(
                TaskState.input_required,
                new_agent_parts_message(final_parts, task.context_id, task.id),
                final=False,
            )
            break
````

### LLM Prompt Strategy

The LLM is instructed to output a two-part response separated by `---a2ui_JSON---`:

```
Part 1: Conversational text (e.g., "Here are the results...")
---a2ui_JSON---
Part 2: A2UI JSON array of messages
```

The system prompt includes:

1. **Agent instructions** - behavioral logic for the domain
2. **UI template rules** - when to use which template
3. **UI examples** - complete A2UI JSON examples for each scenario
4. **A2UI JSON schema** - the full schema for validation

### Schema Validation (Critical Pattern)

```python
import json
import jsonschema

# Load schema and wrap in array validator
single_message_schema = json.loads(A2UI_SCHEMA)
array_schema = {"type": "array", "items": single_message_schema}

# Validate LLM output
json_data = json.loads(json_string)
jsonschema.validate(instance=json_data, schema=array_schema)
```

Always wrap the single-message schema in an array validator since the LLM returns a list of messages.

### Retry Logic

If validation fails, retry with error feedback:

```python
retry_query = f"Your previous response had an invalid JSON. Error: {error}. Please regenerate valid A2UI JSON."
```

Implement at least 1 retry (2 total attempts).

## A2UI Extension System

### Extension URI

```
https://a2ui.org/a2a-extension/a2ui/v0.8
```

### Extension MIME Type

```
application/json+a2ui
```

### Key Functions from `a2ui.extension.a2ui_extension`

```python
# Register extension in AgentCapabilities
get_a2ui_agent_extension() -> AgentExtension

# Check if client requested A2UI and activate it
try_activate_a2ui_extension(context: RequestContext) -> bool

# Create A2A DataPart from A2UI JSON dict
create_a2ui_part(a2ui_data: dict) -> Part
```

### Client Extension Request

The client sends this header to request A2UI support:

```
X-A2A-Extensions: https://a2ui.org/a2a-extension/a2ui/v0.8
```

### Standard Catalog ID

```
https://a2ui.org/specification/v0_8/standard_catalog_definition.json
```

## Client Setup (Reference)

The client shell uses:

- **@a2a-js/sdk** - A2A client SDK
- **@a2ui/lit** - Lit-based A2UI renderer
- **Vite** - Dev server
- **Lit** - Web component framework

Client fetches agent card from `{serverUrl}/.well-known/agent-card.json`, then sends messages via the A2A JSON-RPC protocol.

## Common Patterns and Gotchas

### 1. Components are a flat list, not nested

Components reference each other by string ID. The tree structure is implicit:

```json
[
  { "id": "card", "component": { "Card": { "child": "content" } } },
  {
    "id": "content",
    "component": {
      "Column": { "children": { "explicitList": ["title", "body"] } }
    }
  }
]
```

### 2. Button text requires a separate Text component

```json
[
  {
    "id": "btn-text",
    "component": { "Text": { "text": { "literalString": "Click Me" } } }
  },
  {
    "id": "btn",
    "component": {
      "Button": { "child": "btn-text", "action": { "name": "click" } }
    }
  }
]
```

### 3. TaskState controls the conversation flow

- `TaskState.input_required` - UI is displayed, waiting for user interaction (keeps conversation going)
- `TaskState.completed` - Final response, conversation can end
- `TaskState.working` - Intermediate status update

### 4. Dual UI/Text agent pattern

Always create both a UI and text agent. Use `try_activate_a2ui_extension()` to choose:

```python
use_ui = try_activate_a2ui_extension(context)
agent = self.ui_agent if use_ui else self.text_agent
```

### 5. Base URL for static assets

Store `base_url` in session state so tools can reference it:

```python
tool_context.state["base_url"] = base_url
```

Then in tools, replace hardcoded URLs with the dynamic base URL.

### 6. The `---a2ui_JSON---` delimiter

This is the convention used to separate LLM text from A2UI JSON. The agent executor splits on this delimiter to create separate TextPart and DataPart objects.

### 7. JSON cleaning

LLMs often wrap JSON in markdown code fences. Always clean:

````python
json_cleaned = json_string.strip().lstrip("```json").rstrip("```").strip()
````

### 8. Empty result handling

If the LLM returns an empty JSON list `[]`, skip creating DataParts and just return text.

### 9. CORS is required

The agent server MUST have CORS middleware since the browser client is on a different port:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 10. The `.well-known/agent-card.json` endpoint

This is automatically registered by `A2AStarletteApplication.build()`. No manual setup needed - just pass the `AgentCard` to the constructor.

## Complete A2UI JSON Example: Card with Actions

```json
[
  {
    "beginRendering": {
      "surfaceId": "review-card",
      "root": "main-card",
      "styles": { "primaryColor": "#1a73e8", "font": "Roboto" }
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "review-card",
      "components": [
        {
          "id": "main-card",
          "component": { "Card": { "child": "main-col" } }
        },
        {
          "id": "main-col",
          "component": {
            "Column": {
              "children": {
                "explicitList": [
                  "title",
                  "description",
                  "divider",
                  "actions-row"
                ]
              },
              "alignment": "stretch"
            }
          }
        },
        {
          "id": "title",
          "component": {
            "Text": { "text": { "path": "title" }, "usageHint": "h2" }
          }
        },
        {
          "id": "description",
          "component": {
            "Text": { "text": { "path": "description" }, "usageHint": "body" }
          }
        },
        {
          "id": "divider",
          "component": { "Divider": {} }
        },
        {
          "id": "actions-row",
          "component": {
            "Row": {
              "children": { "explicitList": ["approve-btn", "reject-btn"] },
              "distribution": "center"
            }
          }
        },
        {
          "id": "approve-text",
          "component": { "Text": { "text": { "literalString": "Approve" } } }
        },
        {
          "id": "approve-btn",
          "component": {
            "Button": {
              "child": "approve-text",
              "primary": true,
              "action": {
                "name": "approve",
                "context": [{ "key": "itemId", "value": { "path": "id" } }]
              }
            }
          }
        },
        {
          "id": "reject-text",
          "component": { "Text": { "text": { "literalString": "Reject" } } }
        },
        {
          "id": "reject-btn",
          "component": {
            "Button": {
              "child": "reject-text",
              "action": {
                "name": "reject",
                "context": [{ "key": "itemId", "value": { "path": "id" } }]
              }
            }
          }
        }
      ]
    }
  },
  {
    "dataModelUpdate": {
      "surfaceId": "review-card",
      "path": "/",
      "contents": [
        { "key": "id", "valueString": "PR-123" },
        { "key": "title", "valueString": "Fix authentication bug" },
        {
          "key": "description",
          "valueString": "Resolved the session timeout issue in the login flow."
        }
      ]
    }
  }
]
```

## Complete A2UI JSON Example: List with Template

```json
[
  {
    "beginRendering": {
      "surfaceId": "results",
      "root": "root-col",
      "styles": { "primaryColor": "#00897B" }
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "results",
      "components": [
        {
          "id": "root-col",
          "component": {
            "Column": {
              "children": { "explicitList": ["heading", "result-list"] }
            }
          }
        },
        {
          "id": "heading",
          "component": {
            "Text": {
              "text": { "literalString": "Search Results" },
              "usageHint": "h1"
            }
          }
        },
        {
          "id": "result-list",
          "component": {
            "List": {
              "direction": "vertical",
              "children": {
                "template": {
                  "componentId": "item-card",
                  "dataBinding": "/items"
                }
              }
            }
          }
        },
        {
          "id": "item-card",
          "component": { "Card": { "child": "item-row" } }
        },
        {
          "id": "item-row",
          "component": {
            "Row": {
              "children": { "explicitList": ["item-info", "view-btn"] },
              "alignment": "center"
            }
          }
        },
        {
          "id": "item-info",
          "weight": 1,
          "component": {
            "Column": {
              "children": { "explicitList": ["item-name", "item-desc"] }
            }
          }
        },
        {
          "id": "item-name",
          "component": {
            "Text": { "text": { "path": "name" }, "usageHint": "h3" }
          }
        },
        {
          "id": "item-desc",
          "component": { "Text": { "text": { "path": "description" } } }
        },
        {
          "id": "view-btn-text",
          "component": { "Text": { "text": { "literalString": "View" } } }
        },
        {
          "id": "view-btn",
          "component": {
            "Button": {
              "child": "view-btn-text",
              "primary": true,
              "action": {
                "name": "view_item",
                "context": [
                  { "key": "itemId", "value": { "path": "id" } },
                  { "key": "itemName", "value": { "path": "name" } }
                ]
              }
            }
          }
        }
      ]
    }
  },
  {
    "dataModelUpdate": {
      "surfaceId": "results",
      "path": "/",
      "contents": [
        {
          "key": "items",
          "valueMap": [
            {
              "key": "item1",
              "valueMap": [
                { "key": "id", "valueString": "1" },
                { "key": "name", "valueString": "First Item" },
                {
                  "key": "description",
                  "valueString": "Description of first item"
                }
              ]
            },
            {
              "key": "item2",
              "valueMap": [
                { "key": "id", "valueString": "2" },
                { "key": "name", "valueString": "Second Item" },
                {
                  "key": "description",
                  "valueString": "Description of second item"
                }
              ]
            }
          ]
        }
      ]
    }
  }
]
```
