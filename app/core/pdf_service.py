# app/core/pdf_service.py

import fitz
from PyQt6.QtGui import QImage, QPixmap
from app.config.settings import PDF_RENDER_DPI


class PDFService:
    def __init__(self):
        self.doc = None
        self.file_path = None

    def open_pdf(self, file_path):
        try:
            self.doc = fitz.open(file_path)
            self.file_path = file_path
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            self.doc = None
            self.file_path = None
            return False

    def close_pdf(self):
        if self.doc:
            self.doc.close()
        self.doc = None
        self.file_path = None

    def get_page_count(self):
        return self.doc.page_count if self.doc else 0

    def get_page_as_pixmap(self, page_num):
        """Lấy ảnh GỐC của trang."""
        if not self.doc or not (0 <= page_num < self.doc.page_count):
            return None

        page = self.doc.load_page(page_num)
        pix = page.get_pixmap(dpi=PDF_RENDER_DPI)
        image = QImage(pix.samples, pix.width, pix.height,
                       pix.stride, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(image)

    def get_clean_page_as_pixmap(self, page_num):
        """
        Tạo ảnh nền SẠCH bằng cách xóa tất cả text trên một bản sao tạm thời.
        Cách này đảm bảo đối tượng self.doc gốc không bị thay đổi.
        """
        if not self.file_path:  # Cần file_path để mở bản sao
            return None

        # --- LOGIC MỚI: TẠO BẢN SAO TÀI LIỆU TẠM THỜI ---
        try:
            temp_doc = fitz.open(self.file_path)
            page = temp_doc.load_page(page_num)

            # Thêm các vùng cần biên tập (redaction) cho tất cả các vùng chữ
            for rect in page.get_text_blocks():
                page.add_redact_annot(rect[:4])

            # Áp dụng các thay đổi, xóa sạch text
            page.apply_redactions()

            # Render trang đã sạch chữ này
            pix = page.get_pixmap(dpi=PDF_RENDER_DPI)
            image = QImage(pix.samples, pix.width, pix.height,
                           pix.stride, QImage.Format.Format_RGB888)

            # Đóng bản sao tạm thời lại
            temp_doc.close()

            return QPixmap.fromImage(image)

        except Exception as e:
            print(f"Error creating clean background: {e}")
            return None
        # --- KẾT THÚC LOGIC MỚI ---

    def extract_text_blocks(self, page_num):
        """Hàm này bây giờ sẽ luôn làm việc trên self.doc gốc, không bị ảnh hưởng."""
        if not self.doc or not (0 <= page_num < self.doc.page_count):
            return []

        page = self.doc.load_page(page_num)
        blocks_data = page.get_text("dict")["blocks"]

        structured_blocks = []
        for block in blocks_data:
            if block['type'] == 0:
                lines_info = []
                for line in block['lines']:
                    line_text = ""
                    if not line['spans']:
                        continue

                    font_size = line['spans'][0]['size']
                    for span in line['spans']:
                        line_text += span['text'] + " "

                    lines_info.append({
                        "text": line_text.strip(),
                        "bbox": line['bbox'],
                        "size": font_size
                    })

                if lines_info:
                    structured_blocks.append({
                        "bbox": block['bbox'],
                        "lines": lines_info
                    })
        return structured_blocks
