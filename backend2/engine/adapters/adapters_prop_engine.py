# ============================================================
# Prop Engine Adapter – játékos market / props predikciós motor
# ============================================================

from backend.core.engine_base import EngineBase
from backend.core.engine_registry import EngineRegistry

# Meglévő Prop Engine importálása
from backend.engine.prop_engine import PropPredictor


@EngineRegistry.register
class PropEngineAdapter(EngineBase):
    """
    A player props (pl. gól, lövés, lap, assziszt) előrejelző motor adaptere.
    """

    def prepare(self, raw_input):
        # A prop engine általában player stat inputokat vár
        return raw_input.get("player_stats", raw_input)

    def run_model(self, prepared_input):
        try:
            model = PropPredictor()
            return model.predict(prepared_input)
        except Exception as e:
            return {"error": f"Prop model error: {e}"}

    def postprocess(self, model_output):
        return {
            "engine": "prop_engine",
            "probabilities": model_output.get("prop_predictions", None),
            "confidence": model_output.get("confidence", 0.72),
            "raw_output": model_output
        }
