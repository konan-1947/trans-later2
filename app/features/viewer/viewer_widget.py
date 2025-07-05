# app/features/viewer/viewer_widget.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

ZOOM_STEP = 0.25


class ViewerWidget(QWidget):
    render_requested = pyqtSignal(float)
    zoom_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.zoom_factor = 1.0
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.image_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        # Khi resize, chúng ta sẽ ưu tiên fit-to-width
        self.resize_timer.timeout.connect(self.fit_to_width)

    def set_pixmap(self, pixmap):
        if pixmap:
            self.image_label.setPixmap(pixmap)
            self.image_label.adjustSize()
        else:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Please open a PDF file to start.")

    def request_initial_render(self):
        """
        Được gọi khi một trang mới được tải.
        Yêu cầu render ở chế độ Fit-to-Width.
        """
        self.fit_to_width()  # Mặc định ban đầu là Fit to Width

    def zoom_in(self):
        self.zoom_factor += ZOOM_STEP
        self.render_requested.emit(self.zoom_factor)
        self.zoom_changed.emit(int(self.zoom_factor * 100))

    def zoom_out(self):
        if self.zoom_factor - ZOOM_STEP > 0.1:
            self.zoom_factor -= ZOOM_STEP
            self.render_requested.emit(self.zoom_factor)
            self.zoom_changed.emit(int(self.zoom_factor * 100))

    def fit_to_width(self):
        self.render_requested.emit(-1.0)

    def fit_to_page(self):
        self.render_requested.emit(-2.0)

    def resizeEvent(self, event):
        """Khi resize, khởi động lại timer. Chỉ khi dừng resize, timer mới kích hoạt."""
        super().resizeEvent(event)
        # Khi người dùng resize cửa sổ, chúng ta cũng tự động fit-to-width
        self.resize_timer.start(200)
