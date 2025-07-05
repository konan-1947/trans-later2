# app/features/translator/translation_controller.py

from app.core.pdf_service import PDFService
from app.core.translation_service import TranslationService
from app.features.translator.image_renderer import ImageRenderer


class TranslationController:
    def __init__(self):
        self.pdf_service = PDFService()
        self.translator = TranslationService()
        self.renderer = ImageRenderer()

    def set_pdf_service(self, service):
        """Cho phép MainWindow gán đối tượng pdf_service đang hoạt động."""
        self.pdf_service = service

    def translate_and_cache_page(self, page_num):
        """Chỉ dịch và trả về dữ liệu đã được làm giàu, không render."""
        structured_blocks = self.pdf_service.extract_text_blocks(page_num)
        if not structured_blocks:
            return None

        all_lines_text = [line['text']
                          for block in structured_blocks for line in block['lines']]
        translated_json = self.translator.translate_page_json(all_lines_text)

        line_index_counter = 0
        for block in structured_blocks:
            for line in block['lines']:
                line_key = f"line_{line_index_counter}"
                line['translated'] = translated_json.get(
                    line_key, line['text'])
                line_index_counter += 1

        return structured_blocks

    def render_translated_page(self, page_num, translated_blocks, dpi):
        """Render một trang đã dịch với dữ liệu và DPI cho trước."""
        clean_bg_pixmap = self.pdf_service.get_clean_page_as_pixmap(
            page_num, dpi)
        if not clean_bg_pixmap:
            return None

        rendered_pixmap = self.renderer.render(
            clean_bg_pixmap, translated_blocks, dpi)
        return rendered_pixmap
