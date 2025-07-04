# app/features/translator/translation_controller.py

from app.core.pdf_service import PDFService
from app.core.translation_service import TranslationService
from app.features.translator.image_renderer import ImageRenderer


class TranslationController:
    def __init__(self):
        # Truyền pdf_service vào để có thể lấy cả ảnh nền và text
        self.pdf_service = PDFService()
        self.translator = TranslationService()
        self.renderer = ImageRenderer()

    def set_pdf_service(self, service):
        """Cho phép MainWindow gán đối tượng pdf_service đang hoạt động."""
        self.pdf_service = service

    def translate_page(self, page_num):
        # 1. Tạo ảnh nền SẠCH
        clean_bg_pixmap = self.pdf_service.get_clean_page_as_pixmap(page_num)
        if not clean_bg_pixmap:
            return None

        # 2. Trích xuất text từ trang GỐC
        structured_blocks = self.pdf_service.extract_text_blocks(page_num)
        if not structured_blocks:
            return clean_bg_pixmap  # Trả về ảnh sạch nếu không có text

        # 3. Gom các dòng để dịch
        all_lines_text = []
        for block in structured_blocks:
            for line in block['lines']:
                all_lines_text.append(line['text'])

        # 4. Dịch bằng phương thức JSON mới
        translated_json = self.translator.translate_page_json(all_lines_text)

        # 5. Gán lại kết quả dịch vào cấu trúc dữ liệu
        line_index_counter = 0
        for block in structured_blocks:
            for line in block['lines']:
                line_key = f"line_{line_index_counter}"
                # Lấy bản dịch, fallback về gốc nếu lỗi
                line['translated'] = translated_json.get(
                    line_key, line['text'])
                line_index_counter += 1

        # 6. Vẽ lại trên nền sạch
        rendered_pixmap = self.renderer.render(
            clean_bg_pixmap, structured_blocks)

        return rendered_pixmap
