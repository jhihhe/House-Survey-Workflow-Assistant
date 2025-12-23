from pathlib import Path
import platform

class Config:
    PRICE_PER_SHOOT = 28
    
    PATHS = {
        "root": Path("/Users/mac/Pictures/工作"),
        "photo_src": Path("/Volumes/Untitled/DCIM/100SIGMA"),
        "vr_src": Path("/Volumes/Osmo360/DCIM/CAM_001"),
    }

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

    @staticmethod
    def get_fonts():
        os_type = platform.system()
        if os_type == 'Windows':
            base_font = '微软雅黑'
            mono_font = 'Consolas'
        elif os_type == 'Darwin':
            base_font = 'Helvetica'
            mono_font = 'Menlo'
        else:
            base_font = 'Sans'
            mono_font = 'Monospace'

        return {
            'body': (base_font, 11),
            'button': (base_font, 11, 'bold'),
            'header': (base_font, 20, 'bold'),
            'subheader': (base_font, 12),
            'code': (mono_font, 13),
        }
