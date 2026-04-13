// store/layerStore.ts
import { create } from 'zustand';

interface LayerState {
  layers: string[];
  setLayers: (layers: string[]) => void;
  clearLayers: () => void;
}

interface ObjectState {
  objects: string[];
  setObjects: (objects: string[]) => void;
  clearObjects: () => void;
}

export const useLayerStore = create<LayerState>((set) => ({
  layers: [],
  setLayers: (layers) => set({ layers }),
  clearLayers: () => set({ layers: [] }),
}));

export const useObjectStore = create<ObjectState>((set) => ({
  objects: [],
  setObjects: (objects) => set({ objects }),
  clearObjects: () => set({ objects: [] }),
}));