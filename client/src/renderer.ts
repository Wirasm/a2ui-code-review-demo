import { html, nothing, type TemplateResult } from 'lit';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { resolveValue, getAtPath } from './data-binding.js';
import type { Action, BoundValue, Children, Surface } from './types.js';

const DISTRIBUTION_MAP: Record<string, string> = {
  start: 'flex-start',
  center: 'center',
  end: 'flex-end',
  spaceBetween: 'space-between',
  spaceAround: 'space-around',
  spaceEvenly: 'space-evenly',
};

const ALIGNMENT_MAP: Record<string, string> = {
  start: 'flex-start',
  center: 'center',
  end: 'flex-end',
  stretch: 'stretch',
};

export function renderComponent(
  id: string,
  surface: Surface,
  scope?: string,
  animationIndex?: number,
): TemplateResult | typeof nothing {
  const def = surface.components.get(id);
  if (!def) return nothing;

  const componentEntries = Object.entries(def.component);
  if (componentEntries.length === 0) return nothing;

  const [type, props] = componentEntries[0] as [string, Record<string, unknown>];
  const weight = def.weight;
  const weightStyle = weight ? `flex: ${weight};` : '';

  let content: TemplateResult | typeof nothing;

  switch (type) {
    case 'Text':
      content = renderText(props, surface.data, scope);
      break;
    case 'Column':
      content = renderColumn(props, surface, scope);
      break;
    case 'Row':
      content = renderRow(props, surface, scope);
      break;
    case 'Card':
      content = renderCard(props, surface, scope, animationIndex);
      break;
    case 'List':
      content = renderList(props, surface, scope);
      break;
    case 'Button':
      content = renderButton(props, surface, id, scope);
      break;
    case 'Icon':
      content = renderIcon(props, surface.data, scope);
      break;
    case 'Divider':
      content = html`<hr class="a2ui-divider" />`;
      break;
    case 'Image':
      content = renderImage(props, surface.data, scope);
      break;
    case 'Tabs':
      content = renderTabs(props, surface, scope);
      break;
    case 'Modal':
      content = renderModal(props, surface, scope);
      break;
    case 'CheckBox':
      content = renderCheckBox(props, surface, id, scope);
      break;
    default:
      content = html`<div class="a2ui-unknown">[Unknown: ${type}]</div>`;
  }

  if (weightStyle) {
    return html`<div style=${weightStyle}>${content}</div>`;
  }
  return content;
}

function isDiffContent(text: string): boolean {
  if (!text.includes('\n') && !text.includes('\\n')) return false;
  // Split on actual newlines or escaped newlines
  const lines = text.includes('\n') ? text.split('\n') : text.split('\\n');
  let diffLineCount = 0;
  for (const line of lines) {
    const trimmed = line.trimStart();
    if (trimmed.startsWith('+') || trimmed.startsWith('-')) {
      diffLineCount++;
    }
    if (trimmed.length > 200) return false;
  }
  return diffLineCount >= 2;
}

function renderDiffBlock(text: string): TemplateResult {
  // Handle both real newlines and escaped \n
  const lines = text.includes('\n') ? text.split('\n') : text.split('\\n');
  const lineHtml = lines
    .map((line) => {
      const trimmed = line.trimStart();
      let cls = 'a2ui-diff-line a2ui-diff-line--ctx';
      if (trimmed.startsWith('+')) cls = 'a2ui-diff-line a2ui-diff-line--add';
      else if (trimmed.startsWith('-')) cls = 'a2ui-diff-line a2ui-diff-line--del';
      // Escape HTML entities
      const escaped = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      return `<div class="${cls}">${escaped}</div>`;
    })
    .join('');
  return html`<pre class="a2ui-diff">${unsafeHTML(lineHtml)}</pre>`;
}

function renderText(
  props: Record<string, unknown>,
  data: Record<string, unknown>,
  scope?: string,
): TemplateResult {
  const textBinding = props.text as BoundValue | undefined;
  const usageHint = (props.usageHint as string) || 'body';
  const text = textBinding ? String(resolveValue(textBinding, data, scope) ?? '') : '';

  if (usageHint === 'body' && isDiffContent(text)) {
    return renderDiffBlock(text);
  }

  return html`<div class="a2ui-text a2ui-text--${usageHint}">${text}</div>`;
}

function renderColumn(
  props: Record<string, unknown>,
  surface: Surface,
  scope?: string,
): TemplateResult {
  const children = props.children as Children | undefined;
  const alignment = ALIGNMENT_MAP[(props.alignment as string) || 'stretch'] || 'stretch';
  const distribution = DISTRIBUTION_MAP[(props.distribution as string) || ''] || '';
  const style = `align-items:${alignment};${distribution ? `justify-content:${distribution};` : ''}`;

  return html`
    <div class="a2ui-column" style=${style}>
      ${children ? renderChildren(children, surface, scope) : nothing}
    </div>
  `;
}

function renderRow(
  props: Record<string, unknown>,
  surface: Surface,
  scope?: string,
): TemplateResult {
  const children = props.children as Children | undefined;
  const distribution = DISTRIBUTION_MAP[(props.distribution as string) || ''] || '';
  const alignment = ALIGNMENT_MAP[(props.alignment as string) || 'stretch'] || 'stretch';
  const style = `align-items:${alignment};${distribution ? `justify-content:${distribution};` : ''}`;

  return html`
    <div class="a2ui-row" style=${style}>
      ${children ? renderChildren(children, surface, scope) : nothing}
    </div>
  `;
}

const SEVERITY_CARD_CLASSES: Record<string, string> = {
  error: 'a2ui-card--critical',
  warning: 'a2ui-card--warning',
  info: 'a2ui-card--info',
};

function renderCard(
  props: Record<string, unknown>,
  surface: Surface,
  scope?: string,
  animationIndex?: number,
): TemplateResult {
  const childId = props.child as string;

  // Check scoped data for severity_icon to apply colored left border
  let severityClass = '';
  if (scope) {
    const severityIcon = getAtPath(surface.data, `${scope}/severity_icon`);
    if (typeof severityIcon === 'string' && SEVERITY_CARD_CLASSES[severityIcon]) {
      severityClass = ` ${SEVERITY_CARD_CLASSES[severityIcon]}`;
    }
  }

  const delayStyle = animationIndex !== undefined
    ? `animation-delay: ${animationIndex * 0.08}s`
    : '';

  return html`
    <div class="a2ui-card${severityClass}" style=${delayStyle}>
      ${childId ? renderComponent(childId, surface, scope) : nothing}
    </div>
  `;
}

function renderList(
  props: Record<string, unknown>,
  surface: Surface,
  scope?: string,
): TemplateResult {
  const children = props.children as Children | undefined;
  const direction = (props.direction as string) || 'vertical';
  const dirClass = direction === 'horizontal' ? 'a2ui-list--horizontal' : 'a2ui-list--vertical';

  return html`
    <div class="a2ui-list ${dirClass}">
      ${children ? renderChildren(children, surface, scope) : nothing}
    </div>
  `;
}

function renderButton(
  props: Record<string, unknown>,
  surface: Surface,
  componentId: string,
  scope?: string,
): TemplateResult {
  const childId = props.child as string;
  const primary = props.primary as boolean;
  const action = props.action as Action | undefined;
  const className = primary ? 'a2ui-button a2ui-button--primary' : 'a2ui-button';

  const handleClick = () => {
    if (!action) return;
    const resolvedContext: Record<string, unknown> = {};
    if (action.context) {
      for (const item of action.context) {
        resolvedContext[item.key] = resolveValue(item.value, surface.data, scope);
      }
    }
    const event = new CustomEvent('a2ui-action', {
      bubbles: true,
      composed: true,
      detail: {
        name: action.name,
        sourceComponentId: componentId,
        surfaceId: surface.surfaceId,
        context: resolvedContext,
      },
    });
    document.dispatchEvent(event);
  };

  return html`
    <button class=${className} @click=${handleClick}>
      ${childId ? renderComponent(childId, surface, scope) : nothing}
    </button>
  `;
}

const SEVERITY_ICON_CLASSES: Record<string, string> = {
  error: 'a2ui-icon--error',
  warning: 'a2ui-icon--warning',
  info: 'a2ui-icon--info',
};

function renderIcon(
  props: Record<string, unknown>,
  data: Record<string, unknown>,
  scope?: string,
): TemplateResult {
  const nameBinding = props.name;
  let iconName: string;
  if (typeof nameBinding === 'string') {
    iconName = nameBinding;
  } else if (nameBinding && typeof nameBinding === 'object') {
    iconName = String(resolveValue(nameBinding as BoundValue, data, scope) ?? '');
  } else {
    iconName = '';
  }
  const severityClass = SEVERITY_ICON_CLASSES[iconName] || '';
  const classes = `material-icons a2ui-icon${severityClass ? ` ${severityClass}` : ''}`;
  return html`<span class=${classes}>${iconName}</span>`;
}

function renderImage(
  props: Record<string, unknown>,
  data: Record<string, unknown>,
  scope?: string,
): TemplateResult {
  const urlBinding = props.url as BoundValue | undefined;
  const fit = (props.fit as string) || 'contain';
  const url = urlBinding ? String(resolveValue(urlBinding, data, scope) ?? '') : '';
  return html`<img class="a2ui-image" src=${url} style="object-fit:${fit}" />`;
}

function renderTabs(
  props: Record<string, unknown>,
  surface: Surface,
  scope?: string,
): TemplateResult {
  const tabItems = props.tabItems as Array<{title: BoundValue; child: string}> | undefined;
  if (!tabItems || tabItems.length === 0) return html`<div class="a2ui-tabs"></div>`;

  const handleTabClick = (e: Event, index: number) => {
    // Walk up from the clicked button to find the .a2ui-tabs container
    let container = (e.target as HTMLElement).closest('.a2ui-tabs');
    if (!container) return;
    const headers = container.querySelectorAll('.a2ui-tabs__tab');
    const panels = container.querySelectorAll('.a2ui-tabs__panel');
    headers.forEach((h, i) => {
      h.classList.toggle('a2ui-tabs__tab--active', i === index);
    });
    panels.forEach((p, i) => {
      p.classList.toggle('a2ui-tabs__panel--hidden', i !== index);
    });
  };

  return html`
    <div class="a2ui-tabs">
      <div class="a2ui-tabs__header">
        ${tabItems.map((item, i) => {
          const title = item.title ? String(resolveValue(item.title, surface.data, scope) ?? '') : '';
          return html`
            <button
              class="a2ui-tabs__tab${i === 0 ? ' a2ui-tabs__tab--active' : ''}"
              @click=${(e: Event) => handleTabClick(e, i)}
            >${title}</button>
          `;
        })}
      </div>
      ${tabItems.map((item, i) => html`
        <div class="a2ui-tabs__panel${i !== 0 ? ' a2ui-tabs__panel--hidden' : ''}">
          ${item.child ? renderComponent(item.child, surface, scope) : nothing}
        </div>
      `)}
    </div>
  `;
}

function renderModal(
  props: Record<string, unknown>,
  surface: Surface,
  scope?: string,
): TemplateResult {
  const entryPointId = props.entryPointChild as string;
  const contentId = props.contentChild as string;

  const findOverlay = (el: HTMLElement): HTMLElement | null => {
    const modal = el.closest('.a2ui-modal');
    return modal ? modal.querySelector('.a2ui-modal-overlay') : null;
  };

  const openModal = (e: Event) => {
    const overlay = findOverlay(e.target as HTMLElement);
    if (overlay) overlay.style.display = 'flex';
  };

  const handleBackdropClick = (e: Event) => {
    if (e.target === e.currentTarget) {
      (e.currentTarget as HTMLElement).style.display = 'none';
    }
  };

  // Close modal on any action from within (cancel or confirm)
  const handleAction = (e: Event) => {
    const detail = (e as CustomEvent).detail;
    if (!detail?.name) return;
    const overlay = findOverlay(e.target as HTMLElement);
    if (overlay) overlay.style.display = 'none';
    // Cancel is client-only, don't propagate to server
    if (detail.name === 'modal_cancel') {
      e.stopPropagation();
    }
  };

  return html`
    <div class="a2ui-modal" @a2ui-action=${handleAction}>
      <div @click=${openModal}>
        ${entryPointId ? renderComponent(entryPointId, surface, scope) : nothing}
      </div>
      <div class="a2ui-modal-overlay" style="display:none" @click=${handleBackdropClick}>
        <div class="a2ui-modal-content">
          ${contentId ? renderComponent(contentId, surface, scope) : nothing}
        </div>
      </div>
    </div>
  `;
}

function renderCheckBox(
  props: Record<string, unknown>,
  surface: Surface,
  componentId: string,
  scope?: string,
): TemplateResult {
  const labelBinding = props.label as BoundValue | undefined;
  const valueBinding = props.value as BoundValue | undefined;
  const label = labelBinding ? String(resolveValue(labelBinding, surface.data, scope) ?? '') : '';
  const checked = valueBinding ? Boolean(resolveValue(valueBinding, surface.data, scope)) : false;

  const handleChange = (e: Event) => {
    const newChecked = (e.target as HTMLInputElement).checked;

    // Update local data model if value has a path binding
    if (valueBinding && 'path' in valueBinding) {
      const p = valueBinding.path;
      const fullPath = p.startsWith('/') ? p : (scope ? `${scope}/${p}` : p);
      const segments = fullPath.replace(/^\//, '').split('/').filter(Boolean);
      let current: Record<string, unknown> = surface.data;
      for (let i = 0; i < segments.length - 1; i++) {
        const seg = segments[i];
        if (current[seg] == null || typeof current[seg] !== 'object') {
          current[seg] = {};
        }
        current = current[seg] as Record<string, unknown>;
      }
      current[segments[segments.length - 1]] = newChecked;
    }

    // Dispatch action to server
    const event = new CustomEvent('a2ui-action', {
      bubbles: true,
      composed: true,
      detail: {
        name: 'toggle_finding',
        sourceComponentId: componentId,
        surfaceId: surface.surfaceId,
        context: {
          findingId: resolveValue({path: 'id'} as BoundValue, surface.data, scope),
          selected: newChecked,
        },
      },
    });
    document.dispatchEvent(event);
  };

  return html`
    <label class="a2ui-checkbox">
      <input type="checkbox" .checked=${checked} @change=${handleChange} />
      ${label ? html`<span class="a2ui-checkbox__label">${label}</span>` : nothing}
    </label>
  `;
}

function renderChildren(
  children: Children,
  surface: Surface,
  scope?: string,
): Array<TemplateResult | typeof nothing> {
  if ('explicitList' in children) {
    return children.explicitList.map((id) => renderComponent(id, surface, scope));
  }
  if ('template' in children) {
    return renderTemplate(children.template, surface, scope);
  }
  return [];
}

function renderTemplate(
  template: { componentId: string; dataBinding: string },
  surface: Surface,
  scope?: string,
): Array<TemplateResult | typeof nothing> {
  const bindingPath = template.dataBinding;
  // Resolve relative bindings against parent scope
  const fullPath = bindingPath.startsWith('/')
    ? bindingPath
    : (scope ? `${scope}/${bindingPath}` : `/${bindingPath}`);
  const dataAtPath = getAtPath(surface.data, fullPath);
  if (!dataAtPath || typeof dataAtPath !== 'object') return [];

  const items = Object.keys(dataAtPath as Record<string, unknown>);
  return items.map((key, index) => {
    const itemScope = `${fullPath}/${key}`;
    return renderComponent(template.componentId, surface, itemScope, index);
  });
}
