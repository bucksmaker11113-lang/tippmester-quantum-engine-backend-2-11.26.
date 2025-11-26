# ============================================================
# Poisson Engine Adapter – egységes EngineBase interfészre kötve
# ============================================================

from backend.core.engine_base import EngineBase
from backend.core.engine_registry import EngineRegistry

# Itt importáljuk a meglévő régi Poisson engine-t
from backend.engine.poisson_engine import PoissonPredictor


@EngineRegistry.register
class PoissonEngineAdapter(EngineBase):
    """
    Az eredeti Poisson motort összeköti az új EngineBase rendszerrel.
    Nem írja át az eredeti modellt, csak becsomagolja.
    """

    def prepare(self, raw_input):
        # A Poisson modell tipikusan xG vagy historical goal data-t vár
        return raw_input.get("stats", raw_input)

    def run_model(self, prepared_input):
        # Meghívjuk az eredeti Poisson motort
        try:
            model = PoissonPredictor()
            return model.predict(prepared_input)
        except Exception as e:
            return {"error": f"Poisson model error: {e}"}

    def postprocess(self, model_output):
        # Egységes formára alakítjuk
        return {
            "engine": "poisson",
            "probabilities": model_output,
            "confidence": 0.85,
            "raw_output": model_output
        }
