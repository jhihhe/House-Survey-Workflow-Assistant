import fs from 'fs-extra';
import path from 'path';
import exifr from 'exifr';

export interface DeviceStatus {
  path: string;
  name: string;
  type: 'photo' | 'vr';
  model?: string;
  capacity?: string;
}

export async function detectDevices(photoPath: string, vrPath: string): Promise<DeviceStatus[]> {
  const devices: DeviceStatus[] = [];

  // Check Photo Device
  if (photoPath && await fs.pathExists(photoPath)) {
    let driveName = path.basename(photoPath);
    
    // macOS: try to get the actual volume name if path starts with /Volumes/
    if (photoPath.startsWith('/Volumes/')) {
        const parts = photoPath.split(path.sep);
        if (parts.length >= 3) { // /Volumes/Name/...
            driveName = parts[2];
        }
    }

    let model = 'SD Card (Photo)';
    
    // Priority: Drive Name -> EXIF -> Default
    if (driveName && driveName.toLowerCase() !== 'untitled' && driveName !== '.' && driveName !== '..') {
        model = driveName;
    } else {
        const exifModel = await getCameraModel(photoPath);
        if (exifModel) model = exifModel;
    }

    devices.push({
      path: photoPath,
      name: 'SD Card (Photo)',
      type: 'photo',
      model: model,
      capacity: 'Unknown'
    });
  }

  // Check VR Device
  if (vrPath && await fs.pathExists(vrPath)) {
    let driveName = path.basename(vrPath);
    
    if (vrPath.startsWith('/Volumes/')) {
        const parts = vrPath.split(path.sep);
        if (parts.length >= 3) {
            driveName = parts[2];
        }
    }

    let model = 'SD Card (VR)';
    
    if (driveName && driveName.toLowerCase() !== 'untitled' && driveName !== '.' && driveName !== '..') {
        model = driveName;
    } else {
        const exifModel = await getCameraModel(vrPath);
        if (exifModel) model = exifModel;
    }

    devices.push({
      path: vrPath,
      name: 'SD Card (VR)',
      type: 'vr',
      model: model,
      capacity: 'Unknown'
    });
  }

  return devices;
}

async function getCameraModel(dirPath: string): Promise<string | null> {
  try {
    const files = await fs.readdir(dirPath);
    const imageExtensions = ['.jpg', '.jpeg', '.arw', '.cr2', '.nef', '.dng', '.insp'];
    
    for (const file of files) {
      if (file.startsWith('.')) continue;
      const ext = path.extname(file).toLowerCase();
      if (imageExtensions.includes(ext)) {
        const filePath = path.join(dirPath, file);
        // Only read the first 4KB is usually enough for EXIF, but exifr handles this efficiently
        const output = await exifr.parse(filePath, ['Make', 'Model']);
        if (output && output.Model) {
            return output.Model;
        }
      }
    }
  } catch (error) {
    console.error(`Error reading EXIF from ${dirPath}:`, error);
  }
  return null;
}

export async function copyFiles(
  src: string, 
  dst: string, 
  onProgress: (current: number, total: number, speed: string) => void
): Promise<{ success: boolean; error?: string; count: number }> {
  try {
    // If src is empty string, skip
    if (!src) return { success: false, error: "Source path not set", count: 0 };

    if (!await fs.pathExists(src)) {
      return { success: false, error: "Source not found", count: 0 };
    }

    await fs.ensureDir(dst);
    const files = (await fs.readdir(src)).filter(f => !f.startsWith('.'));
    const total = files.length;
    let count = 0;

    for (const file of files) {
      const srcFile = path.join(src, file);
      
      // Skip directories if we only want files
      const stat = await fs.stat(srcFile);
      if (stat.isDirectory()) continue;

      const dstFile = await resolveConflict(dst, file);
      const size = stat.size;
      const start = Date.now();

      await fs.copy(srcFile, dstFile, { overwrite: false });
      
      const duration = (Date.now() - start) / 1000; // seconds
      // Avoid division by zero
      const mb = size / 1024 / 1024;
      const speed = duration > 0.1 ? (mb / duration).toFixed(1) + " MB/s" : "瞬时";
      
      count++;
      onProgress(count, total, speed);
    }

    return { success: true, count };
  } catch (error: any) {
    return { success: false, error: error.message, count: 0 };
  }
}

async function resolveConflict(dir: string, filename: string): Promise<string> {
  let dst = path.join(dir, filename);
  if (!await fs.pathExists(dst)) return dst;

  const ext = path.extname(filename);
  const name = path.basename(filename, ext);
  let counter = 1;
  
  while (true) {
    const newName = `${name}_${counter}${ext}`;
    dst = path.join(dir, newName);
    if (!await fs.pathExists(dst)) return dst;
    counter++;
  }
}
