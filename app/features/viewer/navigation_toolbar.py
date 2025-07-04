# app/features/viewer/navigation_toolbar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QIcon


class NavigationToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.open_button = QPushButton("Open PDF")
        # self.open_button.setIcon(QIcon("assets/icons/open.png")) # Uncomment if you have icons

        self.prev_button = QPushButton("<< Prev")
        self.page_label = QLabel("Page: 0 / 0")
        self.next_button = QPushButton("Next >>")

        self.translate_button = QPushButton("Translate This Page")
        self.toggle_view_button = QPushButton("Toggle Original/Translated")

        layout.addWidget(self.open_button)
        layout.addStretch()
        layout.addWidget(self.prev_button)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_button)
        layout.addStretch()
        layout.addWidget(self.translate_button)
        layout.addWidget(self.toggle_view_button)

        self.setLayout(layout)
