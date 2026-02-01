import { LitElement, html, nothing } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import type { A2AClient } from '@a2a-js/sdk/client';
import { createClient, sendMessage, sendUserAction, type StreamEvent } from '../a2a-client.js';
import { SurfaceManager } from '../surface-manager.js';
import { renderComponent } from '../renderer.js';
import type { A2UIMessage, Surface, UserAction } from '../types.js';
import { appStyles } from '../styles.js';

const SERVER_URL = 'http://localhost:10002';

@customElement('app-shell')
export class AppShell extends LitElement {
  static override styles = appStyles;

  @state() private loading = false;
  @state() private statusText = '';
  @state() private statusHistory: string[] = [];
  @state() private errorText = '';
  @state() private textResponse = '';
  @state() private activeSurfaces: Surface[] = [];
  @state() private renderKey = 0;

  @state() private chatInput = '';

  private client: A2AClient | null = null;
  private surfaceManager = new SurfaceManager();
  private contextId: string | undefined;
  private taskId: string | undefined;
  private inputValue = '';

  override connectedCallback(): void {
    super.connectedCallback();
    document.addEventListener('a2ui-action', this.handleA2UIAction as unknown as EventListener);
  }

  override disconnectedCallback(): void {
    super.disconnectedCallback();
    document.removeEventListener('a2ui-action', this.handleA2UIAction as unknown as EventListener);
  }

  private handleA2UIAction = async (e: CustomEvent) => {
    const detail = e.detail as {
      name: string;
      sourceComponentId: string;
      surfaceId: string;
      context: Record<string, unknown>;
    };

    // Client-only actions that don't need a server round-trip
    if (detail.name === 'toggle_finding' || detail.name === 'modal_cancel') {
      if (detail.name === 'toggle_finding') {
        this.updateSelectedCount(detail.surfaceId);
      }
      this.renderKey++;
      return;
    }

    if (!this.client || !this.contextId || !this.taskId) return;

    const action: UserAction = {
      name: detail.name,
      surfaceId: detail.surfaceId,
      sourceComponentId: detail.sourceComponentId,
      timestamp: new Date().toISOString(),
      context: detail.context,
    };

    this.loading = true;
    this.statusText = 'Processing action...';
    this.statusHistory = [];
    this.errorText = '';
    this.textResponse = '';

    try {
      const stream = sendUserAction(this.client, action, this.contextId, this.taskId);
      await this.processStream(stream);
    } catch (err) {
      this.errorText = `Action failed: ${err instanceof Error ? err.message : String(err)}`;
    } finally {
      this.loading = false;
      this.statusText = '';
      this.statusHistory = [];
    }
  };

  private updateSelectedCount(surfaceId: string): void {
    const surface = this.surfaceManager.getSurface(surfaceId);
    if (!surface) return;

    // Count selected findings across all file groups in findings_all
    let count = 0;
    const findingsAll = surface.data.findings_all;
    if (findingsAll && typeof findingsAll === 'object') {
      for (const fileGroup of Object.values(findingsAll as Record<string, Record<string, unknown>>)) {
        const findings = fileGroup.findings;
        if (findings && typeof findings === 'object') {
          for (const finding of Object.values(findings as Record<string, Record<string, unknown>>)) {
            if (finding.selected) count++;
          }
        }
      }
    }

    surface.data.post_selected_label = `Post Selected (${count})`;
    surface.data.modal_message = `${count} finding${count !== 1 ? 's' : ''} will be posted as inline comments on the PR.`;
  }

  private async handleSubmit(): Promise<void> {
    const input = this.inputValue.trim();
    if (!input) return;

    this.loading = true;
    this.statusText = 'Connecting to agent...';
    this.statusHistory = [];
    this.errorText = '';
    this.textResponse = '';
    this.surfaceManager.clear();
    this.activeSurfaces = [];

    try {
      if (!this.client) {
        this.client = await createClient(SERVER_URL);
      }

      this.statusText = 'Analyzing...';

      const stream = sendMessage(this.client, input, this.contextId, this.taskId);
      await this.processStream(stream);
    } catch (err) {
      this.errorText = `Failed: ${err instanceof Error ? err.message : String(err)}`;
    } finally {
      this.loading = false;
      this.statusText = '';
      this.statusHistory = [];
    }
  }

  private async processStream(stream: AsyncGenerator<StreamEvent>): Promise<void> {
    const collectedA2UI: A2UIMessage[] = [];

    for await (const event of stream) {
      switch (event.type) {
        case 'task':
          if (event.taskId) this.taskId = event.taskId;
          if (event.contextId) this.contextId = event.contextId;
          if (event.a2uiMessages) collectedA2UI.push(...event.a2uiMessages);
          break;
        case 'status':
          if (event.text) {
            if (this.statusText && this.statusText !== event.text) {
              this.statusHistory = [...this.statusHistory, this.statusText];
            }
            this.statusText = event.text;
          }
          break;
        case 'a2ui':
          if (event.a2uiMessages) collectedA2UI.push(...event.a2uiMessages);
          break;
        case 'text':
          if (event.text) this.textResponse = event.text;
          break;
        case 'done':
          if (event.taskId) this.taskId = event.taskId;
          if (event.contextId) this.contextId = event.contextId;
          break;
      }
    }

    if (collectedA2UI.length > 0) {
      this.surfaceManager.processBatch(collectedA2UI);
      this.activeSurfaces = this.surfaceManager.getReadySurfaces();
      this.renderKey++;
    }
  }

  private async handleChat(): Promise<void> {
    const input = this.chatInput.trim();
    if (!input || !this.client || !this.contextId || !this.taskId) return;

    this.chatInput = '';
    this.loading = true;
    this.statusText = 'Processing...';
    this.statusHistory = [];
    this.errorText = '';
    this.textResponse = '';

    try {
      const stream = sendMessage(this.client, input, this.contextId, this.taskId);
      await this.processStream(stream);
    } catch (err) {
      this.errorText = `Failed: ${err instanceof Error ? err.message : String(err)}`;
    } finally {
      this.loading = false;
      this.statusText = '';
      this.statusHistory = [];
    }
  }

  private onInputChange(e: Event): void {
    this.inputValue = (e.target as HTMLInputElement).value;
  }

  private onKeyDown(e: KeyboardEvent): void {
    if (e.key === 'Enter' && !this.loading) {
      this.handleSubmit();
    }
  }

  private onChatInput(e: Event): void {
    this.chatInput = (e.target as HTMLInputElement).value;
  }

  private onChatKeyDown(e: KeyboardEvent): void {
    if (e.key === 'Enter' && !this.loading) {
      this.handleChat();
    }
  }

  override render() {
    return html`
      <div class="header">
        <h1>Code Review Agent</h1>
        <p>Enter a GitHub PR URL to get an AI-powered code review</p>
      </div>

      <div class="input-row">
        <input
          type="text"
          placeholder="https://github.com/owner/repo/pull/123"
          .value=${this.inputValue}
          @input=${this.onInputChange}
          @keydown=${this.onKeyDown}
          ?disabled=${this.loading}
        />
        <button @click=${this.handleSubmit} ?disabled=${this.loading}>
          Review
        </button>
      </div>

      ${this.loading
        ? html`
            <div class="status-stack">
              ${this.statusHistory.map(
                (msg) => html`<div class="status-item status-item--previous">${msg}</div>`,
              )}
              <div class="status-item">
                <span class="pulse-dot"></span>${this.statusText}
              </div>
            </div>
          `
        : nothing}

      ${this.errorText
        ? html`<div class="error">${this.errorText}</div>`
        : nothing}

      ${this.textResponse && this.activeSurfaces.length === 0
        ? html`<div class="text-response">${this.textResponse}</div>`
        : nothing}

      ${this.activeSurfaces.map(
        (surface) => html`
          <div class="surface-container" key=${`${surface.surfaceId}-${this.renderKey}`}>
            ${renderComponent(surface.root, surface)}
          </div>
        `,
      )}

      ${this.activeSurfaces.length > 0
        ? html`
            <div class="chat-row">
              <input
                type="text"
                placeholder="Ask about this review..."
                .value=${this.chatInput}
                @input=${this.onChatInput}
                @keydown=${this.onChatKeyDown}
                ?disabled=${this.loading}
              />
              <button @click=${this.handleChat} ?disabled=${this.loading || !this.chatInput.trim()}>
                Send
              </button>
            </div>
          `
        : nothing}
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'app-shell': AppShell;
  }
}
