from PyQt6 import QtWidgets  # j'importe PyQt
from gui.main_window_ui import Ui_MainWindow  # j'importe l'interface générée par Qt Designer
from database.db import get_machines, get_produits, add_machine  # j'importe mes fonctions SQL

class MainWindow(QtWidgets.QMainWindow):  # je crée la fenêtre principale
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()  # je crée l'objet interface
        self.ui.setupUi(self)  # j'applique l'interface à la fenêtre

        # je connecte les boutons de l'interface à mes fonctions Python
        self.ui.btnRefresh.clicked.connect(self.load_data)
        self.ui.btnAddMachine.clicked.connect(self.add_machine_from_form)

        self.load_data()  # je charge les données au démarrage

    def load_data(self):  # fonction pour afficher les machines et produits
        machines = get_machines()  # je récupère les machines depuis la base
        produits = get_produits()  # je récupère les produits depuis la base

        self.ui.textMachines.clear()  # je vide la zone machines
        for m in machines:
            nom, puissance, operateur, email = m
            self.ui.textMachines.append(
                f"Nom: {nom} | Puissance: {puissance} W | Opérateur: {operateur} | Email: {email}"
            )  # j'affiche chaque machine

        self.ui.textProduits.clear()  # je vide la zone produits
        for p in produits:
            self.ui.textProduits.append(p[0])  # j'affiche chaque produit

    def add_machine_from_form(self):  # fonction appelée quand on clique sur ajouter
        nom = self.ui.inputNom.text().strip()  # je lis le nom
        puissance = self.ui.inputPuissance.text().strip()  # je lis la puissance
        operateur = self.ui.inputOperateur.text().strip()  # je lis l'opérateur
        email = self.ui.inputEmail.text().strip()  # je lis l'email

        # je vérifie que tous les champs sont remplis
        if not nom or not puissance or not operateur or not email:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        # je vérifie que la puissance est bien un nombre entier
        if not puissance.isdigit():
            QtWidgets.QMessageBox.warning(self, "Erreur", "La puissance doit être un nombre entier.")
            return

        add_machine(nom, int(puissance), operateur, email)  # j'ajoute la machine à la base

        # je vide les champs après ajout
        self.ui.inputNom.clear()
        self.ui.inputPuissance.clear()
        self.ui.inputOperateur.clear()
        self.ui.inputEmail.clear()

        self.load_data()  # je recharge l'affichage