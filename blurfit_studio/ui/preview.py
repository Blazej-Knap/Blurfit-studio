from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QFrame, QSizePolicy, QGraphicsBlurEffect
from PyQt6.QtGui import QPainter, QColor

class BlurredBackgroundWidget(QWidget):
    """
    Renders a stretched background frame, using QGraphicsBlurEffect
    to achieve a high-quality blur that matches FFmpeg's output.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.blur_strength = 40
        self.crop_position = 50
        
        # Apply standard graphics blur effect
        self.blur_effect = QGraphicsBlurEffect(self)
        self.blur_effect.setBlurRadius(20) # Default: 40% strength * 0.5 = 20 radius
        self.setGraphicsEffect(self.blur_effect)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    def set_image(self, image):
        self.image = image
        self.update()

    def set_blur_strength(self, val):
        self.blur_strength = val
        # Map 0-100 to 0-50 radius (matches FFmpeg boxblur math)
        self.blur_effect.setBlurRadius(val * 0.5)

    def set_crop_position(self, val):
        self.crop_position = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        if self.image and not self.image.isNull():
            widget_w = self.width()
            widget_h = self.height()
            
            if widget_w <= 0 or widget_h <= 0:
                painter.end()
                return
                
            img_w = self.image.width()
            img_h = self.image.height()
            
            widget_ratio = widget_w / widget_h
            img_ratio = img_w / img_h
            
            # Crop image to match the widget aspect ratio using crop_position
            if img_ratio > widget_ratio:
                # Image is wider -> crop sides
                crop_h = img_h
                crop_w = int(crop_h * widget_ratio)
                crop_x = int((img_w - crop_w) * (self.crop_position / 100.0))
                crop_y = 0
            else:
                # Image is taller -> crop top/bottom
                crop_w = img_w
                crop_h = int(crop_w / widget_ratio)
                crop_x = 0
                crop_y = int((img_h - crop_h) * (self.crop_position / 100.0))
                
            cropped = self.image.copy(crop_x, crop_y, crop_w, crop_h)
            painter.drawImage(self.rect(), cropped)
        else:
            is_dark = self.palette().window().color().value() < 128
            bg_color = QColor("#0E0E0E") if is_dark else QColor("#EBEBEF")
            painter.fillRect(self.rect(), bg_color)
        painter.end()


class VideoFrameWidget(QWidget):
    """
    Renders the sharp foreground video frame centered on screen.
    Supports crop position panning in cover scale mode.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.scale_mode = "fit"
        self.crop_position = 50
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    def set_image(self, image):
        self.image = image
        self.update()

    def set_scale_mode(self, mode):
        self.scale_mode = mode
        self.update()

    def set_crop_position(self, val):
        self.crop_position = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        if self.image and not self.image.isNull():
            rect = self.rect()
            if self.scale_mode == "cover":
                # Crop and fill canvas frame with panning offset
                widget_w = self.width()
                widget_h = self.height()
                img_w = self.image.width()
                img_h = self.image.height()
                
                widget_ratio = widget_w / widget_h
                img_ratio = img_w / img_h
                
                if img_ratio > widget_ratio:
                    crop_h = img_h
                    crop_w = int(crop_h * widget_ratio)
                    crop_x = int((img_w - crop_w) * (self.crop_position / 100.0))
                    crop_y = 0
                else:
                    crop_w = img_w
                    crop_h = int(crop_w / widget_ratio)
                    crop_x = 0
                    crop_y = int((img_h - crop_h) * (self.crop_position / 100.0))
                    
                cropped = self.image.copy(crop_x, crop_y, crop_w, crop_h)
                painter.drawImage(rect, cropped)
            else:
                # Fit centered
                painter.drawImage(rect, self.image)
        else:
            is_dark = self.palette().window().color().value() < 128
            bg_color = QColor("#0E0E0E") if is_dark else QColor("#EBEBEF")
            painter.fillRect(self.rect(), bg_color)
        painter.end()


class PreviewContainer(QWidget):
    """
    Custom container widget that displays the target aspect ratio canvas,
    centered inside the available preview space.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_ratio_str = "9:16"
        self.input_width = 16
        self.input_height = 9
        self.scale_mode = "blur"
        
        # Output Canvas Frame boundary
        self.canvas_frame = QFrame(self)
        self.canvas_frame.setObjectName("canvasFrame")
        self.canvas_frame.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
        # Background blurred widget
        self.bg_widget = BlurredBackgroundWidget(self.canvas_frame)
        
        # Foreground sharp widget
        self.fg_widget = VideoFrameWidget(self.canvas_frame)
        
    def set_aspect_ratio(self, ratio_str):
        self.target_ratio_str = ratio_str
        self.update_canvas_geometry()
        
    def set_input_aspect_ratio(self, w, h):
        self.input_width = max(1, w)
        self.input_height = max(1, h)
        self.update_canvas_geometry()
        
    def set_scale_mode(self, mode):
        self.scale_mode = mode
        self.fg_widget.set_scale_mode("cover" if mode == "crop" else "fit")
        
        if mode == "crop":
            self.bg_widget.hide()
        else: # "blur"
            self.bg_widget.show()
            
        self.update_canvas_geometry()
        
    def set_blur_strength(self, val):
        self.bg_widget.set_blur_strength(val)
        
    def set_crop_position(self, val):
        """Sets the horizontal/vertical crop panning alignment (0-100%)."""
        self.fg_widget.set_crop_position(val)
        self.bg_widget.set_crop_position(val)
        
    def set_video_frame(self, image):
        """Passes the decoded frame image to both drawing widgets."""
        self.bg_widget.set_image(image)
        self.fg_widget.set_image(image)
        
    def clear_preview(self):
        """Clears all video frame images."""
        self.bg_widget.set_image(None)
        self.fg_widget.set_image(None)
        
    def layout_canvas_children(self):
        cw = self.canvas_frame.width()
        ch = self.canvas_frame.height()
        
        if cw <= 0 or ch <= 0:
            return
            
        if self.scale_mode == "crop":
            # Foreground fills the entire output canvas and crops excess
            self.fg_widget.setGeometry(0, 0, cw, ch)
        else:
            # Background fills the entire output canvas
            self.bg_widget.setGeometry(0, 0, cw, ch)
            
            # Foreground fits in the center preserving aspect ratio
            r_in = self.input_width / self.input_height
            if cw / ch > r_in:
                # Canvas is wider than input -> fit height
                fg_h = ch
                fg_w = int(fg_h * r_in)
            else:
                # Canvas is taller than input -> fit width
                fg_w = cw
                fg_h = int(fg_w / r_in)
                
            fg_x = (cw - fg_w) // 2
            fg_y = (ch - fg_h) // 2
            self.fg_widget.setGeometry(fg_x, fg_y, fg_w, fg_h)
            
    def update_canvas_geometry(self):
        try:
            num, den = map(int, self.target_ratio_str.split(":"))
            ratio = num / den
        except Exception:
            ratio = 9/16
            
        w_container = self.width()
        h_container = self.height()
        
        if w_container <= 0 or h_container <= 0:
            return
            
        # Give a 20px padding boundary
        padding = 20
        max_w = w_container - padding
        max_h = h_container - padding
        
        if max_w / max_h > ratio:
            canvas_h = max_h
            canvas_w = int(canvas_h * ratio)
        else:
            canvas_w = max_w
            canvas_h = int(canvas_w / ratio)
            
        x = (w_container - canvas_w) // 2
        y = (h_container - canvas_h) // 2
        
        self.canvas_frame.setGeometry(x, y, canvas_w, canvas_h)
        self.layout_canvas_children()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_canvas_geometry()
