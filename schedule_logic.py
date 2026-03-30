import sqlite3
from datetime import datetime, timedelta

DB_PATH = "pizzeria.db"


def command_exceeds_day(produit_nom, date_str, heure_depart):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # récupérer l'id du produit à partir de son nom
    cursor.execute("""
        SELECT id
        FROM produits
        WHERE nom = ?
    """, (produit_nom,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        raise ValueError(f"Produit introuvable : {produit_nom}")

    produit_id = result[0]

    # récupérer les durées des étapes du produit
    cursor.execute("""
        SELECT duree_minutes
        FROM etapes_process
        WHERE produit_id = ?
        ORDER BY ordre
    """, (produit_id,))
    steps = cursor.fetchall()

    conn.close()

    total_duration = sum(step[0] for step in steps)

    start_time = datetime.strptime(f"{date_str} {heure_depart}", "%Y-%m-%d %H:%M")
    end_time = start_time + timedelta(minutes=total_duration)
    end_of_day = datetime.strptime(f"{date_str} 23:59", "%Y-%m-%d %H:%M")

    return end_time > end_of_day, end_time.strftime("%H:%M")