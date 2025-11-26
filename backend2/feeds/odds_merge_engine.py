# ============================================================
# ODDS MERGE ENGINE – Full System Version
# ------------------------------------------------------------
# Feladata:
# - Betfair / Pinnacle / OddsAPI oddsok normálizálása
# - Duplikált események egyesítése
# - Közös egységesített tippelem formátum készítése
# - Fair odds + value számítás
# ============================================================

import uuid


class OddsMergeEngine:
    """
    Odds feed adatmezők egységesítése:
    Bemenet: 3 különböző odds feed (dict)
    Kimenet: egységes, normalizált odds lista
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------
    # FAIR ODDS + VALUE
    # ------------------------------------------------------------
    def calculate_value(self, odds, fair_odds):
        """
        value = (bookmaker odds) / (valós, modellezett fair odds)
        """
        if fair_odds <= 0:
            return 1.0
        return round(odds / fair_odds, 4)

    # ------------------------------------------------------------
    # FORMÁTUM NORMALIZÁLÁS
    # ------------------------------------------------------------
    def normalize_event(self, source_event, source_name):
        """
        Bármely odds API-ból egységesített objektumot készít.
        Minimális mezők:
        - id
        - sport
        - market
        - odds
        - fair_odds
        - value
        - confidence
        - liquid
        - provider
        """

        return {
            "id": source_event.get("id") or str(uuid.uuid4()),
            "sport": source_event.get("sport", "foci"),
            "market": source_event.get("market", "1x2"),
            "odds": float(source_event.get("odds", 1.0)),

            # fair odds → modellekből jön majd
            "fair_odds": float(source_event.get("fair_odds", 1.0)),

            # value automatikus számítása
            "value": self.calculate_value(
                float(source_event.get("odds", 1.0)),
                float(source_event.get("fair_odds", 1.0)),
            ),

            # AI confidence skála → később AI modul tölti
            "confidence": float(source_event.get("confidence", 0.5)),

            # liquid piac (fontos a single tippeknél)
            "liquid": source_event.get("liquid", True),

            # forrásjelölés (debug)
            "provider": source_name,
        }

    # ------------------------------------------------------------
    # MERGING OF ALL SOURCES
    # ------------------------------------------------------------
    def merge_all(self, odds_sources: dict):
        """
        odds_sources = {
            "betfair": [...],
            "pinnacle": [...],
            "oddsapi": [...]
        }
        """

        combined = []

        for provider, events in odds_sources.items():
            if not isinstance(events, list):
                continue

            for event in events:
                try:
                    normalized = self.normalize_event(event, provider)
                    combined.append(normalized)
                except:
                    continue

        # ------------------------------------------------------------
        # DUPLIKÁCIÓK KEZELÉSE (ugyanaz az esemény több forrásból)
        # ------------------------------------------------------------
        final = {}
        for e in combined:
            event_id = e["id"]

            if event_id not in final:
                final[event_id] = e
            else:
                # Ha több provider adja ugyanazt → a jobb value megy tovább
                old = final[event_id]
                if e["value"] > old["value"]:
                    final[event_id] = e

        # visszaadjuk a merge-elt listát
        return list(final.values())
