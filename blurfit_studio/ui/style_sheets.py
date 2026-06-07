import os
from PyQt6.QtGui import QImage, QPainter, QColor, QPolygon
from PyQt6.QtCore import QPoint

def ensure_assets():
    """Generates down arrow triangle PNGs for QComboBox if they don't exist."""
    dir_path = os.path.dirname(os.path.abspath(__file__))
    
    # White arrow (for dark mode)
    white_path = os.path.join(dir_path, "down_arrow_white.png")
    if not os.path.exists(white_path):
        image = QImage(12, 12, QImage.Format.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0)) # transparent
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(QColor("#FFFFFF"))
        
        points = [
            QPoint(2, 4),
            QPoint(10, 4),
            QPoint(6, 9)
        ]
        painter.drawPolygon(QPolygon(points))
        painter.end()
        image.save(white_path)
        
    # Dark arrow (for light mode)
    dark_path = os.path.join(dir_path, "down_arrow_dark.png")
    if not os.path.exists(dark_path):
        image = QImage(12, 12, QImage.Format.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0)) # transparent
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#2D2D3A"))
        painter.setPen(QColor("#2D2D3A"))
        
        points = [
            QPoint(2, 4),
            QPoint(10, 4),
            QPoint(6, 9)
        ]
        painter.drawPolygon(QPolygon(points))
        painter.end()
        image.save(dark_path)
        
    return white_path, dark_path

def get_stylesheet(theme_mode="dark"):
    """
    Returns a QSS (Qt Style Sheet) string defining a premium dark or light theme
    with vibrant purple/violet accents and sleek rounded elements.
    """
    white_arrow, dark_arrow = ensure_assets()
    
    if theme_mode == "light":
        arrow_path = dark_arrow.replace("\\", "/")
        return f"""
        /* Global Styles */
        QWidget {{
            background-color: #F5F6FA;
            color: #2D2D3A;
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Helvetica, sans-serif;
            font-size: 13px;
        }}

        QMainWindow {{
            background-color: #F5F6FA;
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: #EBEBEF;
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #CCCCCC;
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #6C5CE7;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: #EBEBEF;
            height: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: #CCCCCC;
            min-width: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: #6C5CE7;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
        }}

        /* QGroupBox */
        QGroupBox {{
            background-color: #FFFFFF;
            border: 1px solid #E1E2E6;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
            color: #1A1A24;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: #1A1A24;
            background-color: #F5F6FA;
            border-radius: 3px;
        }}
        QGroupBox:disabled {{
            background-color: #FBFBFC;
            border-color: #EBEBEF;
            color: #A2A2B0;
        }}
        QGroupBox::title:disabled {{
            color: #A2A2B0;
        }}

        /* Labels */
        QLabel {{
            background-color: transparent;
            color: #5C5C6A;
        }}
        QLabel#headerLabel {{
            color: #1A1A24;
            font-size: 16px;
            font-weight: bold;
        }}
        QLabel#previewTitle {{
            color: #1A1A24;
            font-size: 14px;
            font-weight: bold;
        }}
        QLabel#errorLabel {{
            color: #D63031;
            font-size: 12px;
        }}
        QLabel:disabled {{
            color: #A2A2B0;
        }}

        /* Inputs (QLineEdit) */
        QLineEdit {{
            background-color: #F8F9FD;
            border: 1px solid #D1D2D6;
            border-radius: 6px;
            padding: 6px 10px;
            color: #2D2D3A;
            selection-background-color: #6C5CE7;
            selection-color: #FFFFFF;
        }}
        QLineEdit:focus {{
            border: 1px solid #6C5CE7;
            background-color: #FFFFFF;
        }}
        QLineEdit:read-only {{
            color: #7A7A85;
            background-color: #F1F2F6;
        }}
        QLineEdit:disabled {{
            background-color: #F1F2F6;
            border-color: #EBEBEF;
            color: #A2A2B0;
        }}

        /* ComboBox */
        QComboBox {{
            background-color: #F1F2F6;
            border: 1px solid #D1D2D6;
            border-radius: 6px;
            padding: 6px 12px;
            color: #2D2D3A;
            min-width: 100px;
        }}
        QComboBox:hover {{
            border: 1px solid #6C5CE7;
            background-color: #E4E5EA;
        }}
        QComboBox:focus {{
            border: 1px solid #6C5CE7;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
        }}
        QComboBox::down-arrow {{
            image: url({arrow_path});
            width: 10px;
            height: 10px;
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: #FFFFFF;
            border: 1px solid #D1D2D6;
            selection-background-color: #6C5CE7;
            selection-color: #FFFFFF;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 6px;
            background-color: transparent;
            color: #2D2D3A;
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: #6C5CE7;
            color: #FFFFFF;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: #6C5CE7;
            color: #FFFFFF;
        }}
        QComboBox:disabled {{
            background-color: #F1F2F6;
            border-color: #EBEBEF;
            color: #A2A2B0;
        }}

        /* Radio Buttons */
        QRadioButton {{
            background-color: transparent;
            color: #2D2D3A;
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 9px;
            border: 2px solid #A2A2B0;
            background-color: #FFFFFF;
        }}
        QRadioButton::indicator:hover {{
            border: 2px solid #6C5CE7;
        }}
        QRadioButton::indicator:checked {{
            border: 2px solid #6C5CE7;
            background-color: #6C5CE7;
            image: url(none);
            width: 10px;
            height: 10px;
            margin: 3px;
            border-radius: 5px;
            background-color: #FFFFFF;
            border: 3px solid #6C5CE7;
        }}
        QRadioButton:disabled {{
            color: #A2A2B0;
        }}
        QRadioButton::indicator:disabled {{
            border-color: #EBEBEF;
            background-color: #F1F2F6;
        }}

        /* Buttons (QPushButton) */
        QPushButton {{
            background-color: #6C5CE7;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 7px 15px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #8F7EE7;
        }}
        QPushButton:pressed {{
            background-color: #5A4CD8;
        }}
        QPushButton:disabled {{
            background-color: #E0E0E8;
            color: #A2A2B0;
            border: 1px solid #D0D0D8;
        }}

        /* Outlined Button */
        QPushButton#secondaryButton {{
            background-color: transparent;
            border: 1px solid #A2A2B0;
            color: #5C5C6A;
        }}
        QPushButton#secondaryButton:hover {{
            background-color: #E4E5EA;
            border: 1px solid #6C5CE7;
            color: #1A1A24;
        }}
        QPushButton#secondaryButton:pressed {{
            background-color: #D1D2D6;
        }}
        QPushButton#secondaryButton:disabled {{
            background-color: transparent;
            border-color: #EBEBEF;
            color: #A2A2B0;
        }}

        /* Sliders (QSlider) */
        QSlider::groove:horizontal {{
            height: 6px;
            background: #E1E2E6;
            border-radius: 3px;
        }}
        QSlider::sub-page:horizontal {{
            background: #6C5CE7;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: #FFFFFF;
            border: 2px solid #6C5CE7;
            width: 14px;
            height: 14px;
            margin-top: -5px;
            margin-bottom: -5px;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background: #6C5CE7;
            border-color: #FFFFFF;
        }}
        QSlider::groove:horizontal:disabled {{
            background: #EBEBEF;
        }}
        QSlider::sub-page:horizontal:disabled {{
            background: #D0D0D8;
        }}
        QSlider::handle:horizontal:disabled {{
            background: #D0D0D8;
            border-color: #C0C0C8;
        }}

        /* Progress Bar */
        QProgressBar {{
            background-color: #F1F2F6;
            border: 1px solid #D1D2D6;
            border-radius: 8px;
            text-align: center;
            color: #2D2D3A;
            font-weight: bold;
            height: 18px;
        }}
        QProgressBar::chunk {{
            background-color: #6C5CE7;
            border-radius: 6px;
        }}

        /* Preview Canvas Area Frame */
        QFrame#canvasFrame {{
            background-color: #F0F1F5;
            border: 1px solid #D1D2D6;
            border-radius: 8px;
        }}
        QFrame#canvasFrame:disabled {{
            background-color: #EBEBEF;
            border-color: #E1E2E6;
        }}
        """
    else:
        arrow_path = white_arrow.replace("\\", "/")
        return f"""
        /* Global Styles */
        QWidget {{
            background-color: #121212;
            color: #E0E0E0;
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Helvetica, sans-serif;
            font-size: 13px;
        }}

        QMainWindow {{
            background-color: #121212;
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: #1A1A1A;
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #3A3A3A;
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #6C5CE7;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: #1A1A1A;
            height: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: #3A3A3A;
            min-width: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: #6C5CE7;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
        }}

        /* QGroupBox */
        QGroupBox {{
            background-color: #1E1E1E;
            border: 1px solid #2D2D2D;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
            color: #FFFFFF;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: #FFFFFF;
            background-color: #121212;
            border-radius: 3px;
        }}
        QGroupBox:disabled {{
            background-color: #151515;
            border-color: #242424;
            color: #555555;
        }}
        QGroupBox::title:disabled {{
            color: #555555;
        }}

        /* Labels */
        QLabel {{
            background-color: transparent;
            color: #B3B3B3;
        }}
        QLabel#headerLabel {{
            color: #FFFFFF;
            font-size: 16px;
            font-weight: bold;
        }}
        QLabel#previewTitle {{
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
        }}
        QLabel#errorLabel {{
            color: #FF7675;
            font-size: 12px;
        }}
        QLabel:disabled {{
            color: #555555;
        }}

        /* Inputs (QLineEdit) */
        QLineEdit {{
            background-color: #1A1A1A;
            border: 1px solid #2D2D2D;
            border-radius: 6px;
            padding: 6px 10px;
            color: #FFFFFF;
            selection-background-color: #6C5CE7;
            selection-color: #FFFFFF;
        }}
        QLineEdit:focus {{
            border: 1px solid #6C5CE7;
            background-color: #202020;
        }}
        QLineEdit:read-only {{
            color: #888888;
            background-color: #151515;
        }}
        QLineEdit:disabled {{
            background-color: #151515;
            border-color: #242424;
            color: #555555;
        }}

        /* ComboBox */
        QComboBox {{
            background-color: #252525;
            border: 1px solid #3A3A3A;
            border-radius: 6px;
            padding: 6px 12px;
            color: #FFFFFF;
            min-width: 100px;
        }}
        QComboBox:hover {{
            border: 1px solid #6C5CE7;
            background-color: #2D2D2D;
        }}
        QComboBox:focus {{
            border: 1px solid #6C5CE7;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
        }}
        QComboBox::down-arrow {{
            image: url({arrow_path});
            width: 10px;
            height: 10px;
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: #252525;
            border: 1px solid #3A3A3A;
            selection-background-color: #6C5CE7;
            selection-color: #FFFFFF;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 6px;
            background-color: transparent;
            color: #FFFFFF;
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: #6C5CE7;
            color: #FFFFFF;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: #6C5CE7;
            color: #FFFFFF;
        }}
        QComboBox:disabled {{
            background-color: #161616;
            border-color: #242424;
            color: #555555;
        }}

        /* Radio Buttons */
        QRadioButton {{
            background-color: transparent;
            color: #E0E0E0;
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 9px;
            border: 2px solid #555555;
            background-color: #1E1E1E;
        }}
        QRadioButton::indicator:hover {{
            border: 2px solid #6C5CE7;
        }}
        QRadioButton::indicator:checked {{
            border: 2px solid #6C5CE7;
            background-color: #6C5CE7;
            image: url(none);
            width: 10px;
            height: 10px;
            margin: 3px;
            border-radius: 5px;
            background-color: #FFFFFF;
            border: 3px solid #6C5CE7;
        }}
        QRadioButton:disabled {{
            color: #555555;
        }}
        QRadioButton::indicator:disabled {{
            border-color: #333333;
            background-color: #151515;
        }}

        /* Buttons (QPushButton) */
        QPushButton {{
            background-color: #6C5CE7;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 7px 15px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #8F7EE7;
        }}
        QPushButton:pressed {{
            background-color: #5A4CD8;
        }}
        QPushButton:disabled {{
            background-color: #2A2A2A;
            color: #555555;
            border: 1px solid #242424;
        }}

        /* Outlined Button */
        QPushButton#secondaryButton {{
            background-color: transparent;
            border: 1px solid #555555;
            color: #E0E0E0;
        }}
        QPushButton#secondaryButton:hover {{
            background-color: #2D2D2D;
            border: 1px solid #6C5CE7;
            color: #FFFFFF;
        }}
        QPushButton#secondaryButton:pressed {{
            background-color: #1A1A1A;
        }}
        QPushButton#secondaryButton:disabled {{
            background-color: transparent;
            border-color: #242424;
            color: #555555;
        }}

        /* Sliders (QSlider) */
        QSlider::groove:horizontal {{
            height: 6px;
            background: #2D2D2D;
            border-radius: 3px;
        }}
        QSlider::sub-page:horizontal {{
            background: #6C5CE7;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: #FFFFFF;
            border: 2px solid #6C5CE7;
            width: 14px;
            height: 14px;
            margin-top: -5px;
            margin-bottom: -5px;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background: #6C5CE7;
            border-color: #FFFFFF;
        }}
        QSlider::groove:horizontal:disabled {{
            background: #1C1C1C;
        }}
        QSlider::sub-page:horizontal:disabled {{
            background: #3A3A3A;
        }}
        QSlider::handle:horizontal:disabled {{
            background: #3A3A3A;
            border-color: #444444;
        }}

        /* Progress Bar */
        QProgressBar {{
            background-color: #252525;
            border: 1px solid #3A3A3A;
            border-radius: 8px;
            text-align: center;
            color: #FFFFFF;
            font-weight: bold;
            height: 18px;
        }}
        QProgressBar::chunk {{
            background-color: #6C5CE7;
            border-radius: 6px;
        }}

        /* Preview Canvas Area Frame */
        QFrame#canvasFrame {{
            background-color: #0E0E0E;
            border: 1px solid #2D2D2D;
            border-radius: 8px;
        }}
        QFrame#canvasFrame:disabled {{
            background-color: #080808;
            border-color: #1C1C1C;
        }}
        """
