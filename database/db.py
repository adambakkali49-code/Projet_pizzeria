import sqlite3

def init_db():  # je crée une fonction pour créer les tables
    conn = sqlite3.connect("pizzeria.db")  # je me connecte à la base
    cursor = conn.cursor()  # je crée un curseur SQL

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS machines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        puissance_w INTEGER,
        operateur_nom TEXT,
        operateur_email TEXT
    )
    """)  # je crée la table machines

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT
    )
    """)  # je crée la table produits

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produit_id INTEGER,
        quantite INTEGER,
        heure_depart TEXT,
        cout_unitaire REAL,
        cout_total REAL
    )
    """)  # je crée la table commandes


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etapes_process (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produit_id INTEGER,
        machine_id INTEGER,
        ordre INTEGER,
        duree_minutes INTEGER
    )
    """)

    conn.commit()  # je sauvegarde
    conn.close()  # je ferme la base

def insert_data():  # fonction pour ajouter les données dans la base
    
    conn = sqlite3.connect("pizzeria.db")  # je me connecte à la base
    cursor = conn.cursor()  # je crée un curseur pour exécuter des commandes SQL

    # -----------------------------
    # AJOUT DES MACHINES
    # -----------------------------
    
    machines = [  # je crée une liste avec mes machines
        ("Pétrin", 800, "jalyl", "jalyl@email.com"),
        ("Four", 3000, "amine", "amine@email.com"),
        ("Trancheuse", 300, "adam", "adam@email.com"),
        ("Emballeuse", 200, "sami", "sami@email.com")
    ]

    cursor.executemany(  # executemany permet d’insérer plusieurs lignes d’un coup
        "INSERT INTO machines (nom, puissance_w, operateur_nom, operateur_email) VALUES (?, ?, ?, ?)",  # ? = valeurs à remplacer
        machines  # je passe ma liste ici
    )

    # -----------------------------
    # AJOUT DES PRODUITS
    # -----------------------------

    produits = [  # liste des pizzas
        ("Creamy Chicken",),
        ("BBQ Chicken",),
        ("Cannibale",),
        ("ECAMnienne",)
    ]

    cursor.executemany(
        "INSERT INTO produits (nom) VALUES (?)",  # ici un seul champ donc un seul ?
        produits
    )

    # -----------------------------
    # RECUPERER LES ID
    # -----------------------------

    cursor.execute("SELECT id, nom FROM produits")  # je récupère les produits avec leurs id
    produits_dict = {nom: id for id, nom in cursor.fetchall()}  
    # je crée un dictionnaire genre {"Creamy Chicken": 1}

    cursor.execute("SELECT id, nom FROM machines")  # pareil pour les machines
    machines_dict = {nom: id for id, nom in cursor.fetchall()}

    # -----------------------------
    # AJOUT DES ETAPES (PROCESS)
    # -----------------------------

    etapes = [  # chaque ligne = une étape
        # Creamy Chicken
        (produits_dict["Creamy Chicken"], machines_dict["Pétrin"], 1, 10),
        (produits_dict["Creamy Chicken"], machines_dict["Four"], 2, 15),
        (produits_dict["Creamy Chicken"], machines_dict["Emballeuse"], 3, 2),

        # BBQ Chicken
        (produits_dict["BBQ Chicken"], machines_dict["Trancheuse"], 1, 3),
        (produits_dict["BBQ Chicken"], machines_dict["Pétrin"], 2, 10),
        (produits_dict["BBQ Chicken"], machines_dict["Four"], 3, 15),
        (produits_dict["BBQ Chicken"], machines_dict["Emballeuse"], 4, 2),

        # Cannibale
        (produits_dict["Cannibale"], machines_dict["Pétrin"], 1, 10),
        (produits_dict["Cannibale"], machines_dict["Four"], 2, 16),
        (produits_dict["Cannibale"], machines_dict["Emballeuse"], 3, 2),

        # ECAMnienne
        (produits_dict["ECAMnienne"], machines_dict["Pétrin"], 1, 12),
        (produits_dict["ECAMnienne"], machines_dict["Four"], 2, 18),
        (produits_dict["ECAMnienne"], machines_dict["Emballeuse"], 3, 2),
    ]

    cursor.executemany(
        "INSERT INTO etapes_process (produit_id, machine_id, ordre, duree_minutes) VALUES (?, ?, ?, ?)",
        etapes
    )

    conn.commit()  # je sauvegarde tout
    conn.close()  # je ferme la base

def show_data():  # fonction pour afficher les données de la base
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    print("\n--- MACHINES ---")
    cursor.execute("SELECT * FROM machines")
    for row in cursor.fetchall():
        print(row)

    print("\n--- PRODUITS ---")
    cursor.execute("SELECT * FROM produits")
    for row in cursor.fetchall():
        print(row)

    print("\n--- ETAPES PROCESS ---")
    cursor.execute("SELECT * FROM etapes_process")
    for row in cursor.fetchall():
        print(row)

    conn.close()



# FONCTIONS POUR L'INTERFACE


def get_machines():  # récupérer machines pour l'interface
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    cursor.execute("SELECT nom, puissance_w, operateur_nom, operateur_email FROM machines")
    machines = cursor.fetchall()

    conn.close()
    return machines


def get_produits():  # récupérer produits pour l'interface
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    cursor.execute("SELECT nom FROM produits")
    produits = cursor.fetchall()

    conn.close()
    return produits

def add_machine(nom, puissance, operateur, email):  # fonction pour ajouter une machine à la base
    conn = sqlite3.connect("pizzeria.db")  # je me connecte à la base
    cursor = conn.cursor()  # je crée un curseur SQL

    cursor.execute(
        "INSERT INTO machines (nom, puissance_w, operateur_nom, operateur_email) VALUES (?, ?, ?, ?)",
        (nom, puissance, operateur, email)
    )  # j'insère une nouvelle machine


    conn.commit()  # je sauvegarde les changements
    conn.close()  # je ferme la base

def add_commande(produit_nom, quantite, heure_depart, cout_unitaire, cout_total):  # ajoute une commande dans la base
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM produits WHERE nom = ?", (produit_nom,))
    resultat = cursor.fetchone()

    if resultat is None:
        conn.close()
        return

    produit_id = resultat[0]

    cursor.execute(
        """
        INSERT INTO commandes (produit_id, quantite, heure_depart, cout_unitaire, cout_total)
        VALUES (?, ?, ?, ?, ?)
        """,
        (produit_id, quantite, heure_depart, cout_unitaire, cout_total)
    )

    conn.commit()
    conn.close()

def get_commandes():  # récupère les commandes avec le nom du produit et les coûts
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT produits.nom, commandes.quantite, commandes.heure_depart,
               commandes.cout_unitaire, commandes.cout_total
        FROM commandes
        JOIN produits ON commandes.produit_id = produits.id
    """)

    commandes = cursor.fetchall()
    conn.close()
    return commandes 


def get_etapes_for_produit(produit_nom):  # récupère les étapes d'un produit avec machine, puissance et durée
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT machines.nom, machines.puissance_w, etapes_process.duree_minutes
        FROM etapes_process
        JOIN produits ON etapes_process.produit_id = produits.id
        JOIN machines ON etapes_process.machine_id = machines.id
        WHERE produits.nom = ?
        ORDER BY etapes_process.ordre
    """, (produit_nom,))

    etapes = cursor.fetchall()
    conn.close()
    return etapes