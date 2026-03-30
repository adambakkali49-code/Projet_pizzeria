import os
os.environ["QT_QPA_PLATFORM"] = "windows"

import sys
from PyQt6 import QtWidgets
from gui.main_window import MainWindow
from database.db import init_db, insert_data

init_db()
#insert_data()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())