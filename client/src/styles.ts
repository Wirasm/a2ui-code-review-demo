import { css } from 'lit';

export const appStyles = css`
  :host {
    display: block;
    max-width: 800px;
    margin: 0 auto;
    padding: 24px;
    font-family: 'Roboto', system-ui, sans-serif;
    color: #1a1a2e;
  }

  .header {
    margin-bottom: 24px;
  }

  .header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: #1a1a2e;
  }

  .header p {
    margin: 0;
    color: #666;
    font-size: 0.875rem;
  }

  .input-row {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
  }

  .input-row input {
    flex: 1;
    padding: 10px 14px;
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    font-size: 0.95rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.15s;
  }

  .input-row input:focus {
    border-color: #1a73e8;
  }

  .input-row input:disabled {
    background: #f5f5f5;
    color: #999;
  }

  .input-row button {
    padding: 10px 20px;
    background: #1a73e8;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s;
    font-family: inherit;
  }

  .input-row button:hover:not(:disabled) {
    background: #1557b0;
  }

  .input-row button:disabled {
    background: #a0c4f1;
    cursor: not-allowed;
  }

  .status {
    padding: 12px 16px;
    background: #f8f9fa;
    border-radius: 8px;
    color: #555;
    font-size: 0.875rem;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status .spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid #d0d0d0;
    border-top-color: #1a73e8;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error {
    padding: 12px 16px;
    background: #fce8e6;
    border-radius: 8px;
    color: #c5221f;
    font-size: 0.875rem;
    margin-bottom: 16px;
  }

  .text-response {
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    font-size: 0.95rem;
    line-height: 1.5;
    white-space: pre-wrap;
    margin-bottom: 16px;
  }

  /* A2UI Component Styles */
  .a2ui-text--h1 {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 8px 0;
    line-height: 1.2;
  }

  .a2ui-text--h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.3;
  }

  .a2ui-text--h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0;
    line-height: 1.3;
  }

  .a2ui-text--h4 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0;
  }

  .a2ui-text--h5 {
    font-size: 0.875rem;
    font-weight: 600;
    margin: 0;
  }

  .a2ui-text--body {
    font-size: 0.95rem;
    margin: 0;
    line-height: 1.5;
  }

  .a2ui-text--caption {
    font-size: 0.8rem;
    color: #666;
    margin: 0;
  }

  .a2ui-column {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .a2ui-row {
    display: flex;
    flex-direction: row;
    gap: 12px;
  }

  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .a2ui-card {
    border-radius: 12px;
    padding: 16px;
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
    animation: fadeInUp 0.3s ease-out both;
  }

  .a2ui-card--critical {
    border-left: 4px solid #cf222e;
  }

  .a2ui-card--warning {
    border-left: 4px solid #bf8700;
  }

  .a2ui-card--info {
    border-left: 4px solid #0969da;
  }

  .a2ui-list--vertical {
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow: auto;
  }

  .a2ui-list--horizontal {
    display: flex;
    flex-direction: row;
    gap: 8px;
    overflow: auto;
  }

  .a2ui-button {
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid #d0d0d0;
    background: transparent;
    color: #1a1a2e;
    transition: background 0.15s;
    font-family: inherit;
  }

  .a2ui-button:hover {
    background: #f0f0f0;
  }

  .a2ui-button--primary {
    background: #1a73e8;
    color: white;
    border-color: #1a73e8;
  }

  .a2ui-button--primary:hover {
    background: #1557b0;
    border-color: #1557b0;
  }

  .a2ui-icon {
    font-size: 20px;
    vertical-align: middle;
  }

  .a2ui-icon--error {
    color: #cf222e;
  }

  .a2ui-icon--warning {
    color: #bf8700;
  }

  .a2ui-icon--info {
    color: #0969da;
  }

  .a2ui-divider {
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 8px 0;
  }

  .a2ui-image {
    max-width: 100%;
    border-radius: 8px;
  }

  .a2ui-unknown {
    padding: 8px;
    background: #fff3cd;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #856404;
  }

  /* Tabs */
  .a2ui-tabs {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .a2ui-tabs__header {
    display: flex;
    gap: 0;
    border-bottom: 2px solid #e0e0e0;
    margin-bottom: 12px;
  }

  .a2ui-tabs__tab {
    padding: 10px 20px;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    font-family: inherit;
    color: #666;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: color 0.15s, border-color 0.15s;
  }

  .a2ui-tabs__tab:hover {
    color: #1a73e8;
  }

  .a2ui-tabs__tab--active {
    color: #1a73e8;
    border-bottom-color: #1a73e8;
    font-weight: 600;
  }

  .a2ui-tabs__panel {
    /* visible by default */
  }

  .a2ui-tabs__panel--hidden {
    display: none;
  }

  /* Modal */
  .a2ui-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.15s ease-out;
  }

  .a2ui-modal-content {
    background: white;
    border-radius: 12px;
    padding: 24px;
    max-width: 480px;
    width: 90%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    animation: fadeInUp 0.2s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  /* CheckBox */
  .a2ui-checkbox {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    user-select: none;
  }

  .a2ui-checkbox input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: #1a73e8;
    cursor: pointer;
    margin: 0;
  }

  .a2ui-checkbox__label {
    font-size: 0.875rem;
    color: #1a1a2e;
  }

  .surface-container {
    background: #f0f2f5;
    border-radius: 12px;
    padding: 20px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.06);
  }

  /* Diff block styling */
  .a2ui-diff {
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.8rem;
    background: #f6f8fa;
    border-radius: 6px;
    padding: 12px;
    overflow-x: auto;
    margin: 4px 0;
    line-height: 1.5;
  }

  .a2ui-diff-line {
    padding: 1px 8px;
    white-space: pre;
  }

  .a2ui-diff-line--add {
    background: #dafbe1;
    color: #1a7f37;
  }

  .a2ui-diff-line--del {
    background: #ffebe9;
    color: #cf222e;
  }

  .a2ui-diff-line--ctx {
    color: #656d76;
  }

  /* Severity count colors */
  .a2ui-count--critical {
    color: #cf222e;
  }

  .a2ui-count--warning {
    color: #bf8700;
  }

  .a2ui-count--info {
    color: #0969da;
  }

  /* Status message stack */
  .status-stack {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 16px;
  }

  .status-item {
    padding: 10px 16px;
    background: #f8f9fa;
    border-radius: 8px;
    color: #555;
    font-size: 0.875rem;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: fadeInUp 0.2s ease-out both;
  }

  .status-item--previous {
    opacity: 0.5;
    font-size: 0.8rem;
    padding: 6px 16px;
  }

  .pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #1a73e8;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 0.4; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1); }
  }

  /* Inline chat input */
  .chat-row {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #e0e0e0;
  }

  .chat-row input {
    flex: 1;
    padding: 10px 14px;
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    font-size: 0.9rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.15s;
    background: white;
  }

  .chat-row input:focus {
    border-color: #1a73e8;
  }

  .chat-row input:disabled {
    background: #f5f5f5;
    color: #999;
  }

  .chat-row button {
    padding: 10px 16px;
    background: #1a73e8;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s;
    font-family: inherit;
  }

  .chat-row button:hover:not(:disabled) {
    background: #1557b0;
  }

  .chat-row button:disabled {
    background: #a0c4f1;
    cursor: not-allowed;
  }
`;
