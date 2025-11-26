# ============================================================
# QUANTUM LIVE SPIKE WORKER – V4
# ------------------------------------------------------------
# Javítások:
# - valós odds spike detektálás (current vs previous)
# - multi-sport scan
# - fair odds fallback
# - spike threshold használat
# - biztonságos asyncio futtatás
# - strukturált logika
# ============================================================

from celery import shared_task
from core.odds_feed_manager import OddsFeedManager
from api.websocket_routes import broadcast_live_tips
from api.push_api import send_push_to_all

SPIKE_THRESHOLD = 0.12     # 12% odds drift
MIN_CONFIDENCE = 0.62
MIN_VALUE = 1.03

SPORTS = ["soccer", "tennis", "basketball", "ice_hockey"]


@shared_task
def monitor_live_spikes():

    manager = OddsFeedManager()
    spike_tips = []

    for sport in SPORTS:

        events = manager.load(sport=sport)

        for event in events:

            odds_now = float(event.get("odds", 1.0))
            odds_prev = float(event.get("prev_odds", odds_now))
            fair = float(event.get("fair_odds", odds_now))
            conf = float(event.get("confidence", 0.5))
            liquid = event.get("liquid", False)

            # 1) valódi spike detektálás
            if odds_prev <= 0:
                continue

            spike_ratio = (odds_now - odds_prev) / odds_prev

            if spike_ratio < SPIKE_THRESHOLD:
                continue  # nincs spike

            # 2) value kalkuláció
            value = odds_now / fair if fair > 0 else 1.0

            if value < MIN_VALUE:
                continue

            if conf < MIN_CONFIDENCE:
                continue

            if not liquid:
                continue

            spike_tips.append({
                "id": event["id"],
                "sport": sport,
                "market": event["market"],
                "odds": odds_now,
                "prev_odds": odds_prev,
                "spike": round(spike_ratio, 3),
                "value": round(value, 4),
                "confidence": round(conf, 3),
                "type": "LIVE_SPIKE"
            })

    if not spike_tips:
        return {"status": "no_spikes"}

    # SAFE async WS call
    import asyncio
    try:
        asyncio.get_running_loop()
        loop = None
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop:
        loop.run_until_complete(broadcast_live_tips(spike_tips))
    else:
        asyncio.run(broadcast_live_tips(spike_tips))

    # push
    send_push_to_all({
        "type": "live_spike",
        "tips": spike_tips
    })

    return {
        "status": "spikes_detected",
        "count": len(spike_tips)
    }
