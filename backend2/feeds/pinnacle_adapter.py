# ============================================================
# PINNACLE ADAPTER – Pinnacle Odds → Normalized Format
# Full system version
# ============================================================

import uuid


class PinnacleAdapter:
    """
    Pinnacle API odds normalizálása az egységes rendszerhez.
    A Pinnacle kiemelten megbízható (nagy likviditás),
    ezért gyakran pontosabb értéket ad, mint más feedek.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------
    # FAIR ODDS KONVERZIÓ (odds → implied prob → fair odds)
    # ------------------------------------------------------------
    def implied_probability(self, odds):
        if odds <= 1.0:
            return 1.0
        return round(1.0 / odds, 4)

    # ------------------------------------------------------------
    # EGY ESEMÉNY NORMALIZÁLÁSA
    # ------------------------------------------------------------
    def normalize_pinnacle_event(self, event):
        """
        A Pinnacle odds feed adatait konzisztens formátumba alakítja.
        Minimális elvárt mezők:
        - id
        - sport
        - market
        - odds
        - fair_odds
        - confidence
        - liquid
        - provider
        """

        odds = float(event.get("odds", 1.0))
        fair_odds = 1.0 / max(self.implied_probability(odds), 0.01)

        return {
            "id": event.get("id") or str(uuid.uuid4()),
            "sport": event.get("sport", "foci"),
            "market": event.get("market", "1x2"),

            "odds": odds,
            "fair_odds": fair_odds,
            "value": round(odds / fair_odds, 4),

            # A confidence-t később az AI modellek frissítik
            "confidence": float(event.get("confidence", 0.62)),

            # Pinnacle likvid piac → mindig True
            "liquid": True,

            "provider": "pinnacle"
        }

    # ------------------------------------------------------------
    # LISTA NORMALIZÁLÁSA
    # ------------------------------------------------------------
    def normalize_list(self, pinnacle_list):
        """
        A Pinnacle feed több eseményének normalizálása.
        """
        normalized = []

        for ev in pinnacle_list:
            try:
                norm = self.normalize_pinnacle_event(ev)
                normalized.append(norm)
            except:
                continue

        return normalized
