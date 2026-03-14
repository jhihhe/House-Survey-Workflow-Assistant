from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from src.ui.styles import THEMES

class FolderHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, theme_name="Dracula (Official) - 德古拉(官方)"):
        super().__init__(parent)
        self.theme_name = theme_name
        self.update_rules()

    def set_theme(self, theme_name):
        self.theme_name = theme_name
        self.update_rules()
        self.rehighlight()

    def update_rules(self):
        t = THEMES.get(self.theme_name, THEMES["Dracula (Official) - 德古拉(官方)"])
        self.rules = []

        # 0. Catch-all for Chinese Characters (General Text / Community Name) -> Pink
        # This acts as a base layer for unclassified Chinese text
        fmt_cn = QTextCharFormat()
        fmt_cn.setForeground(QColor(t.PINK))
        fmt_cn.setFontWeight(QFont.Weight.Medium)
        self.rules.append((QRegularExpression(r'[\u4e00-\u9fa5]+'), fmt_cn))

        # 1. Index (e.g., "1.", "2、") -> Orange
        fmt_index = QTextCharFormat()
        fmt_index.setForeground(QColor(t.ORANGE))
        fmt_index.setFontWeight(QFont.Weight.Bold)
        self.rules.append((QRegularExpression(r'^\s*(\d+[\.、])'), fmt_index))

        # 2. Broker Name (First word after index) -> Yellow
        # Matches: Index -> Spaces -> (Broker Name)
        fmt_name = QTextCharFormat()
        fmt_name.setForeground(QColor(t.YELLOW))
        fmt_name.setFontWeight(QFont.Weight.Bold)
        # Capture group 1 is the name
        self.rules.append((QRegularExpression(r'^\s*\d+[\.、]\s*([^\s]+)'), fmt_name))

        # 3. HS Code (e.g., "HS123456") -> Purple
        fmt_code = QTextCharFormat()
        fmt_code.setForeground(QColor(t.PURPLE))
        fmt_code.setFontWeight(QFont.Weight.Bold)
        fmt_code.setFontLetterSpacing(110)
        self.rules.append((QRegularExpression(r'(HS\d+)'), fmt_code))

        # 4. Shop (e.g., "XX店") -> Green
        # Matches any non-whitespace sequence ending with "店"
        fmt_shop = QTextCharFormat()
        fmt_shop.setForeground(QColor(t.GREEN))
        fmt_shop.setFontWeight(QFont.Weight.Bold)
        self.rules.append((QRegularExpression(r'(\S+店)'), fmt_shop))

        # 5. Direction (e.g., "北", "东南") -> Red
        # Only matches if surrounded by whitespace or boundaries
        fmt_dir = QTextCharFormat()
        fmt_dir.setForeground(QColor(t.RED))
        fmt_dir.setFontWeight(QFont.Weight.ExtraBold)
        # Capture group 1 is the direction
        self.rules.append((QRegularExpression(r'(?:^|\s)([东南西北]+)(?:\s|$)'), fmt_dir))

        # 6. Room Number (e.g., "A-2311", "B53049", "9-2-603") -> Cyan
        # Matches alphanumeric sequences with optional dashes
        fmt_room = QTextCharFormat()
        fmt_room.setForeground(QColor(t.CYAN))
        fmt_room.setFontWeight(QFont.Weight.Bold)
        # We need to be careful not to match HS code parts or simple words
        # HS code is already matched above.
        # Let's target things that look like room numbers:
        # - Contains digits
        # - Can contain letters (A-Z) and dashes
        # - Is NOT "HS..."
        # Regex: \b(?!HS)[A-Za-z0-9\-]*\d+[A-Za-z0-9\-]*\b
        self.rules.append((QRegularExpression(r'\b(?!HS)[A-Za-z0-9\-]*\d+[A-Za-z0-9\-]*\b'), fmt_room))
        
        # 7. Separators -> Comment Color
        fmt_sep = QTextCharFormat()
        fmt_sep.setForeground(QColor(t.COMMENT))
        self.rules.append((QRegularExpression(r'[\-\|\,]'), fmt_sep))

    def highlightBlock(self, text):
        for pattern, format in self.rules:
            expression = pattern.globalMatch(text)
            while expression.hasNext():
                match = expression.next()
                # If regex has capturing groups (like the direction one), use the specific group
                # capturing group 1 is usually what we want if we used (?:...) wrapper
                if match.lastCapturedIndex() >= 1:
                    self.setFormat(match.capturedStart(1), match.capturedLength(1), format)
                else:
                    self.setFormat(match.capturedStart(), match.capturedLength(), format)
