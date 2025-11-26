# ============================================================
# BETFAIR ADAPTER – Raw Betfair Odds → Normalized Format
# Full system version
# ============================================================

import uuid


class BetfairAdapter:
    """
    Betfair API által visszaadott odds struktúra normalizálása.
    A Betfair exchange likvid piac → értékes forrás single tippekhez.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------
    # FAIR ODDS KONVERZIÓ (odds → implied probability)
    # ------------------------------------------------------------
    def implied_probability(self, odds):
        if odds <= 1.0:
            return 1.0
        return round(1.0 / odds, 4)

    # ------------------------------------------------------------
    # EVENT NORMALIZATION
    # ------------------------------------------------------------
    def normalize_betfair_event(self, event):
        """
        A Betfair saját struktúrájából közös egységes formátum:
        Minimális mezők:
        - id
        - sport
        - market
        - odds
        - fair_odds
        - confidence (placeholder)
        - liquid (always True – exchange)
        - provider: "betfair"
        """

        back_odds = float(event.get("back_odds", 1.0))
        fair_odds = 1.0 / max(self.implied_probability(back_odds), 0.01)

        return {
            "id": event.get("id") or str(uuid.uuid4()),
            "sport": event.get("sport", "foci"),
            "market": event.get("market", "1x2"),

            "odds": back_odds,
            "fair_odds": fair_odds,
            "value": round(back_odds / fair_odds, 4),

            "confidence": float(event.get("confidence", 0.6)),

            # Betfair = LIQUID
            "liquid": True,

            "provider": "betfair"
        }

    # ------------------------------------------------------------
    # RAW LIST NORMALIZATION
    # ------------------------------------------------------------
    def normalize_list(self, betfair_list):
        """
        Több esemény normalizálása.
        """
        normalized = []

        for ev in betfair_list:
            try:
                norm = self.normalize_betfair_event(ev)
                normalized.append(norm)
            except:
                continue

        return normalized
