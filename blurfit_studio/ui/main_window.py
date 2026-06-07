import os
import sys
import subprocess
from PyQt6.QtCore import QUrl, Qt, QFileInfo, QSettings
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QFileDialog, QMessageBox, 
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QComboBox, QSlider, QRadioButton, QButtonGroup, QProgressBar, 
    QGroupBox, QStyle, QStyleOptionSlider, QAbstractButton
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from blurfit_studio.ui.preview import PreviewContainer
from blurfit_studio.core import video_worker

def format_time(ms):
    """Formats milliseconds into MM:SS format."""
    s = ms // 1000
    m = s // 60
    s = s % 60
    return f"{m:02d}:{s:02d}"

def open_file_in_explorer(file_path):
    """Opens Windows File Explorer and selects the generated file."""
    if sys.platform == "win32":
        norm_path = os.path.normpath(file_path)
        if os.path.exists(norm_path):
            subprocess.run(['explorer', '/select,', norm_path])
        else:
            dir_path = os.path.dirname(norm_path)
            if os.path.exists(dir_path):
                os.startfile(dir_path)
    else:
        # Cross-platform fallback for opening the folder
        dir_path = os.path.dirname(file_path)
        if os.path.exists(dir_path):
            if sys.platform == "darwin":
                subprocess.run(["open", dir_path])
            else: # linux
                subprocess.run(["xdg-open", dir_path])

def normalize_path_display(path):
    """Normalizes the path to use forward slashes for clean and consistent UI display."""
    if not path:
        return ""
    return os.path.normpath(path).replace("\\", "/")

def create_social_icon(platform):
    """Programmatically draws social media brand icons on a QPixmap."""
    pixmap = QPixmap(20, 20)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    if platform == "tiktok":
        # TikTok black background
        painter.setBrush(QBrush(QColor("#000000")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 20, 20, 4, 4)
        
        # Draw music note 'd' glyph with cyan & red offsets
        painter.setPen(QPen(QColor("#25F4EE"), 2)) # Cyan
        painter.drawLine(9, 4, 9, 12)
        painter.drawEllipse(6, 10, 3, 3)
        painter.drawLine(9, 4, 13, 6)
        
        painter.setPen(QPen(QColor("#FE2C55"), 2)) # Magenta/Red
        painter.drawLine(10, 5, 10, 13)
        painter.drawEllipse(7, 11, 3, 3)
        painter.drawLine(10, 5, 14, 7)
        
    elif platform == "youtube":
        # YouTube Red Rounded Rect + White Play Triangle
        painter.setBrush(QBrush(QColor("#FF0000")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 2, 20, 16, 4, 4)
        
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        path = QPainterPath()
        path.moveTo(8, 7)
        path.lineTo(13, 10)
        path.lineTo(8, 13)
        path.closeSubpath()
        painter.drawPath(path)
        
    elif platform == "instagram":
        # Instagram Colorful Brand Gradient
        gradient = QLinearGradient(0, 20, 20, 0)
        gradient.setColorAt(0.0, QColor("#FCAF45"))
        gradient.setColorAt(0.5, QColor("#E1306C"))
        gradient.setColorAt(1.0, QColor("#C13584"))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 20, 20, 5, 5)
        
        # White Camera Outlines
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        painter.drawRoundedRect(4, 4, 12, 12, 3, 3)
        painter.drawEllipse(7, 7, 6, 6)
        
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(13, 5, 2, 2)
        
    else: # "classic"
        # Gray frame with inner dash rectangle representing aspect borders
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#888888"), 1.5))
        painter.drawRoundedRect(1, 2, 18, 16, 2, 2)
        
        pen = QPen(QColor("#CCCCCC"), 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(4, 5, 12, 10)
        
    painter.end()
    return QIcon(pixmap)


class PlayPauseButton(QAbstractButton):
    """
    Custom QPainter-drawn Play/Pause button that ensures clean centering
    and high visual consistency with our QSS dark mode.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.is_dark = True
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none; padding: 0px;")
        
    def set_playing(self, playing):
        self.is_playing = playing
        self.update()
        
    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine state colors based on mouse interactions and enabled state
        is_hover = self.underMouse()
        is_pressed = self.isDown()
        is_disabled = not self.isEnabled()
        
        # Check if background is dark
        is_dark = self.is_dark
        
        if is_dark:
            if is_disabled:
                bg_color = QColor("#2A2A2A")
                border_color = QColor("#242424")
                icon_color = QColor("#555555")
            else:
                bg_color = QColor("#6C5CE7") if is_hover else QColor("#2D2D2D")
                border_color = QColor("#6C5CE7") if is_hover else QColor("#3A3A3A")
                if is_pressed:
                    bg_color = QColor("#5A4CD8")
                    border_color = QColor("#5A4CD8")
                icon_color = QColor("#FFFFFF")
        else: # light theme
            if is_disabled:
                bg_color = QColor("#E0E0E8")
                border_color = QColor("#D0D0D8")
                icon_color = QColor("#A2A2B0")
            else:
                bg_color = QColor("#6C5CE7") if is_hover else QColor("#FFFFFF")
                border_color = QColor("#6C5CE7") if is_hover else QColor("#D1D2D6")
                if is_pressed:
                    bg_color = QColor("#5A4CD8")
                    border_color = QColor("#5A4CD8")
                icon_color = QColor("#FFFFFF") if is_hover else QColor("#2D2D3A")
            
        # Draw background circle
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawEllipse(1, 1, 34, 34)
        
        # Draw play/pause icon
        painter.setBrush(QBrush(icon_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        if not self.is_playing:
            # Draw triangle (play)
            path = QPainterPath()
            path.moveTo(14, 11)
            path.lineTo(24, 18)
            path.lineTo(14, 25)
            path.closeSubpath()
            painter.drawPath(path)
        else:
            # Draw two bars (pause)
            painter.drawRect(13, 11, 3, 14)
            painter.drawRect(20, 11, 3, 14)
            
        painter.end()


class VolumeButton(QAbstractButton):
    """
    Custom QPainter-drawn Volume button that replaces Unicode characters
    with a vector speaker icon, indicating mute and volume levels dynamically.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_muted = False
        self.volume_level = 70 # 0 to 100
        self.is_dark = True
        self.setStyleSheet("background: transparent; border: none; padding: 0px;")
        
    def set_muted(self, muted):
        self.is_muted = muted
        self.update()
        
    def set_volume_level(self, level):
        self.volume_level = level
        self.update()
        
    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_hover = self.underMouse()
        is_pressed = self.isDown()
        is_disabled = not self.isEnabled()
        
        # Check if background is dark
        is_dark = self.is_dark
        
        if is_dark:
            if is_disabled:
                bg_color = QColor("transparent")
                border_color = QColor("#242424")
                icon_color = QColor("#555555")
            else:
                bg_color = QColor("#2D2D2D") if is_hover else QColor("transparent")
                border_color = QColor("#6C5CE7") if is_hover else QColor("#555555")
                if is_pressed:
                    bg_color = QColor("#1A1A1A")
                icon_color = QColor("#FFFFFF")
        else: # light theme
            if is_disabled:
                bg_color = QColor("transparent")
                border_color = QColor("#EBEBEF")
                icon_color = QColor("#A2A2B0")
            else:
                bg_color = QColor("#E4E5EA") if is_hover else QColor("transparent")
                border_color = QColor("#6C5CE7") if is_hover else QColor("#CCCCCC")
                if is_pressed:
                    bg_color = QColor("#D1D2D6")
                icon_color = QColor("#2D2D3A")
            
        # Draw background rect
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(1, 1, 28, 28, 6, 6)
        
        # Draw speaker icon
        painter.setBrush(QBrush(icon_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 1. Speaker body
        painter.drawRect(7, 11, 4, 8)
        path = QPainterPath()
        path.moveTo(11, 11)
        path.lineTo(15, 7)
        path.lineTo(15, 23)
        path.lineTo(11, 19)
        path.closeSubpath()
        painter.drawPath(path)
        
        # 2. Sound waves / mute cross
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.is_muted or self.volume_level == 0:
            # Draw a small mute cross 'x'
            painter.setPen(QPen(icon_color, 1.5))
            painter.drawLine(18, 12, 22, 18)
            painter.drawLine(22, 12, 18, 18)
        else:
            painter.setPen(QPen(icon_color, 1.5))
            # First wave
            painter.drawArc(13, 10, 10, 10, -60 * 16, 120 * 16)
            # Second wave (drawn if volume > 50%)
            if self.volume_level > 50:
                painter.drawArc(11, 7, 16, 16, -60 * 16, 120 * 16)
                
        painter.end()


class ThemeToggleButton(QAbstractButton):
    """
    Custom QPainter-drawn button that toggles between Dark and Light themes.
    Displays a Moon icon in Light Mode (to switch to Dark)
    and a Sun icon in Dark Mode (to switch to Light).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_dark = True
        self.setStyleSheet("background: transparent; border: none; padding: 0px;")
        
    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_hover = self.underMouse()
        is_pressed = self.isDown()
        is_disabled = not self.isEnabled()
        
        # Background and border colors based on theme and state
        if self.is_dark:
            bg_color = QColor("#2D2D2D") if is_hover else QColor("transparent")
            border_color = QColor("#6C5CE7") if is_hover else QColor("#555555")
            if is_pressed:
                bg_color = QColor("#1A1A1A")
            icon_color = QColor("#FFFFFF")
        else: # light mode
            bg_color = QColor("#E4E5EA") if is_hover else QColor("transparent")
            border_color = QColor("#6C5CE7") if is_hover else QColor("#CCCCCC")
            if is_pressed:
                bg_color = QColor("#D1D2D6")
            icon_color = QColor("#2D2D3A")
            
        # Draw background rounded rectangle
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(1, 1, 34, 34, 8, 8)
        
        if self.is_dark:
            # Draw Sun icon (we are in dark mode, click switches to light)
            painter.setPen(QPen(icon_color, 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Center circle
            painter.setBrush(QBrush(icon_color))
            painter.drawEllipse(13, 13, 10, 10)
            
            # Rays
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(icon_color, 1.5))
            # 8 rays around the circle
            rays = [
                (18, 7, 18, 10),   # North
                (18, 26, 18, 29), # South
                (7, 18, 10, 18),   # West
                (26, 18, 29, 18), # East
                (11, 11, 13, 13), # NW
                (23, 23, 25, 25), # SE
                (11, 25, 13, 23), # SW
                (23, 11, 25, 13)  # NE
            ]
            for x1, y1, x2, y2 in rays:
                painter.drawLine(x1, y1, x2, y2)
        else:
            # Draw Full Moon (filled yellow circle with craters, we are in light mode, click switches to dark)
            moon_color = QColor("#FBE585")
            painter.setBrush(QBrush(moon_color))
            painter.setPen(QPen(icon_color, 1.5))
            painter.drawEllipse(11, 11, 14, 14)
            
            # Crater details
            crater_color = QColor("#D4B93A")
            painter.setBrush(QBrush(crater_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(14, 15, 3, 3)
            painter.drawEllipse(19, 17, 2, 2)
            painter.drawEllipse(16, 20, 2, 2)
            
        painter.end()


class JumpSlider(QSlider):
    """
    A custom QSlider that jumps immediately to the clicked position
    instead of moving by step increments.
    """
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            sr = self.style().subControlRect(
                QStyle.ComplexControl.CC_Slider,
                opt,
                QStyle.SubControl.SC_SliderGroove,
                self
            )
            
            if self.orientation() == Qt.Orientation.Horizontal:
                slider_length = sr.width()
                slider_position = event.position().x() - sr.x()
            else:
                slider_length = sr.height()
                slider_position = sr.bottom() - event.position().y()
                
            if slider_length > 0:
                new_val = self.minimum() + int(
                    (self.maximum() - self.minimum()) * slider_position / slider_length
                )
                new_val = max(self.minimum(), min(self.maximum(), new_val))
                self.setValue(new_val)
                self.sliderMoved.emit(new_val)
            
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlurFit Studio")
        self.resize(1100, 750)
        self.setMinimumSize(950, 600)
        
        # State variables
        self.input_file = ""
        self.output_file = ""
        self.video_metadata = None
        self.processing_thread = None
        
        # Sliders states
        self.blur_strength = 40      # 0 to 100
        self.crop_position = 50      # 0 to 100 (horizontal/vertical pan offset)
        
        # Setup GUI elements
        self.settings = QSettings("BlurFitStudio", "BlurFitStudio")
        if not self.settings.contains("theme"):
            from PyQt6.QtGui import QGuiApplication
            scheme = QGuiApplication.styleHints().colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                self.settings.setValue("theme", "dark")
            else:
                self.settings.setValue("theme", "light")
                
        self.init_ui()
        self.init_players()
        self.apply_theme()
        self.update_ui_states(has_video=False)

    def init_ui(self):
        # Central Main Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(12)
        
        # ------------------- 1. HEADER PANEL (I/O) -------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Input Box
        input_group = QGroupBox("Wejście wideo")
        input_box_layout = QHBoxLayout(input_group)
        input_box_layout.setContentsMargins(10, 10, 10, 10)
        
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setReadOnly(True)
        self.input_path_edit.setPlaceholderText("Wybierz plik wideo z dysku...")
        
        self.select_input_btn = QPushButton("Wybierz wideo...")
        self.select_input_btn.setObjectName("secondaryButton")
        self.select_input_btn.clicked.connect(self.choose_input_video)
        
        input_box_layout.addWidget(self.input_path_edit)
        input_box_layout.addWidget(self.select_input_btn)
        
        # Output Box
        output_group = QGroupBox("Wyjście wideo")
        output_box_layout = QHBoxLayout(output_group)
        output_box_layout.setContentsMargins(10, 10, 10, 10)
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setReadOnly(True)
        self.output_path_edit.setPlaceholderText("Zdefiniuj miejsce zapisu...")
        
        self.save_as_btn = QPushButton("Zapisz jako...")
        self.save_as_btn.setObjectName("secondaryButton")
        self.save_as_btn.clicked.connect(self.choose_output_destination)
        
        output_box_layout.addWidget(self.output_path_edit)
        output_box_layout.addWidget(self.save_as_btn)
        
        # Theme Toggle Button
        self.theme_button = ThemeToggleButton()
        self.theme_button.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(input_group, stretch=2)
        header_layout.addWidget(output_group, stretch=2)
        header_layout.addWidget(self.theme_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addLayout(header_layout)
        
        # ------------------- 2. CENTRAL PREVIEWS PANEL -------------------
        previews_layout = QHBoxLayout()
        previews_layout.setSpacing(15)
        
        # Original Player Panel (Left)
        original_group = QGroupBox("Oryginał")
        original_layout = QVBoxLayout(original_group)
        original_layout.setContentsMargins(10, 15, 10, 10)
        
        self.original_video_widget = QVideoWidget()
        self.original_video_widget.setObjectName("canvasFrame")
        self.original_video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        
        # Playback controls bar
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Custom QPainter-drawn Play/Pause Button
        self.play_button = PlayPauseButton()
        self.play_button.clicked.connect(self.toggle_playback)
        
        self.timeline_slider = JumpSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setRange(0, 0)
        self.timeline_slider.sliderMoved.connect(self.on_slider_moved)
        self.timeline_slider.sliderPressed.connect(self.on_slider_pressed)
        self.timeline_slider.sliderReleased.connect(self.on_slider_released)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFixedWidth(85)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Custom QPainter Speaker Icon & Volume Slider
        self.volume_button = VolumeButton()
        self.volume_button.clicked.connect(self.toggle_mute)
        
        self.volume_slider = JumpSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70) # Default volume 70%
        self.volume_slider.setFixedWidth(70)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.timeline_slider)
        controls_layout.addWidget(self.time_label)
        controls_layout.addWidget(self.volume_button)
        controls_layout.addWidget(self.volume_slider)
        
        original_layout.addWidget(self.original_video_widget, stretch=1)
        original_layout.addLayout(controls_layout)
        
        # Simulated Effect Preview Panel (Right)
        preview_group = QGroupBox("Podgląd efektu")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(10, 15, 10, 10)
        
        self.preview_container = PreviewContainer()
        preview_layout.addWidget(self.preview_container, stretch=1)
        
        previews_layout.addWidget(original_group, stretch=1)
        previews_layout.addWidget(preview_group, stretch=1)
        self.main_layout.addLayout(previews_layout, stretch=1)
        
        # ------------------- 3. CONFIGURATION PANEL -------------------
        config_group = QGroupBox("Ustawienia obrazu")
        config_layout = QHBoxLayout(config_group)
        config_layout.setContentsMargins(15, 15, 15, 15)
        config_layout.setSpacing(25)
        
        # Ratio Combobox Layout
        ratio_layout = QVBoxLayout()
        ratio_layout.setSpacing(6)
        ratio_label = QLabel("Docelowe proporcje:")
        self.ratio_combo = QComboBox()
        self.ratio_combo.addItem(create_social_icon("tiktok"), "9:16 (Pionowo / TikTok / Shorts)", "9:16")
        self.ratio_combo.addItem(create_social_icon("youtube"), "16:9 (Poziomo / YouTube)", "16:9")
        self.ratio_combo.addItem(create_social_icon("instagram"), "1:1 (Kwadrat / Instagram)", "1:1")
        self.ratio_combo.addItem(create_social_icon("classic"), "4:3 (Klasyczny / Standard)", "4:3")
        self.ratio_combo.currentIndexChanged.connect(self.on_aspect_ratio_changed)
        
        ratio_layout.addWidget(ratio_label)
        ratio_layout.addWidget(self.ratio_combo)
        
        # Scale Mode Layout
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(6)
        mode_label = QLabel("Tryb skalowania:")
        
        self.mode_group = QButtonGroup(self)
        self.mode_blur_radio = QRadioButton("Dopasuj z rozmytym tłem")
        self.mode_crop_radio = QRadioButton("Przytnij i wypełnij")
        
        self.mode_group.addButton(self.mode_blur_radio)
        self.mode_group.addButton(self.mode_crop_radio)
        
        self.mode_blur_radio.setChecked(True)
        self.mode_group.buttonClicked.connect(self.on_scale_mode_changed)
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_blur_radio)
        mode_layout.addWidget(self.mode_crop_radio)
        
        # Multi-purpose Slider (Blur Strength OR Crop Position)
        self.blur_layout = QVBoxLayout()
        self.blur_layout.setSpacing(6)
        self.blur_title_label = QLabel("Intensywność rozmycia (40%):")
        
        self.blur_slider = JumpSlider(Qt.Orientation.Horizontal)
        self.blur_slider.setRange(0, 100)
        self.blur_slider.setValue(40) # Default blur percentage
        self.blur_slider.valueChanged.connect(self.on_slider_changed)
        
        self.blur_layout.addWidget(self.blur_title_label)
        self.blur_layout.addWidget(self.blur_slider)
        
        config_layout.addLayout(ratio_layout, stretch=1)
        config_layout.addLayout(mode_layout, stretch=1)
        config_layout.addLayout(self.blur_layout, stretch=2)
        
        self.main_layout.addWidget(config_group)
        
        # ------------------- 4. ACTION PANEL -------------------
        action_layout = QVBoxLayout()
        action_layout.setSpacing(8)
        
        self.export_button = QPushButton("Eksportuj wideo")
        self.export_button.setFixedHeight(45)
        self.export_button.clicked.connect(self.on_export_clicked)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        action_layout.addWidget(self.export_button)
        action_layout.addWidget(self.progress_bar)
        
        self.main_layout.addLayout(action_layout)

    def init_players(self):
        """Initializes the single QMediaPlayer for playback and preview rendering."""
        # 1. Audio Output
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(self.volume_slider.value() / 100.0)
        
        # 2. Original Player
        self.original_player = QMediaPlayer()
        self.original_player.setAudioOutput(self.audio_output)
        self.original_player.setVideoOutput(self.original_video_widget)
        
        # 3. Connect signals for playback state & slider synchronization
        self.original_player.positionChanged.connect(self.on_player_position_changed)
        self.original_player.durationChanged.connect(self.on_player_duration_changed)
        self.original_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.original_player.errorOccurred.connect(self.on_player_error)
        
        # Grab decoded video frames in real-time from the video sink and draw on preview canvas
        self.original_video_widget.videoSink().videoFrameChanged.connect(self.on_video_frame_changed)
        
        # Init Volume Button State
        self.volume_button.set_volume_level(self.volume_slider.value())

    def get_active_theme_mode(self):
        """Determines the active theme mode ('dark' or 'light') based on user choice."""
        return self.settings.value("theme", "dark")

    def apply_theme(self):
        """Applies the active theme stylesheet and updates custom painted widgets."""
        mode = self.get_active_theme_mode()
        is_dark = (mode == "dark")
        
        self.theme_button.is_dark = is_dark
        self.play_button.is_dark = is_dark
        self.volume_button.is_dark = is_dark
        
        from PyQt6.QtWidgets import QApplication
        from blurfit_studio.ui import style_sheets
        
        app = QApplication.instance()
        if app:
            app.setStyleSheet(style_sheets.get_stylesheet(mode))
            
        # Update custom buttons and widgets to adapt to new theme colors
        self.play_button.update()
        self.volume_button.update()
        self.theme_button.update()
        self.preview_container.update()

    def toggle_theme(self):
        """Toggles between Dark and Light themes."""
        current = self.get_active_theme_mode()
        new_theme = "light" if current == "dark" else "dark"
        self.settings.setValue("theme", new_theme)
        self.apply_theme()

    def update_ui_states(self, has_video=False):
        """Enables/disables layout elements depending on video loaded state."""
        self.original_video_widget.setEnabled(has_video)
        self.play_button.setEnabled(has_video)
        self.timeline_slider.setEnabled(has_video)
        self.ratio_combo.setEnabled(has_video)
        self.mode_blur_radio.setEnabled(has_video)
        self.mode_crop_radio.setEnabled(has_video)
        self.export_button.setEnabled(has_video)
        
        self.volume_button.setEnabled(has_video)
        self.volume_slider.setEnabled(has_video)
        self.preview_container.setEnabled(has_video)
        
        # Slider is active in both modes when video is loaded
        self.blur_slider.setEnabled(has_video)
        self.blur_title_label.setEnabled(has_video)

    # ------------------- EVENT HANDLERS & BINDINGS -------------------
    
    def choose_input_video(self):
        """Opens a file dialog to load a video."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Wybierz wideo źródłowe", 
            "", 
            "Pliki wideo (*.mp4 *.mov *.avi *.mkv *.webm *.m4v);;Wszystkie pliki (*.*)"
        )
        if not file_path:
            return
            
        self.load_video(normalize_path_display(file_path))

    def load_video(self, file_path):
        """Parses video metadata and feeds players."""
        file_path = normalize_path_display(file_path)
        self.setCursor(Qt.CursorShape.WaitCursor)
        try:
            metadata = video_worker.get_video_metadata(file_path)
            self.video_metadata = metadata
            self.input_file = file_path
            self.input_path_edit.setText(file_path)
            
            # Setup initial output destination path guess (e.g. video_blurfit.mp4)
            dir_name = os.path.dirname(file_path)
            file_info = QFileInfo(file_path)
            base_name = file_info.completeBaseName()
            suffix = file_info.suffix()
            
            # Default suffix to mp4 for the output
            out_suffix = suffix if suffix.lower() in ("mp4", "mkv", "mov", "avi") else "mp4"
            default_out = normalize_path_display(os.path.join(dir_name, f"{base_name}_blurfit.{out_suffix}"))
            
            self.output_file = default_out
            self.output_path_edit.setText(default_out)
            
            # Stop any playing media
            self.stop_all_players()
            
            # Load URL to player
            url = QUrl.fromLocalFile(file_path)
            self.original_player.setSource(url)
            
            # Set input aspect ratio for preview calculations
            self.preview_container.set_input_aspect_ratio(metadata["width"], metadata["height"])
            
            # Clear old frame drawings
            self.preview_container.clear_preview()
            
            # Enable controls
            self.update_ui_states(has_video=True)
            self.play_button.set_playing(False)
            
            # Reset slider and labels based on active mode
            self.on_scale_mode_changed(None)
            
            # Force player to load and show the first frame by playing and pausing on first decoded frame
            self.is_initial_load = True
            self._pre_load_muted = self.audio_output.isMuted()
            self.audio_output.setMuted(True)
            self.original_player.play()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Błąd ładowania pliku", 
                f"Nie można odczytać metadanych wideo:\n{str(e)}"
            )
            self.update_ui_states(has_video=False)
            self.input_path_edit.clear()
            self.output_path_edit.clear()
            self.input_file = ""
            self.output_file = ""
            self.video_metadata = None
            self.preview_container.clear_preview()
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def choose_output_destination(self):
        """Opens 'Save As' file dialog."""
        if not self.input_file:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Zapisz wideo jako", 
            self.output_file, 
            "MPEG-4 Video (*.mp4);;Matroska Video (*.mkv);;QuickTime Movie (*.mov);;AVI Video (*.avi);;Wszystkie pliki (*.*)"
        )
        if not file_path:
            return
            
        normalized_path = normalize_path_display(file_path)
        self.output_file = normalized_path
        self.output_path_edit.setText(normalized_path)

    def toggle_playback(self):
        """Toggles playback on the player."""
        if not self.input_file:
            return
            
        # Cancel initial load flags if user manually interacts before first frame
        if hasattr(self, 'is_initial_load') and self.is_initial_load:
            self.is_initial_load = False
            if hasattr(self, '_pre_load_muted'):
                self.audio_output.setMuted(self._pre_load_muted)
                
        if self.original_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.original_player.pause()
            self.play_button.set_playing(False)
        else:
            self.original_player.play()
            self.play_button.set_playing(True)

    def stop_all_players(self):
        """Stops the player."""
        self.original_player.stop()

    def on_slider_pressed(self):
        # Temporarily pause updates to avoid fighting the slider
        self.is_scrubbing = True

    def on_slider_released(self):
        self.is_scrubbing = False

    def on_slider_moved(self, position):
        """Scrubs player synchronously when user drags the timeline slider."""
        self.original_player.setPosition(position)

    def on_player_position_changed(self, position):
        """Syncs slider value and duration labels."""
        if not hasattr(self, 'is_scrubbing') or not self.is_scrubbing:
            self.timeline_slider.setValue(position)
            
        # Update time label
        total_dur = self.original_player.duration()
        self.time_label.setText(f"{format_time(position)} / {format_time(total_dur)}")

    def on_player_duration_changed(self, duration):
        """Configures slider ranges once media loads."""
        self.timeline_slider.setRange(0, duration)
        self.time_label.setText(f"00:00 / {format_time(duration)}")

    def on_media_status_changed(self, status):
        """Handles video looping/stopping at the end of stream."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.stop_all_players()
            self.original_player.setPosition(0)
            self.timeline_slider.setValue(0)
            self.play_button.set_playing(False)

    def on_player_error(self, error, error_string):
        """Soft warning if QMediaPlayer has local codec issues."""
        print(f"Player Error: {error_string}")
        pass

    def on_video_frame_changed(self, video_frame):
        """Sinks frames from the player and updates the preview canvas."""
        if not self.input_file or not video_frame.isValid():
            return
            
        # Convert QVideoFrame to QImage and draw on the canvas
        img = video_frame.toImage()
        if not img.isNull():
            self.preview_container.set_video_frame(img)
            
            # If this is the initial load, pause the player immediately on the first valid frame
            if hasattr(self, 'is_initial_load') and self.is_initial_load:
                self.is_initial_load = False
                self.original_player.pause()
                self.play_button.set_playing(False)
                # Restore original muted state
                if hasattr(self, '_pre_load_muted'):
                    self.audio_output.setMuted(self._pre_load_muted)

    def toggle_mute(self):
        """Toggles volume muting on the audio output."""
        is_muted = self.audio_output.isMuted()
        self.audio_output.setMuted(not is_muted)
        self.update_volume_button_icon()

    def on_volume_changed(self, value):
        """Adjusts the output playback volume."""
        self.audio_output.setVolume(value / 100.0)
        self.volume_button.set_volume_level(value)
        if self.audio_output.isMuted() and value > 0:
            self.audio_output.setMuted(False)
        self.update_volume_button_icon()

    def update_volume_button_icon(self):
        """Updates muted state on the vector volume icon."""
        self.volume_button.set_muted(self.audio_output.isMuted())

    def on_aspect_ratio_changed(self, index):
        """Updates aspect ratio string for the canvas container."""
        ratio_str = self.ratio_combo.itemData(index)
        self.preview_container.set_aspect_ratio(ratio_str)

    def on_scale_mode_changed(self, button):
        """Updates UI sliders and labels based on the scaling mode."""
        is_blur = self.mode_blur_radio.isChecked()
        mode = "blur" if is_blur else "crop"
        self.preview_container.set_scale_mode(mode)
        
        # Switch slider configuration
        if is_blur:
            self.blur_slider.setValue(self.blur_strength)
            self.blur_title_label.setText(f"Intensywność rozmycia ({self.blur_strength}%):")
            self.preview_container.set_blur_strength(self.blur_strength)
        else:
            self.blur_slider.setValue(self.crop_position)
            self.blur_title_label.setText(f"Pozycja kadrowania ({self.crop_position}%):")
            self.preview_container.set_crop_position(self.crop_position)

    def on_slider_changed(self, val):
        """Handles slider adjustments for either blur strength or crop panning."""
        if self.mode_blur_radio.isChecked():
            self.blur_strength = val
            self.blur_title_label.setText(f"Intensywność rozmycia ({val}%):")
            self.preview_container.set_blur_strength(val)
        else:
            self.crop_position = val
            self.blur_title_label.setText(f"Pozycja kadrowania ({val}%):")
            self.preview_container.set_crop_position(val)

    # ------------------- VIDEO EXPORT WORKER INTEGRATION -------------------

    def on_export_clicked(self):
        """Initiates background FFmpeg rendering, or cancels it if running."""
        # 1. If currently processing, click cancels it
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.cancel()
            return
            
        if not self.input_file or not self.output_file:
            QMessageBox.warning(self, "Błąd", "Wybierz plik wejściowy i wyjściowy.")
            return
            
        # Check if output file exists, ask confirmation to overwrite
        if os.path.exists(self.output_file):
            reply = QMessageBox.question(
                self, 
                "Plik istnieje", 
                "Plik docelowy już istnieje. Czy chcesz go nadpisać?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
                
        # 2. Pause playback instead of stopping it, keeping the frame visible
        self.original_player.pause()
        self.play_button.set_playing(False)
        
        # 3. Disable GUI settings to prevent changes during export
        self.set_ui_lock(locked=True)
        
        # 4. Prepare Progress Bar & Button Text
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.export_button.setText("Anuluj eksport wideo")
        self.export_button.setStyleSheet("background-color: #D63031;") # Bright red for cancel button
        
        # 5. Build and run Video Worker Thread
        ratio_str = self.ratio_combo.itemData(self.ratio_combo.currentIndex())
        mode = "blur" if self.mode_blur_radio.isChecked() else "crop"
        
        self.processing_thread = video_worker.VideoProcessingThread(
            input_path=self.input_file,
            output_path=self.output_file,
            target_ratio_str=ratio_str,
            mode=mode,
            blur_strength=self.blur_strength,
            metadata=self.video_metadata,
            crop_position=self.crop_position
        )
        
        self.processing_thread.progress_changed.connect(self.on_export_progress)
        self.processing_thread.finished.connect(self.on_export_finished)
        self.processing_thread.error_occurred.connect(self.on_export_error)
        
        self.processing_thread.start()

    def on_export_progress(self, val):
        self.progress_bar.setValue(val)

    def on_export_finished(self, out_path):
        """Displays completion dialogue and resets GUI state."""
        self.progress_bar.setValue(100)
        
        # Custom completion box with Open Folder action
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Sukces!")
        msg_box.setText("Przetwarzanie wideo zakończone pomyślnie!")
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        open_folder_btn = msg_box.addButton("Otwórz folder", QMessageBox.ButtonRole.ActionRole)
        close_btn = msg_box.addButton("Zamknij", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == open_folder_btn:
            open_file_in_explorer(out_path)
            
        self.reset_export_state()

    def on_export_error(self, err_msg):
        """Displays FFmpeg error dialogs and resets GUI state."""
        QMessageBox.critical(
            self, 
            "Błąd renderowania wideo", 
            f"Wystąpił problem podczas eksportu wideo:\n\n{err_msg}"
        )
        self.reset_export_state()

    def reset_export_state(self):
        """Resets action button styles and unlocks settings inputs."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        
        self.export_button.setText("Eksportuj wideo")
        self.export_button.setStyleSheet("") 
        
        self.set_ui_lock(locked=False)
        self.processing_thread = None

    def set_ui_lock(self, locked):
        """Blocks inputs during export execution."""
        self.select_input_btn.setDisabled(locked)
        self.save_as_btn.setDisabled(locked)
        self.play_button.setDisabled(locked)
        self.timeline_slider.setDisabled(locked)
        self.ratio_combo.setDisabled(locked)
        self.mode_blur_radio.setDisabled(locked)
        self.mode_crop_radio.setDisabled(locked)
        self.blur_slider.setDisabled(locked)

    def closeEvent(self, event):
        """Gracefully handle window close during active rendering."""
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self, 
                "Potwierdzenie wyjścia", 
                "Renderowanie wideo nadal trwa. Czy na pewno chcesz wyjść i przerwać eksport?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.processing_thread.cancel()
                self.processing_thread.wait() # Wait for subprocess shutdown
                event.accept()
            else:
                event.ignore()
        else:
            self.stop_all_players()
            event.accept()
