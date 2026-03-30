import pandas as pd
import matplotlib.pyplot as plt
from entsoe import EntsoePandasClient

API_KEY = "69d60be5-c000-412f-bfdb-3eacaa617bb8"

def get_prices_series():
    try:
        client = EntsoePandasClient(api_key=API_KEY)

        today = pd.Timestamp.now(tz="Europe/Brussels").normalize()
        tomorrow = today + pd.Timedelta(days=1)

        prices = client.query_day_ahead_prices("BE", start=today, end=tomorrow)
        return prices

    except Exception as e:
        print("Erreur API :", e)
        return None


def get_price_at_hour(heure_str):
    prices = get_prices_series()

    if prices is None:
        return None

    try:
        heure, minute = map(int, heure_str.split(":"))
    except ValueError:
        return None

    today = pd.Timestamp.now(tz="Europe/Brussels").normalize()
    target_time = today + pd.Timedelta(hours=heure, minutes=minute)

    nearest = prices.index.get_indexer([target_time], method="nearest")[0]
    prix_mwh = prices.iloc[nearest]

    return prix_mwh / 1000


def plot_prices():
    prices = get_prices_series()

    if prices is None:
        print("Impossible de récupérer les prix.")
        return

    prices.plot()
    plt.title("Prix de l'électricité - Belgique")
    plt.xlabel("Heure")
    plt.ylabel("Prix (€/MWh)")
    plt.grid()
    plt.show()