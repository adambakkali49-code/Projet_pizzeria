from PyQt6 import QtWidgets  # j'importe PyQt
from gui.main_window_ui import Ui_MainWindow  # j'importe l'interface générée par Qt Designer
from database.db import get_machines, get_produits, add_machine, add_commande, get_commandes  # j'importe mes fonctions SQL
from api_electricity import plot_prices
from cost import calculer_cout_commande

class MainWindow(QtWidgets.QMainWindow):  # je crée la fenêtre principale
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()  # je crée l'objet interface
        self.ui.setupUi(self)  # j'applique l'interface à la fenêtre

        # je connecte les boutons de l'interface à mes fonctions Python
        self.ui.btnRefresh.clicked.connect(self.load_data)
        self.ui.btnAddMachine.clicked.connect(self.add_machine_from_form)
        self.ui.btnAddCommande.clicked.connect(self.add_commande_from_form)
        self.ui.pushButtonPrices.clicked.connect(self.show_prices)

        self.load_data()  # je charge les données au démarrage
        self.load_produits_combo()
        self.load_commandes()

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
    
    def load_produits_combo(self):  # je remplis la liste déroulante avec les produits
        produits = get_produits()
        self.ui.comboProduit.clear()

        for p in produits:
            self.ui.comboProduit.addItem(p[0])

    def add_commande_from_form(self):
        produit = self.ui.comboProduit.currentText()
        quantite = self.ui.inputQuantite.text().strip()
        heure = self.ui.inputHeureDepart.text().strip()

        if not produit or not quantite or not heure:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        if not quantite.isdigit():
            QtWidgets.QMessageBox.warning(self, "Erreur", "La quantité doit être un nombre entier.")
            return

        quantite_int = int(quantite)

        try:
            cout_unitaire, cout_total = calculer_cout_commande(produit, quantite_int, heure)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur API", str(e))
            return

        add_commande(produit, quantite_int, heure, cout_unitaire, cout_total)

        QtWidgets.QMessageBox.information(
            self,
            "Coût estimé",
            f"Produit : {produit}\n"
            f"Quantité : {quantite_int}\n"
            f"Heure de départ : {heure}\n"
            f"Coût unitaire : {cout_unitaire} €\n"
            f"Coût total : {cout_total} €"
        )

        self.ui.inputQuantite.clear()
        self.ui.inputHeureDepart.clear()
        self.load_commandes()    

    def load_commandes(self):  # j'affiche les commandes dans la zone texte
        commandes = get_commandes()
        self.ui.textCommandes.clear()

        for commande in commandes:
            produit, quantite, heure, cout_unitaire, cout_total = commande
            self.ui.textCommandes.append(
                f"Produit: {produit} | Quantité: {quantite} | Heure de départ: {heure} | Coût unitaire: {cout_unitaire} € | Coût total: {cout_total} €"
            )

    def show_prices(self):
        plot_prices()