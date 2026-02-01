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
  @state() private toastMessage = '';
  @state() private toastLink = '';
  @state() private toastVisible = false;
  @state() private toastDismissing = false;

  private client: A2AClient | null = null;
  private surfaceManager = new SurfaceManager();
  private contextId: string | undefined;
  private taskId: string | undefined;
  private inputValue = '';
  private toastTimer: ReturnType<typeof setTimeout> | null = null;
  private toastDismissTimer: ReturnType<typeof setTimeout> | null = null;

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
    if (detail.name === 'toggle_finding' || detail.name === 'modal_cancel' || detail.name === 'tab_switch') {
      if (detail.name === 'toggle_finding') {
        this.updateSelectedCount(detail.surfaceId);
      }
      this.renderKey++;
      return;
    }

    if (!this.client || !this.contextId || !this.taskId) return;

    // Compute selected findings at dispatch time (data model string may be stale)
    if (detail.name === 'post_selected') {
      const surface = this.surfaceManager.getSurface(detail.surfaceId);
      if (surface) {
        detail.context.selectedFindings = JSON.stringify(this.collectSelectedFindings(surface));
      }
    }

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

  private collectSelectedFindings(surface: Surface): Array<Record<string, unknown>> {
    const findings: Array<Record<string, unknown>> = [];
    const findingsAll = surface.data.findings_all;
    if (!findingsAll || typeof findingsAll !== 'object') return findings;
    for (const fileGroup of Object.values(findingsAll as Record<string, Record<string, unknown>>)) {
      const fileFindings = fileGroup.findings;
      if (!fileFindings || typeof fileFindings !== 'object') continue;
      for (const finding of Object.values(fileFindings as Record<string, Record<string, unknown>>)) {
        if (finding.selected) {
          findings.push({
            id: finding.id,
            severity_icon: finding.severity_icon,
            file_path: finding.file_path,
            description: finding.description,
          });
        }
      }
    }
    return findings;
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
      // Snapshot the review surface before processing so we can restore it if this is a post result
      const reviewSurface = this.surfaceManager.getSurface('review');
      const snapshot = reviewSurface ? {
        components: new Map(reviewSurface.components),
        data: { ...reviewSurface.data },
        root: reviewSurface.root,
      } : null;

      this.surfaceManager.processBatch(collectedA2UI);

      // Detect post result: the review surface root changed to "result-col"
      const updatedReview = this.surfaceManager.getSurface('review');
      if (updatedReview && updatedReview.root === 'result-col' && snapshot) {
        // Extract toast data before restoring
        const message = String(updatedReview.data.result_message ?? 'Review posted');
        const link = String(updatedReview.data.result_link ?? '');

        // Restore the dashboard
        updatedReview.components = snapshot.components;
        updatedReview.data = snapshot.data;
        updatedReview.root = snapshot.root;

        // Show toast
        this.showToast(message, link);
      }

      this.activeSurfaces = this.surfaceManager.getReadySurfaces();
      this.renderKey++;
    }
  }

  private showToast(message: string, link: string): void {
    if (this.toastTimer) clearTimeout(this.toastTimer);
    if (this.toastDismissTimer) clearTimeout(this.toastDismissTimer);
    this.toastMessage = message;
    this.toastLink = link;
    this.toastVisible = true;
    this.toastDismissing = false;
    this.toastTimer = setTimeout(() => this.dismissToast(), 4000);
  }

  private dismissToast(): void {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
      this.toastTimer = null;
    }
    if (this.toastDismissTimer) clearTimeout(this.toastDismissTimer);
    this.toastDismissing = true;
    this.toastDismissTimer = setTimeout(() => {
      this.toastVisible = false;
      this.toastDismissing = false;
      this.toastDismissTimer = null;
    }, 200);
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
        (surface) => {
          const critical = parseInt(String(surface.data.critical_count ?? ''), 10) || 0;
          const warning = parseInt(String(surface.data.warning_count ?? ''), 10) || 0;
          const info = parseInt(String(surface.data.info_count ?? ''), 10) || 0;
          const total = critical + warning + info;
          return html`
            <div class="surface-container" key=${`${surface.surfaceId}-${this.renderKey}`}>
              ${total > 0 ? html`
                <div class="severity-bar">
                  <div class="severity-bar__segment severity-bar__segment--critical" style="width:${(critical / total) * 100}%"></div>
                  <div class="severity-bar__segment severity-bar__segment--warning" style="width:${(warning / total) * 100}%"></div>
                  <div class="severity-bar__segment severity-bar__segment--info" style="width:${(info / total) * 100}%"></div>
                </div>
              ` : nothing}
              ${renderComponent(surface.root, surface)}
            </div>
          `;
        },
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

      ${this.toastVisible
        ? html`
            <div class="toast${this.toastDismissing ? ' toast--dismissing' : ''}">
              <div class="toast__icon"><span class="material-icons">check_circle</span></div>
              <div class="toast__content">
                <div class="toast__message">${this.toastMessage}</div>
                ${this.toastLink
                  ? html`<a class="toast__link" href=${this.toastLink} target="_blank" rel="noopener noreferrer">View on GitHub</a>`
                  : nothing}
              </div>
              <button class="toast__close" @click=${() => this.dismissToast()}>
                <span class="material-icons">close</span>
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
