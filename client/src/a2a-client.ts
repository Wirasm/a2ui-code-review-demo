import { A2AClient } from '@a2a-js/sdk/client';
import type {
  MessageSendParams,
  Task,
  TaskStatusUpdateEvent,
  Message,
  DataPart,
  TextPart,
  Part,
} from '@a2a-js/sdk';
import type { A2UIMessage, UserAction } from './types.js';

type StreamEventData = Message | Task | TaskStatusUpdateEvent;

const A2UI_EXTENSION_URI = 'https://a2ui.org/a2a-extension/a2ui/v0.8';
const A2UI_MIME_TYPE = 'application/json+a2ui';

export interface StreamEvent {
  type: 'task' | 'status' | 'a2ui' | 'text' | 'done';
  taskId?: string;
  contextId?: string;
  state?: string;
  text?: string;
  a2uiMessages?: A2UIMessage[];
  final?: boolean;
}

function createA2UIFetch(): typeof fetch {
  return async (input, init) => {
    const headers = new Headers(init?.headers);
    headers.set('X-A2A-Extensions', A2UI_EXTENSION_URI);
    return fetch(input, { ...init, headers });
  };
}

export async function createClient(serverUrl: string): Promise<A2AClient> {
  const cardUrl = `${serverUrl}/.well-known/agent-card.json`;
  return A2AClient.fromCardUrl(cardUrl, { fetchImpl: createA2UIFetch() });
}

function extractPartsFromEvent(event: StreamEventData): {
  a2uiMessages: A2UIMessage[];
  textParts: string[];
} {
  const a2uiMessages: A2UIMessage[] = [];
  const textParts: string[] = [];

  let parts: Part[] | undefined;

  if (event.kind === 'status-update') {
    parts = (event as TaskStatusUpdateEvent).status?.message?.parts;
  } else if (event.kind === 'task') {
    parts = (event as Task).status?.message?.parts;
  } else if (event.kind === 'message') {
    parts = (event as Message).parts;
  }

  if (parts) {
    for (const part of parts) {
      if (part.kind === 'data') {
        const dp = part as DataPart;
        if (dp.metadata?.mimeType === A2UI_MIME_TYPE) {
          a2uiMessages.push(dp.data as A2UIMessage);
        }
      } else if (part.kind === 'text') {
        const tp = part as TextPart;
        if (tp.text) textParts.push(tp.text);
      }
    }
  }

  return { a2uiMessages, textParts };
}

export async function* sendMessage(
  client: A2AClient,
  text: string,
  contextId?: string,
  taskId?: string,
): AsyncGenerator<StreamEvent> {
  const messageId = crypto.randomUUID();

  const params: MessageSendParams = {
    message: {
      messageId,
      role: 'user',
      parts: [{ kind: 'text' as const, text }],
      kind: 'message' as const,
      ...(contextId ? { contextId } : {}),
      ...(taskId ? { taskId } : {}),
    },
  };

  const stream = client.sendMessageStream(params);

  for await (const event of stream) {
    if (event.kind === 'task') {
      const task = event as Task;
      yield {
        type: 'task',
        taskId: task.id,
        contextId: task.contextId,
        state: task.status?.state,
      };
      // Also extract any parts from the task
      const { a2uiMessages, textParts } = extractPartsFromEvent(event);
      if (a2uiMessages.length > 0) {
        yield { type: 'a2ui', a2uiMessages };
      }
      if (textParts.length > 0) {
        yield { type: 'text', text: textParts.join('\n') };
      }
    } else if (event.kind === 'status-update') {
      const update = event as TaskStatusUpdateEvent;
      const state = update.status?.state;

      const { a2uiMessages, textParts } = extractPartsFromEvent(event);

      if (state === 'working' && textParts.length > 0) {
        yield { type: 'status', state, text: textParts.join('\n') };
      }

      if (a2uiMessages.length > 0) {
        yield { type: 'a2ui', a2uiMessages };
      } else if (textParts.length > 0 && state !== 'working') {
        yield { type: 'text', text: textParts.join('\n') };
      }

      if (update.final) {
        yield {
          type: 'done',
          taskId: update.taskId,
          contextId: update.contextId,
          state,
          final: true,
        };
        return;
      }
    } else if (event.kind === 'message') {
      const { a2uiMessages, textParts } = extractPartsFromEvent(event);
      if (a2uiMessages.length > 0) {
        yield { type: 'a2ui', a2uiMessages };
      }
      if (textParts.length > 0) {
        yield { type: 'text', text: textParts.join('\n') };
      }
    }
  }
}

export async function* sendUserAction(
  client: A2AClient,
  action: UserAction,
  contextId: string,
  taskId: string,
): AsyncGenerator<StreamEvent> {
  const messageId = crypto.randomUUID();

  const params: MessageSendParams = {
    message: {
      messageId,
      role: 'user',
      parts: [
        {
          kind: 'data' as const,
          data: { userAction: action },
          metadata: { mimeType: A2UI_MIME_TYPE },
        },
      ],
      kind: 'message' as const,
      contextId,
      taskId,
    },
  };

  const stream = client.sendMessageStream(params);

  for await (const event of stream) {
    if (event.kind === 'task') {
      const task = event as Task;
      yield {
        type: 'task',
        taskId: task.id,
        contextId: task.contextId,
        state: task.status?.state,
      };
      const { a2uiMessages, textParts } = extractPartsFromEvent(event);
      if (a2uiMessages.length > 0) {
        yield { type: 'a2ui', a2uiMessages };
      }
      if (textParts.length > 0) {
        yield { type: 'text', text: textParts.join('\n') };
      }
    } else if (event.kind === 'status-update') {
      const update = event as TaskStatusUpdateEvent;
      const state = update.status?.state;

      const { a2uiMessages, textParts } = extractPartsFromEvent(event);

      if (state === 'working' && textParts.length > 0) {
        yield { type: 'status', state, text: textParts.join('\n') };
      }

      if (a2uiMessages.length > 0) {
        yield { type: 'a2ui', a2uiMessages };
      } else if (textParts.length > 0 && state !== 'working') {
        yield { type: 'text', text: textParts.join('\n') };
      }

      if (update.final) {
        yield {
          type: 'done',
          taskId: update.taskId,
          contextId: update.contextId,
          state,
          final: true,
        };
        return;
      }
    } else if (event.kind === 'message') {
      const { a2uiMessages, textParts } = extractPartsFromEvent(event);
      if (a2uiMessages.length > 0) {
        yield { type: 'a2ui', a2uiMessages };
      }
      if (textParts.length > 0) {
        yield { type: 'text', text: textParts.join('\n') };
      }
    }
  }
}
