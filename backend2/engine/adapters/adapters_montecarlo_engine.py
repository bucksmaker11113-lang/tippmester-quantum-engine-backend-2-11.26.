# ============================================================
# Monte Carlo Engine Adapter – EngineBase interfészen
# ============================================================

from backend.core.engine_base import EngineBase
from backend.core.engine_registry import EngineRegistry

# Meglévő Monte Carlo modell importálása
from backend.engine.montecarlo_v3_engine import MonteCarloSimulatorV3


@EngineRegistry.register
class MonteCarloEngineAdapter(EngineBase):
    """
    A Monte Carlo-alapú kimenetel-szimulációt végző motor adaptere.
    """

    def prepare(self, raw_input):
        # Monte Carlo szimuláció általában odds, form és expected goals adatot vár
        return raw_input.get("match_data", raw_input)

    def run_model(self, prepared_input):
        try:
            model = MonteCarloSimulatorV3()
            return model.simulate(prepared_input)
        except Exception as e:
            return {"error": f"MonteCarlo model error: {e}"}

    def postprocess(self, model_output):
        return {
            "engine": "montecarlo_v3",
            "probabilities": model_output.get("probabilities", None),
            "confidence": model_output.get("stability_score", 0.75),
            "raw_output": model_output
        }
