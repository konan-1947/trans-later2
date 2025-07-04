# app/features/viewer/viewer_widget.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

ZOOM_STEP = 0.2  # Mỗi lần zoom sẽ tăng/giảm 20%


class ViewerWidget(QWidget):
    zoom_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.original_pixmap = None
        self.zoom_factor = 1.0

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll_area = QScrollArea()
        # Quan trọng: widget bên trong (label) cần có thể tự do thay đổi kích thước
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.image_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def set_pixmap(self, pixmap):
        """Lưu pixmap gốc và reset zoom về trạng thái mặc định (fit-to-page)."""
        self.original_pixmap = pixmap
        if self.original_pixmap:
            self.fit_to_page()
        else:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Failed to load page or no PDF open.")

    def update_pixmap_display(self):
        """Hàm trung tâm: Tạo một pixmap đã được scale và đặt nó vào label."""
        if not self.original_pixmap:
            return

        # --- PHẦN LOGIC ĐƯỢC SỬA LẠI HOÀN TOÀN ---
        # 1. Tạo một phiên bản pixmap mới đã được scale.
        scaled_pixmap = self.original_pixmap.scaled(
            self.original_pixmap.size() * self.zoom_factor,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # 2. Đặt phiên bản ĐÃ SCALE này vào label.
        self.image_label.setPixmap(scaled_pixmap)

        # 3. Quan trọng: Bảo label tự điều chỉnh kích thước của nó để vừa khít với pixmap mới.
        #    Điều này giúp ScrollArea biết được vùng cần cuộn lớn đến đâu.
        self.image_label.adjustSize()
        # --- KẾT THÚC PHẦN SỬA ---

        self.zoom_changed.emit(int(self.zoom_factor * 100))

    def zoom_in(self):
        self.zoom_factor += ZOOM_STEP
        self.update_pixmap_display()

    def zoom_out(self):
        if self.zoom_factor - ZOOM_STEP > 0.1:  # Giới hạn zoom tối thiểu 10%
            self.zoom_factor -= ZOOM_STEP
            self.update_pixmap_display()

    def fit_to_width(self):
        if not self.original_pixmap or self.original_pixmap.width() == 0:
            return

        # Trừ đi một chút để tránh thanh cuộn dọc xuất hiện không cần thiết
        viewport_width = self.scroll_area.viewport().width() - 2
        self.zoom_factor = viewport_width / self.original_pixmap.width()
        self.update_pixmap_display()

    def fit_to_page(self):
        if not self.original_pixmap or self.original_pixmap.width() == 0 or self.original_pixmap.height() == 0:
            return

        viewport_size = self.scroll_area.viewport().size()
        pixmap_size = self.original_pixmap.size()

        width_ratio = viewport_size.width() / pixmap_size.width()
        height_ratio = viewport_size.height() / pixmap_size.height()

        self.zoom_factor = min(width_ratio, height_ratio)
        self.update_pixmap_display()
