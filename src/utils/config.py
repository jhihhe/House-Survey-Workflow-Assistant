import os
import json
import platform
from pathlib import Path

class Config:
    PRICE_PER_SHOOT = 28
    
    # Default Colors (Dracula Theme)
    COLORS = {
        'bg': '#282a36',           # Background
        'fg': '#f8f8f2',           # Foreground
        'selection': '#44475a',    # Selection/Dark Background
        'comment': '#6272a4',      # Comment/Gray
        'cyan': '#8be9fd',
        'green': '#50fa7b',
        'orange': '#ffb86c',
        'pink': '#ff79c6',
        'purple': '#bd93f9',
        'red': '#ff5555',
        'yellow': '#f1fa8c'
    }

    _settings = {}
    _loaded = False

    @staticmethod
    def get_config_path():
        return os.path.expanduser("~/.fangkan_helper_config.json")

    @classmethod
    def load_settings(cls):
        path = cls.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cls._settings = json.load(f)
            except Exception:
                cls._settings = {}
        else:
            cls._settings = {}
        cls._loaded = True
        return cls._settings

    @classmethod
    def save_settings(cls):
        path = cls.get_config_path()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cls._settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @classmethod
    def get(cls, key, default=None):
        if not cls._loaded:
            cls.load_settings()
        return cls._settings.get(key, default)

    @classmethod
    def set(cls, key, value):
        if not cls._loaded:
            cls.load_settings()
        cls._settings[key] = value
        cls.save_settings()

    @classmethod
    def get_root_dir(cls):
        """Get the root working directory."""
        custom_root = cls.get("root_dir")
        if custom_root and os.path.exists(custom_root):
            return Path(custom_root)
        
        # Default defaults
        if platform.system() == 'Windows':
            default = Path(os.path.expanduser("~/Pictures/Work"))
        else:
            default = Path(os.path.expanduser("~/Pictures/工作"))
            
        # If default doesn't exist, maybe just ~/Pictures
        if not default.exists():
            # We don't create it here, just return it. The app might create it.
            pass
            
        return default

    @classmethod
    def _scan_for_folder(cls, candidates, volume_filter=None):
        """
        Scan mounted volumes for specific folder structures.
        volume_filter: optional function(volume_name) -> bool to pre-filter volumes
        """
        system = platform.system()
        found_path = None
        
        if system == 'Darwin':
            volumes_dir = "/Volumes"
            if not os.path.exists(volumes_dir):
                return None
            try:
                # List all volumes
                volumes = [os.path.join(volumes_dir, v) for v in os.listdir(volumes_dir) if not v.startswith('.')]
                
                # Sort volumes to ensure deterministic order (maybe prioritizing non-Macintosh HD?)
                # Usually external drives are what we want. "Macintosh HD" usually shouldn't have DCIM at root level accessible easily?
                # But we check specific paths.
                
                for vol in volumes:
                    if volume_filter and not volume_filter(os.path.basename(vol)):
                        continue
                        
                    for cand in candidates:
                        target = os.path.join(vol, cand)
                        if os.path.exists(target):
                            return Path(target)
            except Exception:
                pass
                
        elif system == 'Windows':
            import string
            drives = []
            try:
                import win32api
                drives = win32api.GetLogicalDriveStrings()
                drives = drives.split('\000')[:-1]
            except:
                drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:")]
            
            for drive in drives:
                # Drive is like "C:\"
                if volume_filter:
                    # Getting volume label on Windows is harder here without extra calls, ignore filter for now or implement if needed
                    pass

                for cand in candidates:
                    target = os.path.join(drive, cand)
                    if os.path.exists(target):
                        return Path(target)
                        
        return None

    @classmethod
    def get_photo_src(cls):
        """Get source directory for photos (SD Card)."""
        custom = cls.get("photo_src")
        if custom and os.path.exists(custom):
            return Path(custom)
            
        # Expanded candidates for professional cameras
        candidates = [
            "DCIM/100SIGMA", "DCIM/100CANON", "DCIM/100NIKON", "DCIM/100FUJI", 
            "DCIM/100SONY", "DCIM/100OLYMP", "DCIM/100PANA", "DCIM/100LEICA",
            "DCIM/101MSDCF", "DCIM/100MSDCF", "DCIM/Camera", 
            "DCIM/100MEDIA", "DCIM/101MEDIA", # Ricoh / Others
            "MP_ROOT/100ANV01" # Sony Video sometimes
        ]
        
        # Try to find a volume that looks like a camera
        detected = cls._scan_for_folder(candidates)
        if detected:
            return detected
            
        return Path("/Volumes/Untitled/DCIM/100SIGMA") if platform.system() == 'Darwin' else Path("D:/DCIM/100SIGMA")

    @classmethod
    def get_vr_src(cls):
        """Get source directory for VR (SD Card)."""
        custom = cls.get("vr_src")
        if custom and os.path.exists(custom):
            return Path(custom)
            
        # Expanded candidates for VR cameras (Insta360, DJI, GoPro Max, etc)
        candidates = [
            "DCIM/CAM_001", "DCIM/Camera01", "DCIM/Camera02", # Insta360
            "DCIM/PANORAMA", "DCIM/100GOPRO", "DCIM/101GOPRO", # GoPro
            "DCIM/100DJI", "DCIM/101DJI", "DCIM/DJI_001", # DJI
            "DCIM/100MEDIA" # Sometimes shared, but if Photo didn't pick it up, maybe VR will?
        ]
        
        detected = cls._scan_for_folder(candidates)
        if detected:
            return detected
            
        return Path("/Volumes/Osmo360/DCIM/CAM_001") if platform.system() == 'Darwin' else Path("E:/DCIM/CAM_001")

    @classmethod
    def get_photographer_name(cls):
        return cls.get("photographer_name", "")
