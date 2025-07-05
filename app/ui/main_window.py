# app/ui/main_window.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QHBoxLayout
from app.config.settings import APP_NAME, APP_VERSION
from app.core.pdf_service import PDFService
from app.features.viewer.viewer_widget import ViewerWidget
from app.features.viewer.navigation_toolbar import NavigationToolbar
from app.features.viewer.zoom_toolbar import ZoomToolbar
from app.features.translator.translation_controller import TranslationController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} - {APP_VERSION}")
        self.setGeometry(100, 100, 1200, 900)

        self.pdf_service = PDFService()
        self.translation_controller = TranslationController()
        self.translation_controller.set_pdf_service(self.pdf_service)

        self.nav_toolbar = NavigationToolbar()
        self.zoom_toolbar = ZoomToolbar()
        self.viewer = ViewerWidget()

        self.current_page = 0
        self.cached_translated_blocks = None
        self.current_pixmap_is_translated = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.nav_toolbar)
        toolbar_layout.addWidget(self.zoom_toolbar)

        main_layout = QVBoxLayout(central_widget)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.viewer)

        self.connect_signals()

    def connect_signals(self):
        self.nav_toolbar.open_button.clicked.connect(self.open_file_dialog)
        self.nav_toolbar.prev_button.clicked.connect(self.show_prev_page)
        self.nav_toolbar.next_button.clicked.connect(self.show_next_page)
        self.nav_toolbar.translate_button.clicked.connect(
            self.translate_current_page)
        self.nav_toolbar.toggle_view_button.clicked.connect(self.toggle_view)

        self.zoom_toolbar.zoom_in_requested.connect(self.viewer.zoom_in)
        self.zoom_toolbar.zoom_out_requested.connect(self.viewer.zoom_out)
        self.zoom_toolbar.fit_to_page_requested.connect(
            self.viewer.fit_to_page)
        self.zoom_toolbar.fit_to_width_requested.connect(
            self.viewer.fit_to_width)

        self.viewer.zoom_changed.connect(self.zoom_toolbar.update_zoom_label)
        self.viewer.render_requested.connect(self.render_current_view)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        if self.pdf_service.open_pdf(file_path):
            self.show_page(0)
        else:
            self.viewer.set_pixmap(None)

    def show_page(self, page_num):
        self.current_page = page_num
        self.cached_translated_blocks = None
        self.current_pixmap_is_translated = False

        self.nav_toolbar.page_label.setText(
            f"Page: {page_num + 1} / {self.pdf_service.get_page_count()}")
        self.viewer.request_initial_render()

    def show_prev_page(self):
        if self.pdf_service.doc and self.current_page > 0:
            self.show_page(self.current_page - 1)

    def show_next_page(self):
        if self.pdf_service.doc and self.current_page < self.pdf_service.get_page_count() - 1:
            self.show_page(self.current_page + 1)

    def translate_current_page(self):
        if not self.pdf_service.doc:
            return

        print("Translating page...")
        self.cached_translated_blocks = self.translation_controller.translate_and_cache_page(
            self.current_page)

        if self.cached_translated_blocks:
            self.current_pixmap_is_translated = True
            print("Translation complete. Data cached.")
            self.render_current_view(self.viewer.zoom_factor)
        else:
            print("No text found or translation failed.")

    def toggle_view(self):
        if not self.pdf_service.doc:
            return

        if self.cached_translated_blocks:
            self.current_pixmap_is_translated = not self.current_pixmap_is_translated
            self.render_current_view(self.viewer.zoom_factor)

    def render_current_view(self, zoom_factor):
        if not self.pdf_service.doc:
            return

        page = self.pdf_service.doc.load_page(self.current_page)

        if zoom_factor == -1.0:
            viewport_width = self.viewer.scroll_area.viewport().width() - 2
            zoom_factor = viewport_width / page.rect.width if page.rect.width > 0 else 1.0
        elif zoom_factor == -2.0:
            viewport_size = self.viewer.scroll_area.viewport().size()
            width_ratio = viewport_size.width() / page.rect.width if page.rect.width > 0 else 1.0
            height_ratio = viewport_size.height(
            ) / page.rect.height if page.rect.height > 0 else 1.0
            zoom_factor = min(width_ratio, height_ratio)

        self.viewer.zoom_factor = zoom_factor
        self.viewer.zoom_changed.emit(int(zoom_factor * 100))

        # Ép kiểu DPI sang số nguyên để tránh lỗi
        dpi = int(72 * zoom_factor)
        if dpi < 10:
            dpi = 10

        final_pixmap = None
        if self.current_pixmap_is_translated and self.cached_translated_blocks:
            final_pixmap = self.translation_controller.render_translated_page(
                self.current_page, self.cached_translated_blocks, dpi
            )
        else:
            final_pixmap, _, _ = self.pdf_service.get_page_as_pixmap(
                self.current_page, dpi)

        self.viewer.set_pixmap(final_pixmap)
