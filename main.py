#!/usr/bin/env python3
"""X3 Flasher - ESP32 阅星瞳 X3 备份刷机工具"""

import sys
from PyQt5.QtWidgets import QApplication
from ui import Win as FlasherWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FlasherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
