# app/features/translator/image_renderer.py

from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QBuffer, QIODevice
from io import BytesIO


class ImageRenderer:
    def render(self, base_pixmap, structured_blocks, dpi):
        # Bước 1: Chuyển đổi an toàn
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        base_pixmap.save(buffer, "PNG")
        pil_image = Image.open(BytesIO(buffer.data())).convert("RGB")

        draw = ImageDraw.Draw(pil_image)

        # Tính toán scale_factor từ DPI được truyền vào
        scale_factor = dpi / 72.0

        for block in structured_blocks:
            for line in block['lines']:
                bbox = line['bbox']
                original_font_size = line['size']
                translated_text = line.get('translated', '')

                scaled_bbox = (
                    bbox[0] * scale_factor, bbox[1] * scale_factor,
                    bbox[2] * scale_factor, bbox[3] * scale_factor
                )

                bbox_width = scaled_bbox[2] - scaled_bbox[0]

                try:
                    # Lấy màu nền ở vị trí an toàn hơn một chút
                    sample_x = int(
                        scaled_bbox[0] + 2) if scaled_bbox[0] + 2 < pil_image.width else int(scaled_bbox[0])
                    sample_y = int(
                        scaled_bbox[1] + 2) if scaled_bbox[1] + 2 < pil_image.height else int(scaled_bbox[1])
                    bg_color = pil_image.getpixel((sample_x, sample_y))
                except IndexError:
                    bg_color = "white"

                draw.rectangle(scaled_bbox, fill=bg_color)

                try:
                    current_font_size = int(original_font_size * scale_factor)
                    font = ImageFont.truetype(
                        "arial.ttf", size=current_font_size)
                    text_width = draw.textlength(translated_text, font=font)

                    while text_width > bbox_width and current_font_size > 6:
                        current_font_size -= 1
                        font = ImageFont.truetype(
                            "arial.ttf", size=current_font_size)
                        text_width = draw.textlength(
                            translated_text, font=font)

                except (IOError, KeyError):
                    font = ImageFont.load_default()

                draw.text((scaled_bbox[0], scaled_bbox[1]),
                          translated_text, fill="black", font=font)

        # Bước 3: Chuyển đổi an toàn ngược lại
        final_buffer = BytesIO()
        pil_image.save(final_buffer, "PNG")
        final_pixmap = QPixmap()
        final_pixmap.loadFromData(final_buffer.getvalue(), "PNG")

        return final_pixmap
