import { css } from 'lit';

export const appStyles = css`
  :host {
    display: block;
    max-width: 1060px;
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
    overflow-wrap: break-word;
  }

  .a2ui-text--caption {
    font-size: 0.8rem;
    color: #666;
    margin: 0;
    overflow-wrap: break-word;
  }

  .a2ui-text--link {
    color: #1a73e8;
    text-decoration: none;
    cursor: pointer;
  }

  .a2ui-text--link:hover {
    text-decoration: underline;
  }

  .a2ui-column {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: 0;
  }

  .a2ui-row {
    display: flex;
    flex-direction: row;
    gap: 12px;
    min-width: 0;
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
    min-width: 0;
    overflow: hidden;
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
    min-width: 0;
  }

  .a2ui-list--horizontal {
    display: flex;
    flex-direction: row;
    gap: 8px;
    overflow: auto;
    min-width: 0;
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

  /* Material Icons - must be defined in shadow DOM since external stylesheets can't cross the boundary */
  .material-icons {
    font-family: 'Material Icons';
    font-weight: normal;
    font-style: normal;
    display: inline-block;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
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

  /* Slider */
  .a2ui-slider {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .a2ui-slider input[type="range"] {
    flex: 1;
    accent-color: #1a73e8;
    height: 4px;
    cursor: pointer;
  }

  .a2ui-slider__value {
    font-size: 0.8rem;
    color: #666;
    min-width: 4em;
    text-align: center;
  }

  /* TextField */
  .a2ui-textfield {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .a2ui-textfield__label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #1a1a2e;
  }

  .a2ui-textfield__input {
    padding: 8px 12px;
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    font-size: 0.875rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.15s;
  }

  .a2ui-textfield__input:focus {
    border-color: #1a73e8;
  }

  textarea.a2ui-textfield__input {
    min-height: 80px;
    resize: vertical;
  }

  /* MultipleChoice */
  .a2ui-multiple-choice {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .a2ui-choice {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border: 1px solid #d0d0d0;
    border-radius: 16px;
    cursor: pointer;
    font-size: 0.8rem;
    user-select: none;
    transition: background 0.15s, border-color 0.15s;
  }

  .a2ui-choice:has(input:checked) {
    background: #e8f0fe;
    border-color: #1a73e8;
    color: #1a73e8;
  }

  .a2ui-choice input {
    display: none;
  }

  /* Multi-surface layout */
  .surfaces-layout {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 16px;
    align-items: start;
  }

  .surfaces-main {
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-width: 0;
  }

  .surface-container {
    background: #f0f2f5;
    border-radius: 12px;
    padding: 20px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.06);
    min-width: 0;
    overflow: hidden;
  }

  .surface-container--sidebar {
    position: sticky;
    top: 24px;
  }

  @media (max-width: 700px) {
    .surfaces-layout {
      grid-template-columns: 1fr;
    }

    .surface-container--sidebar {
      position: static;
    }
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

  /* Side-by-side diff grid */
  .a2ui-diff--split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 1px;
    background: #e0e0e0;
  }

  .a2ui-diff-row {
    display: contents;
  }

  .a2ui-diff-col {
    padding: 1px 8px;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.8rem;
    white-space: pre;
    min-height: 1.5em;
    line-height: 1.5;
    background: #f6f8fa;
  }

  .a2ui-diff-col--del {
    background: #ffebe9;
    color: #cf222e;
  }

  .a2ui-diff-col--add {
    background: #dafbe1;
    color: #1a7f37;
  }

  .a2ui-diff-col--ctx {
    grid-column: 1 / -1;
    color: #656d76;
  }

  .a2ui-diff-col--empty {
    background: #f6f8fa;
  }

  /* Severity bar */
  .severity-bar {
    display: flex;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 16px;
  }

  .severity-bar__segment {
    min-width: 0;
    transition: width 0.3s ease;
  }

  .severity-bar__segment--critical {
    background: #cf222e;
  }

  .severity-bar__segment--warning {
    background: #bf8700;
  }

  .severity-bar__segment--info {
    background: #0969da;
  }

  /* Toast notification */
  .toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    z-index: 10000;
    max-width: 400px;
    animation: slideInRight 0.3s ease-out both;
  }

  .toast--hidden {
    display: none;
  }

  .toast--dismissing {
    animation: slideOutRight 0.2s ease-in forwards;
  }

  .toast__icon .material-icons {
    color: #1a7f37;
    font-size: 24px;
  }

  .toast__content {
    flex: 1;
  }

  .toast__message {
    font-size: 0.875rem;
    font-weight: 500;
    color: #1a1a2e;
  }

  .toast__link {
    font-size: 0.8rem;
    color: #1a73e8;
    text-decoration: none;
    margin-top: 4px;
    display: block;
  }

  .toast__link:hover {
    text-decoration: underline;
  }

  .toast__close {
    background: none;
    border: none;
    cursor: pointer;
    color: #666;
    padding: 4px;
  }

  .toast__close:hover {
    color: #1a1a2e;
  }

  @keyframes slideInRight {
    from { opacity: 0; transform: translateX(100px); }
    to { opacity: 1; transform: translateX(0); }
  }

  @keyframes slideOutRight {
    from { opacity: 1; transform: translateX(0); }
    to { opacity: 0; transform: translateX(100px); }
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

  /* Review history */
  .review-history {
    margin-top: 16px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 12px;
  }

  .review-history__toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    border: none;
    background: none;
    font-size: 0.875rem;
    font-weight: 600;
    color: #1a1a2e;
    padding: 0;
    font-family: inherit;
  }

  .review-history__toggle .material-icons {
    font-size: 18px;
    transition: transform 0.2s;
  }

  .review-history__list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 12px;
  }

  .review-history__item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: white;
    border-radius: 8px;
    animation: fadeInUp 0.2s ease-out both;
  }

  .review-history__item .material-icons {
    color: #1a7f37;
    font-size: 18px;
  }

  .review-history__meta {
    flex: 1;
  }

  .review-history__count {
    font-size: 0.875rem;
    font-weight: 500;
    color: #1a1a2e;
  }

  .review-history__time {
    font-size: 0.75rem;
    color: #666;
  }

  .review-history__link {
    font-size: 0.8rem;
    color: #1a73e8;
    text-decoration: none;
  }

  .review-history__link:hover {
    text-decoration: underline;
  }
`;
