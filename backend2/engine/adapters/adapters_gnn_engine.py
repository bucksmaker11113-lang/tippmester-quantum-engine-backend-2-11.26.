# ============================================================
# GNN Engine Adapter – Graph Neural Network modell illesztése
# ============================================================

from backend.core.engine_base import EngineBase
from backend.core.engine_registry import EngineRegistry

# Meglévő GNN motor importja
from backend.engine.gnn_engine import GNN_Model


@EngineRegistry.register
class GNNEngineAdapter(EngineBase):
    """
    A Graph Neural Network alapú predikciós motor egységes adaptere.
    """

    def prepare(self, raw_input):
        # A GNN általában graph formátumot vár.
        # Kivesszük a "graph" kulcsot, vagy ha nincs, visszaadjuk az eredetit.
        return raw_input.get("graph", raw_input)

    def run_model(self, prepared_input):
        try:
            model = GNN_Model()
            return model.predict(prepared_input)
        except Exception as e:
            return {"error": f'GNN model error: {e}'}

    def postprocess(self, model_output):
        return {
            "engine": "gnn",
            "probabilities": model_output.get("probabilities", None),
            "confidence": model_output.get("confidence", 0.78),
            "raw_output": model_output
        }
