from PyQt6.QtGui import QColor

class ThemeColors:
    def __init__(self, bg, current, fg, comment, cyan, green, orange, pink, purple, red, yellow):
        self.BACKGROUND = bg
        self.CURRENT_LINE = current
        self.FOREGROUND = fg
        self.COMMENT = comment
        self.CYAN = cyan
        self.GREEN = green
        self.ORANGE = orange
        self.PINK = pink
        self.PURPLE = purple
        self.RED = red
        self.YELLOW = yellow

THEMES = {
    "Dracula (Official) - 德古拉(官方)": ThemeColors(
        "#282a36", "#44475a", "#f8f8f2", "#6272a4", "#8be9fd", "#50fa7b", "#ffb86c", "#ff79c6", "#bd93f9", "#ff5555", "#f1fa8c"
    ),
    "Solarized Dark (Pro) - 曝光暗色(专业)": ThemeColors(
        "#002b36", "#073642", "#839496", "#586e75", "#2aa198", "#859900", "#cb4b16", "#d33682", "#6c71c4", "#dc322f", "#b58900"
    ),
    "Monokai Pro (Spectrum) - 莫诺凯(光谱)": ThemeColors(
        "#2d2a2e", "#403e41", "#fcfcfa", "#727072", "#78dce8", "#a9dc76", "#fc9867", "#ff6188", "#ab9df2", "#ff6188", "#ffd866"
    ),
    "GitHub Dark (Dimmed) - GitHub暗色(微暗)": ThemeColors(
        "#22272e", "#2d333b", "#adbac7", "#768390", "#96d0ff", "#8ddb8c", "#eac55f", "#f47067", "#dcbdfb", "#f47067", "#d29922"
    ),
    "Cyberpunk 2077 - 赛博朋克2077": ThemeColors(
        "#020202", "#1a1a1a", "#00ff9f", "#757575", "#00e5ff", "#00ff9f", "#fcee0a", "#ff003c", "#711c91", "#ff003c", "#fcee0a"
    ),
    "Glass Morphism (Frost) - 毛玻璃(冰霜)": ThemeColors(
        "#1e1e2e", "#2a2a3c", "#f8f8f2", "#9399b2", "#89dceb", "#a6e3a1", "#fab387", "#f5c2e7", "#cba6f7", "#f38ba8", "#f9e2af"
    ),
    "Modern Dark (Stone) - 现代暗色(岩石)": ThemeColors(
        "#1f1f1f", "#2d2d2d", "#e0e0e0", "#878787", "#4daafc", "#66bb6a", "#ffa726", "#ec407a", "#ab47bc", "#ef5350", "#ffee58"
    ),
    "Midnight Blue - 午夜蓝(深海)": ThemeColors(
        "#0f172a", "#1e293b", "#e2e8f0", "#64748b", "#38bdf8", "#4ade80", "#fb923c", "#f472b6", "#a78bfa", "#f87171", "#facc15"
    ),
    "Synthwave '84 - 合成波'84(复古)": ThemeColors(
        "#262335", "#34294f", "#fff7f7", "#848bbd", "#36f9f6", "#72f1b8", "#f97e72", "#ff7edb", "#9f7efe", "#fe4450", "#fede5d"
    ),
    "Emerald Forest - 翡翠森林(自然)": ThemeColors(
        "#0f291e", "#1b4332", "#d8f3dc", "#74c69d", "#40916c", "#52b788", "#e9c46a", "#f4a261", "#9d4edd", "#e76f51", "#2a9d8f"
    ),
    "Star Destroyer HUD - 星战舰桥": ThemeColors(
        "#020617", "#0f172a", "#dbeafe", "#334155", "#38bdf8", "#22d3ee", "#fb923c", "#22d3ee", "#818cf8", "#f87171", "#facc15"
    ),
    "Radar Extreme - 极致雷达(黑绿)": ThemeColors(
        "#000500", "#001a00", "#33ff33", "#004d00", "#00ff00", "#00ff00", "#99ff99", "#33cc33", "#00cc00", "#ff3333", "#ccff00"
    ),
    "MacOS Light - MacOS浅色(简洁)": ThemeColors(
        "#ffffff", "#f0f0f5", "#333333", "#8e8e93", "#007aff", "#34c759", "#ff9500", "#ff2d55", "#af52de", "#ff3b30", "#ffcc00"
    )
}

def get_stylesheet(theme_name="Dracula (Official) - 德古拉(官方)"):
    t = THEMES.get(theme_name, THEMES["Dracula (Official) - 德古拉(官方)"])
    
    # Base transparency for glass effect
    # We use rgba in the theme definition for Glass Morphism
    
    return f"""
    QWidget {{
        background-color: transparent;
        color: {t.FOREGROUND};
        font-family: "PingFang SC", "Hiragino Sans GB", "Helvetica Neue", "Microsoft YaHei";
        font-size: 14px;
    }}
    
    QMainWindow {{
        background-color: qradialgradient(cx:0.5, cy:-0.1, radius:1.2, stop:0 {t.CURRENT_LINE}, stop:0.45 {t.BACKGROUND}, stop:1 #000000);
    }}
    
    /* GroupBox: Card-like Look */
    QGroupBox {{
        border: 1px solid {t.CYAN};
        border-radius: 16px;
        margin-top: 0px;
        padding-top: 10px;
        font-weight: bold;
        color: {t.PURPLE};
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(4,12,24,210), stop:1 rgba(4,10,20,180));
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 16px;
        top: 10px;
        padding: 0 5px;
        background-color: transparent;
        color: {t.PURPLE};
    }}

    QStatusBar {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #050d18, stop:1 #040b14);
        border-top: 1px solid {t.CYAN};
    }}

    /* Inputs: Modern & Clean */
    QLineEdit, QTextEdit {{
        background-color: {t.CURRENT_LINE};
        color: {t.FOREGROUND};
        border: 1px solid {t.COMMENT};
        border-radius: 10px;
        padding: 12px;
        selection-background-color: {t.PINK};
        font-family: "Menlo", "Monaco";
        font-size: 14px;
        line-height: 1.5;
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 1px solid {t.PURPLE};
        background-color: {t.CURRENT_LINE};
    }}

    QTextEdit#starwars_console {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #06111d, stop:0.4 #071522, stop:1 #03070f);
        border: 1px solid {t.CYAN};
        border-radius: 12px;
        font-family: "Menlo", "Eurostile", "Bank Gothic";
        font-size: 13px;
        letter-spacing: 0.07em;
        line-height: 1.65;
        padding-top: 10px;
        padding-bottom: 10px;
        selection-background-color: {t.PURPLE};
        color: {t.FOREGROUND};
    }}
    QTextEdit#starwars_console:focus {{
        border: 1px solid {t.YELLOW};
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #081728, stop:1 #050a12);
    }}
    
    /* Secondary Buttons (Clear, Open, etc.) */
    QPushButton {{
        background-color: {t.CURRENT_LINE};
        color: {t.FOREGROUND};
        border: 1px solid {t.COMMENT};
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {t.COMMENT};
        border: 1px solid {t.PURPLE};
    }}
    QPushButton:pressed {{
        background-color: {t.PURPLE};
        color: {t.BACKGROUND};
    }}
    
    /* Primary Action Buttons */
    QPushButton#btn_create {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.PURPLE}, stop:1 {t.PINK});
        color: {t.BACKGROUND if theme_name != 'MacOS Light' else '#fff'};
        font-size: 16px;
        font-weight: bold;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid {t.CYAN};
    }}
    QPushButton#btn_create:hover {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.PINK}, stop:1 {t.PURPLE});
    }}
    
    QPushButton#btn_import {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.PINK}, stop:1 {t.RED});
        color: {t.BACKGROUND if theme_name != 'MacOS Light' else '#fff'};
        font-size: 16px;
        font-weight: bold;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid {t.CYAN};
    }}
    QPushButton#btn_import:hover {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.RED}, stop:1 {t.PINK});
    }}

    /* Progress Bar: Modern */
    QProgressBar {{
        border: none;
        background-color: {t.CURRENT_LINE};
        border-radius: 6px;
        height: 18px;
        text-align: center;
        color: {t.FOREGROUND};
        font-weight: bold;
    }}
    QProgressBar::chunk {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.GREEN}, stop:1 {t.CYAN});
        border-radius: 6px;
    }}
    
    /* Labels */
    QLabel#header_title {{
        font-size: 26px;
        font-weight: 800;
        color: {t.PINK};
        background-color: transparent;
        font-family: "PingFang SC", "Hiragino Sans GB", "Helvetica Neue";
    }}
    QLabel#header_subtitle {{
        font-size: 14px;
        color: {t.PURPLE};
        font-style: italic;
        background-color: transparent;
        margin-bottom: 10px;
    }}
    QLabel#stats_label {{
        color: {t.CYAN};
        font-weight: bold;
        background-color: transparent;
        padding: 4px;
    }}
    
    /* ScrollBar: Minimalist */
    QScrollBar:vertical {{
        border: none;
        background: {t.BACKGROUND};
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {t.COMMENT};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* ComboBox */
    QComboBox {{
        background-color: {t.CURRENT_LINE};
        border: 1px solid {t.COMMENT};
        border-radius: 6px;
        padding: 5px;
        color: {t.FOREGROUND};
    }}
    QComboBox::drop-down {{
        border: 0px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {t.CURRENT_LINE};
        selection-background-color: {t.PURPLE};
        color: {t.FOREGROUND};
    }}
    
    /* Status Labels */
    QLabel#status_hud_scan, QLabel#status_hud_ok, QLabel#status_hud_warn, QLabel#status_hud_err {{
        border: 1px solid {t.CYAN};
        border-radius: 8px;
        padding: 4px 10px;
        background-color: rgba(2, 12, 24, 180);
        font-family: "Menlo", "Eurostile";
        font-weight: 700;
        letter-spacing: 0.08em;
    }}
    QLabel#status_hud_scan {{
        color: {t.CYAN};
    }}
    QLabel#status_hud_ok {{
        color: {t.GREEN};
        border-color: {t.GREEN};
    }}
    QLabel#status_hud_warn {{
        color: {t.YELLOW};
        border-color: {t.YELLOW};
    }}
    QLabel#status_hud_err {{
        color: {t.RED};
        border-color: {t.RED};
    }}
    """
