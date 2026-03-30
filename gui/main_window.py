from PyQt6 import QtWidgets
from gui.main_window_ui import Ui_MainWindow
from database.db import (
    get_machines, get_produits, add_machine, add_commande,
    get_commandes, update_machine, delete_machine
)
from api_electricity import plot_prices
from cost import calculer_cout_commande
from datetime import datetime
from mail_fonction import send_operator_mails
from alerte import generate_negative_price_alert_file
from schedule_logic import command_exceeds_day


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        date = datetime.now().strftime("%d/%m/%Y")
        self.ui.labelDate.setText(date)

        self.ui.btnRefresh.clicked.connect(self.load_data)
        self.ui.btnAddMachine.clicked.connect(self.add_machine_from_form)
        self.ui.btnAddCommande.clicked.connect(self.add_commande_from_form)
        self.ui.pushButtonPrices.clicked.connect(self.show_prices)
        self.ui.pushButton_send_mail.clicked.connect(self.generate_mails)
        self.ui.pushButton_negative_alert.clicked.connect(self.check_negative_prices)
        self.ui.btnModifyMachine.clicked.connect(self.modify_machine_from_form)
        self.ui.btnDeleteMachine.clicked.connect(self.delete_machine_from_form)
        
        

        self.load_data()
        self.load_produits_combo()
        self.load_commandes()

    def load_data(self):
        machines = get_machines()
        produits = get_produits()

        self.ui.textMachines.clear()
        for m in machines:
            nom, puissance, operateur, email = m
            self.ui.textMachines.append(
                f"Nom: {nom} | Puissance: {puissance} W | Opérateur: {operateur} | Email: {email}"
            )

        self.ui.textProduits.clear()
        for p in produits:
            self.ui.textProduits.append(p[0])

    def add_machine_from_form(self):
        nom = self.ui.inputNom.text().strip()
        puissance = self.ui.inputPuissance.text().strip()
        operateur = self.ui.inputOperateur.text().strip()
        email = self.ui.inputEmail.text().strip()

        if not nom or not puissance or not operateur or not email:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        if not puissance.isdigit():
            QtWidgets.QMessageBox.warning(self, "Erreur", "La puissance doit être un nombre entier.")
            return

        add_machine(nom, int(puissance), operateur, email)

        self.ui.inputNom.clear()
        self.ui.inputPuissance.clear()
        self.ui.inputOperateur.clear()
        self.ui.inputEmail.clear()

        self.load_data()

    def modify_machine_from_form(self):
        old_nom = self.ui.inputNom.text().strip()
        puissance = self.ui.inputPuissance.text().strip()
        operateur = self.ui.inputOperateur.text().strip()
        email = self.ui.inputEmail.text().strip()

        if not old_nom or not puissance or not operateur or not email:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        if not puissance.isdigit():
            QtWidgets.QMessageBox.warning(self, "Erreur", "La puissance doit être un nombre entier.")
            return

        update_machine(old_nom, old_nom, int(puissance), operateur, email)

        QtWidgets.QMessageBox.information(self, "Succès", "Machine modifiée avec succès.")

        self.ui.inputNom.clear()
        self.ui.inputPuissance.clear()
        self.ui.inputOperateur.clear()
        self.ui.inputEmail.clear()

        self.load_data()

    def delete_machine_from_form(self):
        nom = self.ui.inputNom.text().strip()

        if not nom:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Entre le nom de la machine à supprimer.")
            return

        delete_machine(nom)

        QtWidgets.QMessageBox.information(self, "Succès", "Machine supprimée avec succès.")

        self.ui.inputNom.clear()
        self.ui.inputPuissance.clear()
        self.ui.inputOperateur.clear()
        self.ui.inputEmail.clear()

        self.load_data()

    def load_produits_combo(self):
        produits = get_produits()
        self.ui.comboProduit.clear()

        for p in produits:
            self.ui.comboProduit.addItem(p[0])

    def add_commande_from_form(self):
        produit = self.ui.comboProduit.currentText()
        quantite = self.ui.inputQuantite.text().strip()
        heure = self.ui.inputHeureDepart.text().strip()
        
        

        if not produit or not quantite or not heure:
            QtWidgets.QMessageBox.warning(
                self,
                "Champs manquants",
                "Veuillez remplir tous les champs."
            )
            return

        try:
            int(quantite)
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self,
                "Erreur",
                "La quantité doit être un nombre entier."
            )
            return

        try:
            datetime.strptime(heure, "%H:%M")
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self,
                "Erreur",
                "L'heure doit être au format HH:MM."
            )
            return

        date_str = datetime.now().strftime("%Y-%m-%d")

        # vérification automatique : est-ce que ça finit avant la fin de la journée ?
        exceeds, end_time = command_exceeds_day(produit, date_str, heure)

        if exceeds:
            QtWidgets.QMessageBox.warning(
                self,
                "Alerte",
                f"La commande ne sera pas terminée avant la fin de la journée.\n"
                f"Heure de fin prévue : {end_time}"
            )
            return

        # ici tu gardes ton code actuel pour enregistrer la commande dans la base
        # exemple :
        # self.db.add_commande(produit, quantite, heure)

        QtWidgets.QMessageBox.information(
            self,
            "Succès",
            "Commande ajoutée avec succès."
        )

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

    def load_commandes(self):
        commandes = get_commandes()
        self.ui.textCommandes.clear()

        for commande in commandes:
            produit, quantite, heure, cout_unitaire, cout_total = commande
            self.ui.textCommandes.append(
                f"Produit: {produit} | Quantité: {quantite} | Heure de départ: {heure} | Coût unitaire: {cout_unitaire} € | Coût total: {cout_total} €"
            )

    def generate_mails(self):
        try:
            send_operator_mails()
            QtWidgets.QMessageBox.information(
                self,
                "Succès",
                "Mails générés dans le dossier mails/"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Erreur",
                str(e)
            )

    def check_negative_prices(self):
        result, data = generate_negative_price_alert_file()

        if isinstance(result, str) and result.startswith("Erreur"):
            QtWidgets.QMessageBox.critical(self, "Erreur", result)
            return

        if not data:
            QtWidgets.QMessageBox.information(self, "Info", "Aucun prix négatif aujourd'hui.")
            return

        self.ui.tableWidget_negative_prices.setRowCount(len(data))
        self.ui.tableWidget_negative_prices.setColumnCount(2)
        self.ui.tableWidget_negative_prices.setHorizontalHeaderLabels(["Heure", "Prix €/MWh"])

        for row, (heure, prix) in enumerate(data):
            self.ui.tableWidget_negative_prices.setItem(row, 0, QtWidgets.QTableWidgetItem(heure))
            self.ui.tableWidget_negative_prices.setItem(row, 1, QtWidgets.QTableWidgetItem(str(prix)))

        QtWidgets.QMessageBox.information(
            self,
            "Alerte",
            f"Prix négatifs détectés.\nFichier créé : {result}"
        )

    def show_prices(self):
        plot_prices()