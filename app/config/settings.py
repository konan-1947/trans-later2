# app/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()  # Tải các biến từ file .env

APP_NAME = "PDF Translator Pro"
APP_VERSION = "0.1.0 (MVP)"

# Lấy API key từ biến môi trường
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Hằng số cho việc dịch thuật
TRANSLATION_SEPARATOR = "|||---|||"

# Hằng số cho việc render PDF, là nguồn chân lý duy nhất
PDF_RENDER_DPI = 150
