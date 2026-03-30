import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from mail import write_mail_to_file

DB_PATH = "pizzeria.db"


def generate_operator_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.produit_id, c.heure_depart, p.nom
        FROM commandes c
        JOIN produits p ON c.produit_id = p.id
    """)
    commandes = cursor.fetchall()

    tasks_by_operator = defaultdict(list)

    for commande_id, produit_id, heure_depart, nom_produit in commandes:
        start_time = datetime.strptime(heure_depart, "%H:%M")

        cursor.execute("""
            SELECT ep.duree_minutes,
                   m.nom,
                   m.operateur_nom,
                   m.operateur_email
            FROM etapes_process ep
            JOIN machines m ON ep.machine_id = m.id
            WHERE ep.produit_id = ?
            ORDER BY ep.ordre
        """, (produit_id,))
        etapes = cursor.fetchall()

        current_time = start_time

        for duree, nom_machine, op_nom, op_email in etapes:
            end_time = current_time + timedelta(minutes=duree)

            if op_email:
                tasks_by_operator[op_email].append({
                    "operateur_nom": op_nom,
                    "produit": nom_produit,
                    "machine": nom_machine,
                    "start": current_time.strftime("%H:%M"),
                    "end": end_time.strftime("%H:%M")
                })

            current_time = end_time

    conn.close()
    return tasks_by_operator


def send_operator_mails():
    tasks = generate_operator_tasks()

    if not tasks:
        raise ValueError("Aucune tâche trouvée pour générer les mails.")

    for email, taches in tasks.items():
        operateur_nom = taches[0]["operateur_nom"]

        body = []
        body.append(f"Bonjour {operateur_nom},\n")
        body.append("Voici vos tâches prévues :\n")

        for t in taches:
            body.append(
                f"- {t['produit']} | {t['machine']} | {t['start']} -> {t['end']}"
            )

        subject = "Planning opérateur"

        write_mail_to_file(email, subject, "\n".join(body))

