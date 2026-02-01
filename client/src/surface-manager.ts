import { mergeDataModel } from './data-binding.js';
import type {
  A2UIMessage,
  BeginRendering,
  ComponentDef,
  DataModelUpdate,
  DeleteSurface,
  Surface,
  SurfaceUpdate,
} from './types.js';

export class SurfaceManager {
  surfaces = new Map<string, Surface>();
  onSurfaceReady: ((surface: Surface) => void) | null = null;

  processMessage(msg: A2UIMessage): void {
    if ('surfaceUpdate' in msg) {
      this.handleSurfaceUpdate(msg.surfaceUpdate);
    } else if ('dataModelUpdate' in msg) {
      this.handleDataModelUpdate(msg.dataModelUpdate);
    } else if ('beginRendering' in msg) {
      this.handleBeginRendering(msg.beginRendering);
    } else if ('deleteSurface' in msg) {
      this.handleDeleteSurface(msg.deleteSurface);
    }
  }

  private getOrCreateSurface(surfaceId: string): Surface {
    let surface = this.surfaces.get(surfaceId);
    if (!surface) {
      surface = {
        surfaceId,
        root: '',
        components: new Map<string, ComponentDef>(),
        data: {},
        ready: false,
      };
      this.surfaces.set(surfaceId, surface);
    }
    return surface;
  }

  private handleSurfaceUpdate(update: SurfaceUpdate): void {
    const surface = this.getOrCreateSurface(update.surfaceId);
    for (const comp of update.components) {
      surface.components.set(comp.id, comp);
    }
  }

  private handleDataModelUpdate(update: DataModelUpdate): void {
    const surface = this.getOrCreateSurface(update.surfaceId);
    surface.data = mergeDataModel(
      surface.data,
      update.path,
      update.contents,
    );
  }

  private handleBeginRendering(begin: BeginRendering): void {
    const surface = this.getOrCreateSurface(begin.surfaceId);
    surface.root = begin.root;
    surface.styles = begin.styles;
    surface.ready = true;
    this.onSurfaceReady?.(surface);
  }

  private handleDeleteSurface(del: DeleteSurface): void {
    this.surfaces.delete(del.surfaceId);
  }

  /** Process a batch of A2UI messages (the standard 3-message array). */
  processBatch(messages: A2UIMessage[]): void {
    // Process surfaceUpdate and dataModelUpdate first, beginRendering last
    const rendering: A2UIMessage[] = [];
    const others: A2UIMessage[] = [];
    for (const msg of messages) {
      if ('beginRendering' in msg) {
        rendering.push(msg);
      } else {
        others.push(msg);
      }
    }
    for (const msg of others) {
      this.processMessage(msg);
    }
    for (const msg of rendering) {
      this.processMessage(msg);
    }
  }

  getSurface(id: string): Surface | undefined {
    return this.surfaces.get(id);
  }

  getLatestReadySurface(): Surface | undefined {
    let latest: Surface | undefined;
    for (const surface of this.surfaces.values()) {
      if (surface.ready) latest = surface;
    }
    return latest;
  }

  /** Return all ready surfaces in insertion order. */
  getReadySurfaces(): Surface[] {
    const result: Surface[] = [];
    for (const surface of this.surfaces.values()) {
      if (surface.ready) result.push(surface);
    }
    return result;
  }

  /** Remove all surfaces. */
  clear(): void {
    this.surfaces.clear();
  }
}
