from database.db import get_etapes_for_produit
from api_electricity import get_price_at_hour

def calculer_cout_produit(produit_nom, heure_depart):
    etapes = get_etapes_for_produit(produit_nom)

    prix_kwh = get_price_at_hour(heure_depart)
    if prix_kwh is None:
        raise ValueError("API ENTSO-E indisponible, impossible de calculer le coût variable.")

    cout_total = 0

    for nom_machine, puissance_w, duree_minutes in etapes:
        puissance_kw = puissance_w / 1000
        duree_heures = duree_minutes / 60
        energie_kwh = puissance_kw * duree_heures
        cout_etape = energie_kwh * prix_kwh
        cout_total += cout_etape

    return round(cout_total, 4)


def calculer_cout_commande(produit_nom, quantite, heure_depart):
    cout_unitaire = calculer_cout_produit(produit_nom, heure_depart)
    cout_total = cout_unitaire * quantite

    return round(cout_unitaire, 4), round(cout_total, 4)