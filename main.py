# main.py
import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def main():
    # Kiểm tra API Key trước khi khởi động
    from app.config.settings import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        print(
            "FATAL ERROR: GEMINI_API_KEY is not set. Please create a .env file and add it.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
