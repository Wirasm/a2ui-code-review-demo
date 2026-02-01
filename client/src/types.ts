// A2UI message types (server → client)
export type A2UIMessage =
  | { beginRendering: BeginRendering }
  | { surfaceUpdate: SurfaceUpdate }
  | { dataModelUpdate: DataModelUpdate }
  | { deleteSurface: DeleteSurface };

export interface BeginRendering {
  surfaceId: string;
  root: string;
  styles?: Record<string, string>;
}

export interface SurfaceUpdate {
  surfaceId: string;
  components: ComponentDef[];
}

export interface ComponentDef {
  id: string;
  weight?: number;
  component: Record<string, unknown>;
}

export interface DataModelUpdate {
  surfaceId: string;
  path: string;
  contents: DataEntry[];
}

export interface DataEntry {
  key: string;
  valueString?: string;
  valueNumber?: number;
  valueBoolean?: boolean;
  valueMap?: DataEntry[];
}

export interface DeleteSurface {
  surfaceId: string;
}

// Data binding
export type BoundValue =
  | { literalString: string }
  | { literalNumber: number }
  | { literalBoolean: boolean }
  | { path: string };

// Children
export type Children =
  | { explicitList: string[] }
  | { template: { componentId: string; dataBinding: string } };

// Button action
export interface Action {
  name: string;
  context?: Array<{ key: string; value: BoundValue }>;
}

// User action (client → server)
export interface UserAction {
  name: string;
  surfaceId: string;
  sourceComponentId: string;
  timestamp: string;
  context: Record<string, unknown>;
}

// Surface state
export interface Surface {
  surfaceId: string;
  root: string;
  components: Map<string, ComponentDef>;
  data: Record<string, unknown>;
  styles?: Record<string, string>;
  ready: boolean;
}
