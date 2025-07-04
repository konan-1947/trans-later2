# app/features/translator/image_renderer.py

from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QBuffer, QIODevice
from io import BytesIO
import fitz
from app.config.settings import PDF_RENDER_DPI


class ImageRenderer:
    def render(self, base_pixmap, structured_blocks):
        # Bước 1: Chuyển đổi an toàn
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        base_pixmap.save(buffer, "PNG")
        pil_image = Image.open(BytesIO(buffer.data())).convert("RGB")

        draw = ImageDraw.Draw(pil_image)

        # Tính toán scale factor chuẩn xác
        scale_factor = PDF_RENDER_DPI / 72.0

        for block in structured_blocks:
            for line in block['lines']:
                bbox = line['bbox']
                original_font_size = line['size']
                translated_text = line.get('translated', '')

                scaled_bbox = (
                    bbox[0] * scale_factor, bbox[1] * scale_factor,
                    bbox[2] * scale_factor, bbox[3] * scale_factor
                )

                # Chiều rộng của khung chứa văn bản
                bbox_width = scaled_bbox[2] - scaled_bbox[0]

                # Lấy màu nền
                try:
                    bg_color = pil_image.getpixel(
                        (int(scaled_bbox[0] + 1), int(scaled_bbox[1] + 1)))
                except IndexError:
                    bg_color = "white"

                # Vẽ hình chữ nhật XÓA
                draw.rectangle(scaled_bbox, fill=bg_color)

                # --- LOGIC MỚI: TỰ ĐỘNG CO DÃN CỠ CHỮ ĐỂ VỪA KHUNG ---
                try:
                    # Bắt đầu với cỡ chữ lý tưởng
                    current_font_size = int(original_font_size * scale_factor)
                    font = ImageFont.truetype(
                        "arial.ttf", size=current_font_size)

                    # Đo chiều dài thực tế của text đã dịch
                    text_width = draw.textlength(translated_text, font=font)

                    # Vòng lặp: Nếu text vẫn bị tràn và cỡ chữ còn có thể giảm
                    while text_width > bbox_width and current_font_size > 6:
                        current_font_size -= 1  # Giảm cỡ chữ đi 1
                        font = ImageFont.truetype(
                            "arial.ttf", size=current_font_size)
                        text_width = draw.textlength(
                            translated_text, font=font)

                except (IOError, KeyError):
                    font = ImageFont.load_default()
                # --- KẾT THÚC LOGIC MỚI ---

                # Vẽ văn bản đã dịch với cỡ chữ đã được điều chỉnh hoàn hảo
                draw.text((scaled_bbox[0], scaled_bbox[1]),
                          translated_text, fill="black", font=font)

        # Bước 3: Chuyển đổi an toàn ngược lại
        final_buffer = BytesIO()
        pil_image.save(final_buffer, "PNG")
        final_pixmap = QPixmap()
        final_pixmap.loadFromData(final_buffer.getvalue(), "PNG")

        return final_pixmap
