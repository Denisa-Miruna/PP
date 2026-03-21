import sys
from multiprocessing import freeze_support
from PyQt5.QtWidgets import QApplication
from html_converter import HTMLConverter

# Punctul de intrare al aplicației.
# Creează fereastra și pornește bucla de evenimente PyQt5.

if __name__ == '__main__':
    freeze_support()            # Necesar pe Windows pentru multiprocessing

    app = QApplication(sys.argv)
    window = HTMLConverter()
    window.show()
    sys.exit(app.exec_())       # app.exec_() = echivalentul mainloop() din Tkinter