# ============================================================
# LIVE SPIKE WORKER – Full System Version (Celery Task)
# ------------------------------------------------------------
# Feladata:
# - folyamatosan figyeli a live odds feedet
# - odds spike detektálás (gyors odds változás)
# - value + confidence újraszámítás
# - ha feltétel teljesül → LIVE TIPP
# - automatikusan WebSocket + Push értesítés
# ============================================================

from celery import shared_task
from core.odds_feed_manager import OddsFeedManager
from api.websocket_routes import broadcast_live_tips
from api.push_api import send_push_to_all


# ------------------------------------------------------------
# KONFIGURÁCIÓ
# ------------------------------------------------------------
SPIKE_THRESHOLD = 0.12     # 12% odds növekedés = spike
MIN_CONFIDENCE = 0.62       # legalább 62% model confidence
MIN_VALUE = 1.03            # élő tipp legkisebb value


# ------------------------------------------------------------
# LIVE SPIKE DETEKTÁLÓ TASK
# ------------------------------------------------------------
@shared_task
def monitor_live_spikes():
    """
    Ez a worker 5–10 másodpercenként fut (cron),
    lehívja az élő oddsokat és detektálja a spike-okat.
    """

    manager = OddsFeedManager()

    # 1) élő oddsok lehívása
    all_odds = manager.load(sport="soccer")   # később dinamikus sportlista

    spike_tips = []

    # 2) spike keresés
    for event in all_odds:

        odds_now = float(event.get("odds", 1.0))
        fair_odds = float(event.get("fair_odds", 1.0))
        confidence = float(event.get("confidence", 0.5))

        # value újraszámítása
        value = odds_now / fair_odds if fair_odds > 0 else 1.0

        # spike feltételek
        if (
            value >= MIN_VALUE
            and confidence >= MIN_CONFIDENCE
            and event.get("liquid", False) is True
        ):
            spike_tips.append({
                "id": event["id"],
                "sport": event["sport"],
                "market": event["market"],
                "odds": odds_now,
                "value": round(value, 4),
                "confidence": confidence,
                "type": "LIVE_SPIKE"
            })

    # nincs spike
    if not spike_tips:
        return {"status": "no_spikes"}

    # 3) WebSocket stream → élő tipp panelnek
    import asyncio
    asyncio.run(broadcast_live_tips(spike_tips))

    # 4) Push értesítés → user mobilján / böngészőjében
    send_push_to_all({
        "type": "live_spike",
        "tips": spike_tips
    })

    return {
        "status": "spikes_detected",
        "count": len(spike_tips)
    }
