"""A2UI v0.8 server-to-client message JSON schema.

Source: https://github.com/google/a2ui - specification/v0_8/json/server_to_client.json
"""

A2UI_SCHEMA = """{
  "title": "A2UI Message Schema",
  "description": "Describes a JSON payload for an A2UI (Agent to UI) message, which is used to dynamically construct and update user interfaces. A message MUST contain exactly ONE of the action properties: 'beginRendering', 'surfaceUpdate', 'dataModelUpdate', or 'deleteSurface'.",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "beginRendering": {
      "type": "object",
      "description": "Signals the client to begin rendering a surface with a root component and specific styles.",
      "additionalProperties": false,
      "properties": {
        "surfaceId": { "type": "string", "description": "The unique identifier for the UI surface to be rendered." },
        "catalogId": { "type": "string", "description": "The identifier of the component catalog to use for this surface." },
        "root": { "type": "string", "description": "The ID of the root component to render." },
        "styles": { "type": "object", "description": "Styling information for the UI.", "additionalProperties": true }
      },
      "required": ["root", "surfaceId"]
    },
    "surfaceUpdate": {
      "type": "object",
      "description": "Updates a surface with a new set of components.",
      "additionalProperties": false,
      "properties": {
        "surfaceId": { "type": "string", "description": "The unique identifier for the UI surface to be updated." },
        "components": {
          "type": "array",
          "description": "A list containing all UI components for the surface.",
          "minItems": 1,
          "items": {
            "type": "object",
            "description": "Represents a single component in a UI widget tree.",
            "additionalProperties": false,
            "properties": {
              "id": { "type": "string", "description": "The unique identifier for this component." },
              "weight": { "type": "number", "description": "The relative weight of this component within a Row or Column (CSS flex-grow)." },
              "component": { "type": "object", "description": "A wrapper object that MUST contain exactly one key (the component type name). The value is an object with that component's properties.", "additionalProperties": true }
            },
            "required": ["id", "component"]
          }
        }
      },
      "required": ["surfaceId", "components"]
    },
    "dataModelUpdate": {
      "type": "object",
      "description": "Updates the data model for a surface.",
      "additionalProperties": false,
      "properties": {
        "surfaceId": { "type": "string", "description": "The unique identifier for the UI surface this data model update applies to." },
        "path": { "type": "string", "description": "An optional path to a location within the data model (e.g., '/user/name'). If omitted or '/', the entire data model is replaced." },
        "contents": {
          "type": "array",
          "description": "An array of data entries. Each entry must contain a 'key' and exactly one typed 'value*' property.",
          "items": {
            "type": "object",
            "description": "A single data entry.",
            "additionalProperties": false,
            "properties": {
              "key": { "type": "string", "description": "The key for this data entry." },
              "valueString": { "type": "string" },
              "valueNumber": { "type": "number" },
              "valueBoolean": { "type": "boolean" },
              "valueMap": {
                "description": "Represents a map as an adjacency list. Items may contain nested valueMap.",
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "key": { "type": "string" },
                    "valueString": { "type": "string" },
                    "valueNumber": { "type": "number" },
                    "valueBoolean": { "type": "boolean" },
                    "valueMap": { "type": "array" }
                  },
                  "required": ["key"]
                }
              }
            },
            "required": ["key"]
          }
        }
      },
      "required": ["contents", "surfaceId"]
    },
    "deleteSurface": {
      "type": "object",
      "description": "Signals the client to delete the surface identified by 'surfaceId'.",
      "additionalProperties": false,
      "properties": {
        "surfaceId": { "type": "string", "description": "The unique identifier for the UI surface to be deleted." }
      },
      "required": ["surfaceId"]
    }
  }
}"""
