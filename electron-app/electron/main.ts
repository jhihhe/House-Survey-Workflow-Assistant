import { app, BrowserWindow, ipcMain, shell, dialog } from 'electron';
import path from 'path';
import store from './store';
import { detectDevices, copyFiles } from './services/file-service';
import { updateTodayExcel } from './services/excel-service';
import fs from 'fs-extra';
import { exec } from 'child_process';

let mainWindow: BrowserWindow | null = null;

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    frame: false,
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#000000',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false
    },
    vibrancy: 'under-window',
    visualEffectState: 'active',
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    const indexPath = path.join(app.getAppPath(), 'dist', 'index.html');
    mainWindow.loadFile(indexPath).catch((error) => {
      console.error('loadFile-error', { indexPath, error });
    });
  }

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.webContents.on('did-fail-load', (_event, errorCode, errorDescription, validatedURL) => {
    console.error('did-fail-load', { errorCode, errorDescription, validatedURL });
    const html = `
      <html>
        <body style="margin:0;background:#030712;color:#cbd5e1;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;">
          <div style="max-width:680px;padding:28px;border:1px solid rgba(148,163,184,.2);border-radius:12px;background:rgba(2,6,23,.7)">
            <h2 style="margin:0 0 10px 0;color:#a5b4fc;">页面加载失败</h2>
            <p style="margin:0 0 8px 0;">无法加载渲染页面，请检查打包资源是否包含 dist 目录。</p>
            <p style="margin:0;font-size:12px;opacity:.8;">code: ${errorCode} | ${errorDescription}</p>
          </div>
        </body>
      </html>
    `;
    mainWindow?.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
  });
};

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

process.on('uncaughtException', (error) => {
  console.error('uncaughtException', error);
});

process.on('unhandledRejection', (reason) => {
  console.error('unhandledRejection', reason);
});

// --- IPC Handlers ---

// Window Controls
ipcMain.handle('minimize-window', () => mainWindow?.minimize());
ipcMain.handle('maximize-window', () => mainWindow?.isMaximized() ? mainWindow?.unmaximize() : mainWindow?.maximize());
ipcMain.handle('close-window', () => mainWindow?.close());

// Settings
ipcMain.handle('get-settings', () => store.store);
ipcMain.handle('save-settings', (_, settings) => store.set(settings));

// Device Detection
ipcMain.handle('scan-devices', async () => {
  const photoSrc = store.get('photo_src');
  const vrSrc = store.get('vr_src');
  // Auto-detect volumes if paths are empty? For now rely on config
  return await detectDevices(photoSrc, vrSrc);
});

// Folder Logic
ipcMain.handle('create-folders', async (_, { text }) => {
  const lines = text.split('\n').filter((l: string) => l.trim().length > 0);
  const photographer = store.get('photographer_name');
  const root = store.get('root_dir');
  
  // Create Dirs
  const today = new Date();
  const yearStr = today.getFullYear().toString();
  const monthStr = `${(today.getMonth() + 1).toString().padStart(2, '0')}月`;
  const dayStr = `${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getDate().toString().padStart(2, '0')}`;
  
  const photoBase = path.join(root, `${yearStr}相片`, monthStr, `${dayStr}${photographer}`);
  const vrBase = path.join(root, `${yearStr}VR`, monthStr, dayStr);
  
  await fs.ensureDir(photoBase);
  await fs.ensureDir(vrBase);
  
  let createdCount = 0;
  let errors: string[] = [];

  for (const line of lines) {
      const validName = line.trim().replace(/\//g, '／').replace(/\\/g, '＼');
      try {
          await fs.ensureDir(path.join(photoBase, validName));
          await fs.ensureDir(path.join(vrBase, validName));
          createdCount++;
      } catch (e: any) {
          errors.push(`Failed to create ${validName}: ${e.message}`);
      }
  }

  // Update Excel
  const excelResult = await updateTodayExcel(lines, root, photographer);
  
  return { 
    success: errors.length === 0, 
    created: createdCount, 
    errors,
    excel: excelResult,
    paths: { photo: photoBase, vr: vrBase }
  };
});

// Import Logic
ipcMain.handle('start-import', async (event, { type }) => {
  const root = store.get('root_dir');
  const src = type === 'photo' ? store.get('photo_src') : store.get('vr_src');
  
  // Construct destination: .../{MMDD}原片
  const today = new Date();
  const yearStr = today.getFullYear().toString();
  const monthStr = `${(today.getMonth() + 1).toString().padStart(2, '0')}月`;
  const dayStr = `${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getDate().toString().padStart(2, '0')}`;
  
  const folderType = type === 'photo' ? '相片' : 'VR';
  const dst = path.join(root, `${yearStr}${folderType}`, monthStr, `${dayStr}原片`);
  
  return await copyFiles(src, dst, (current, total, speed) => {
    event.sender.send('import-progress', { type, current, total, speed });
  });
});

ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow!, {
    properties: ['openDirectory']
  });
  if (result.canceled) return null;
  return result.filePaths[0];
});

ipcMain.handle('open-path', async (_, pathStr) => {
  if (!pathStr) return false;

  // If in fullscreen, exit fullscreen first to prevent Space switching which hides the app
  if (mainWindow?.isFullScreen()) {
    mainWindow.setFullScreen(false);
    // Wait for animation to complete
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  if (process.platform === 'darwin') {
    // macOS specific: use AppleScript to open and resize
    const script = `
      tell application "Finder"
        open POSIX file "${pathStr}"
        set bounds of front window to {200, 200, 1000, 800}
        activate
      end tell
    `;
    
    return new Promise((resolve) => {
      exec(`osascript -e '${script}'`, (error) => {
        if (error) {
          shell.openPath(pathStr).then(r => resolve(r === ''));
        } else {
          resolve(true);
        }
      });
    });
  }

  const result = await shell.openPath(pathStr);
  return result === ''; // Empty string means success
});
