# ============================================================
# Live Engine Adapter – valós idejű (in-play) modell illesztése
# ============================================================

from backend.core.engine_base import EngineBase
from backend.core.engine_registry import EngineRegistry

# Meglévő Live Engine importálása
from backend.engine.live_engine import LiveMatchPredictor


@EngineRegistry.register
class LiveEngineAdapter(EngineBase):
    """
    A valós idejű élő meccs prediktor adaptere.
    """

    def prepare(self, raw_input):
        # A live engine tipikusan real-time feedet vár
        return raw_input.get("live_feed", raw_input)

    def run_model(self, prepared_input):
        try:
            model = LiveMatchPredictor()
            return model.predict(prepared_input)
        except Exception as e:
            return {"error": f"Live engine error: {e}"}

    def postprocess(self, model_output):
        # Standardizált output formátum élő adatokra
        return {
            "engine": "live_engine",
            "probabilities": model_output.get("live_probabilities", None),
            "confidence": model_output.get("confidence", 0.70),
            "raw_output": model_output
        }
