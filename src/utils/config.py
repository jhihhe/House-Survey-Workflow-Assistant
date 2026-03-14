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
    def get_photo_src(cls):
        """Get source directory for photos (SD Card)."""
        custom = cls.get("photo_src")
        if custom and os.path.exists(custom):
            return Path(custom)
        # Default fallbacks could be added here if needed
        return Path("/Volumes/Untitled/DCIM/100SIGMA") if platform.system() == 'Darwin' else Path("D:/DCIM/100SIGMA")

    @classmethod
    def get_vr_src(cls):
        """Get source directory for VR (SD Card)."""
        custom = cls.get("vr_src")
        if custom and os.path.exists(custom):
            return Path(custom)
        return Path("/Volumes/Osmo360/DCIM/CAM_001") if platform.system() == 'Darwin' else Path("E:/DCIM/CAM_001")

    @classmethod
    def get_photographer_name(cls):
        return cls.get("photographer_name", "")
