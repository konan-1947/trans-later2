# app/features/viewer/zoom_toolbar.py

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import pyqtSignal


class ZoomToolbar(QWidget):
    # Định nghĩa các tín hiệu tùy chỉnh để báo cho MainWindow biết người dùng muốn làm gì
    zoom_in_requested = pyqtSignal()
    zoom_out_requested = pyqtSignal()
    fit_to_width_requested = pyqtSignal()
    fit_to_page_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setToolTip("Zoom Out")
        self.zoom_out_button.setFixedWidth(30)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setToolTip("Zoom In")
        self.zoom_in_button.setFixedWidth(30)

        # Thêm một đường kẻ dọc để phân tách
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.fit_width_button = QPushButton("Fit Width")
        self.fit_width_button.setToolTip("Fit to page width")

        self.fit_page_button = QPushButton("Fit Page")
        self.fit_page_button.setToolTip("Fit to entire page")

        layout.addWidget(self.zoom_out_button)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.zoom_in_button)
        layout.addWidget(separator)
        layout.addWidget(self.fit_width_button)
        layout.addWidget(self.fit_page_button)
        layout.addStretch()  # Đẩy các nút về bên trái

        self.setLayout(layout)

        # Kết nối các nút bấm với việc phát tín hiệu
        self.zoom_in_button.clicked.connect(self.zoom_in_requested.emit)
        self.zoom_out_button.clicked.connect(self.zoom_out_requested.emit)
        self.fit_width_button.clicked.connect(self.fit_to_width_requested.emit)
        self.fit_page_button.clicked.connect(self.fit_to_page_requested.emit)

    def update_zoom_label(self, zoom_percentage):
        """Slot này sẽ được gọi từ MainWindow để cập nhật text của label."""
        self.zoom_label.setText(f"{zoom_percentage}%")
