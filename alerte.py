import os
from api_electricity import get_negative_price

def generate_negative_price_alert_file():
    negative_prices = get_negative_price()

    if negative_prices is None:
        return "Erreur API", []

    if negative_prices.empty:
        return "Aucun prix négatif aujourd'hui.", []

    os.makedirs("alerts", exist_ok=True)
    filepath = "alerts/negative_prices_alert.txt"

    lines = []
    lines.append("ALERTE PRIX NEGATIFS")
    lines.append("")

    data = []

    for timestamp, price in negative_prices.items():
        heure = timestamp.strftime("%H:%M")
        ligne = f"Heure: {heure} | Prix: {price:.2f} €/MWh"
        lines.append(ligne)
        data.append((heure, round(float(price), 2)))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath, data