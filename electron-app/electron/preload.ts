import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
  minimize: () => ipcRenderer.invoke('minimize-window'),
  maximize: () => ipcRenderer.invoke('maximize-window'),
  close: () => ipcRenderer.invoke('close-window'),
  
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings: any) => ipcRenderer.invoke('save-settings', settings),
  
  scanDevices: () => ipcRenderer.invoke('scan-devices'),
  createFolders: (data: { text: string }) => ipcRenderer.invoke('create-folders', data),
  startImport: (data: { type: 'photo' | 'vr' }) => ipcRenderer.invoke('start-import', data),
  
  onImportProgress: (callback: (data: any) => void) => {
    ipcRenderer.on('import-progress', (_, data) => callback(data));
    return () => {
      ipcRenderer.removeAllListeners('import-progress');
    };
  },

  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  openPath: (path: string) => ipcRenderer.invoke('open-path', path)
});
