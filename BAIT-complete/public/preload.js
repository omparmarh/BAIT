const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    openWebsite: (url) => ipcRenderer.invoke('open-website', url),
    openApp: (appName) => ipcRenderer.invoke('open-app', appName),
    getAppVersion: () => ipcRenderer.invoke('get-app-version')
});
