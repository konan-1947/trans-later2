# app/core/pdf_service.py

import fitz
from PyQt6.QtGui import QImage, QPixmap


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

    def get_page_as_pixmap(self, page_num, dpi):
        """Render ảnh GỐC của trang ở một DPI cụ thể."""
        if not self.doc or not (0 <= page_num < self.doc.page_count):
            return None, 1.0, 1.0  # Trả về giá trị an toàn

        page = self.doc.load_page(page_num)
        page_width_points = page.rect.width
        scale_factor = dpi / 72.0 if page_width_points > 0 else 1.0

        pix = page.get_pixmap(dpi=dpi)
        image = QImage(pix.samples, pix.width, pix.height,
                       pix.stride, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(image), page_width_points, scale_factor

    def get_clean_page_as_pixmap(self, page_num, dpi):
        """Tạo ảnh nền SẠCH ở một DPI cụ thể trên bản sao tạm thời."""
        if not self.file_path:
            return None

        try:
            temp_doc = fitz.open(self.file_path)
            page = temp_doc.load_page(page_num)

            for rect in page.get_text_blocks():
                page.add_redact_annot(rect[:4])

            page.apply_redactions()

            pix = page.get_pixmap(dpi=dpi)
            image = QImage(pix.samples, pix.width, pix.height,
                           pix.stride, QImage.Format.Format_RGB888)

            temp_doc.close()
            return QPixmap.fromImage(image)

        except Exception as e:
            print(f"Error creating clean background: {e}")
            return None

    def extract_text_blocks(self, page_num):
        """Trích xuất dữ liệu theo cấu trúc Khối > Dòng."""
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
