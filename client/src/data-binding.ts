import type { BoundValue, DataEntry } from './types.js';

/** Traverse nested data by `/`-separated path. */
export function getAtPath(data: Record<string, unknown>, path: string): unknown {
  const segments = path.replace(/^\//, '').split('/').filter(Boolean);
  let current: unknown = data;
  for (const seg of segments) {
    if (current == null || typeof current !== 'object') return undefined;
    current = (current as Record<string, unknown>)[seg];
  }
  return current;
}

/** Resolve a BoundValue to a concrete value. */
export function resolveValue(
  binding: BoundValue,
  data: Record<string, unknown>,
  scope?: string,
): unknown {
  if ('literalString' in binding) return binding.literalString;
  if ('literalNumber' in binding) return binding.literalNumber;
  if ('literalBoolean' in binding) return binding.literalBoolean;
  if ('path' in binding) {
    const p = binding.path;
    // Absolute path starts with /
    if (p.startsWith('/')) return getAtPath(data, p);
    // Relative path — resolve from scope
    if (scope) return getAtPath(data, `${scope}/${p}`);
    return getAtPath(data, p);
  }
  return undefined;
}

/** Convert flat DataEntry[] adjacency list to nested object. */
export function buildDataModel(contents: DataEntry[]): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const entry of contents) {
    if (entry.valueString !== undefined) {
      result[entry.key] = entry.valueString;
    } else if (entry.valueNumber !== undefined) {
      result[entry.key] = entry.valueNumber;
    } else if (entry.valueBoolean !== undefined) {
      result[entry.key] = entry.valueBoolean;
    } else if (entry.valueMap !== undefined) {
      result[entry.key] = buildDataModel(entry.valueMap);
    }
  }
  return result;
}

/** Merge new data at the given path into the existing model. */
export function mergeDataModel(
  existing: Record<string, unknown>,
  path: string,
  contents: DataEntry[],
): Record<string, unknown> {
  const newData = buildDataModel(contents);
  if (path === '/' || path === '') {
    return { ...existing, ...newData };
  }
  const segments = path.replace(/^\//, '').split('/').filter(Boolean);
  const result = { ...existing };
  let current: Record<string, unknown> = result;
  for (let i = 0; i < segments.length - 1; i++) {
    const seg = segments[i];
    if (current[seg] == null || typeof current[seg] !== 'object') {
      current[seg] = {};
    } else {
      current[seg] = { ...(current[seg] as Record<string, unknown>) };
    }
    current = current[seg] as Record<string, unknown>;
  }
  const lastSeg = segments[segments.length - 1];
  const prev = current[lastSeg];
  if (prev != null && typeof prev === 'object') {
    current[lastSeg] = { ...(prev as Record<string, unknown>), ...newData };
  } else {
    current[lastSeg] = newData;
  }
  return result;
}
