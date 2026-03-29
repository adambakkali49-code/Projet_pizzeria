import sys
from PyQt6 import QtWidgets

from gui.main_window import MainWindow
from database.db import init_db, insert_data

init_db()  # je crée la base
# insert_data()  # je laisse commenté sinon ça remet des doublons

app = QtWidgets.QApplication(sys.argv)  # je démarre l'application
window = MainWindow()  # je crée la fenêtre
window.show()  # j'affiche la fenêtre
sys.exit(app.exec())  # je lance la boucle