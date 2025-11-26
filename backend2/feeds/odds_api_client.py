# ============================================================
# ODDS API CLIENT – External Odds Fetcher
# Full upgrade version – Betfair / Pinnacle / OddsAPI kompatibilis
# ============================================================

import httpx
import asyncio


class OddsAPIClient:
    """
    Külső odds API-k egységes kliense.
    Támogatott források (bővíthető):
    - Betfair
    - Pinnacle
    - OddsAPI
    - Unibet API
    """

    def __init__(self):
        self.betfair_url = "https://api.betfair.com/exchange/odds/json"
        self.pinnacle_url = "https://api.pinnacle.com/v1/odds"
        self.oddsapi_url = "https://api.the-odds-api.com/v4/sports"

        # ha később kell API kulcs:
        self.api_key = "YOUR_ODDS_API_KEY"

    # ============================================================
    # BETFAIR
    # ============================================================
    async def fetch_from_betfair(self, sport="soccer"):
        """
        Betfair odds letöltése.
        API limitált, de a valós rendszerrel integrálható.
        """

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.betfair_url}/{sport}")
                return response.json()
        except:
            return []

    # ============================================================
    # PINNACLE
    # ============================================================
    async def fetch_from_pinnacle(self, sport="soccer"):
        """
        Pinnacle odds feed (nagy likviditású, gyors).
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.pinnacle_url}/{sport}")
                return response.json()
        except:
            return []

    # ============================================================
    # ODDS API (multi-sport aggregator)
    # ============================================================
    async def fetch_from_oddsapi(self, sport_key="soccer_epl"):
        """
        OddsAPI – több bookmaker összevont oddsai.
        """
        url = f"{self.oddsapi_url}/{sport_key}/odds?apiKey={self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                return response.json()
        except:
            return []

    # ============================================================
    # ÖSSZEGYŰJTÉS (PARALLEL)
    # ============================================================
    async def fetch_all_sources(self, sport="soccer"):
        """
        Mindhárom odds forrás egyszerre lekérve.
        Ez 3× gyorsabb, mint szekvenciálisan.
        """
        betfair_task = self.fetch_from_betfair(sport)
        pinnacle_task = self.fetch_from_pinnacle(sport)
        oddsapi_task = self.fetch_from_oddsapi(sport)

        results = await asyncio.gather(
            betfair_task,
            pinnacle_task,
            oddsapi_task,
            return_exceptions=True
        )

        # raw list of all three sources
        return {
            "betfair": results[0] if isinstance(results[0], list) else [],
            "pinnacle": results[1] if isinstance(results[1], list) else [],
            "oddsapi": results[2] if isinstance(results[2], list) else []
        }
