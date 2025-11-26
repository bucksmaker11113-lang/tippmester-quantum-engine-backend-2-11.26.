# ============================================================
# LSTM RNN Engine Adapter – EngineBase interfészen
# ============================================================

from backend.core.engine_base import EngineBase
from backend.core.engine_registry import EngineRegistry

# Meglévő LSTM modell importálása
from backend.engine.lstm_rnn_engine import LSTM_RNN_Model


@EngineRegistry.register
class LSTMEngineAdapter(EngineBase):
    """
    Az LSTM-alapú idősort prediktáló motort illeszti az egységes keretrendszerhez.
    """

    def prepare(self, raw_input):
        # LSTM jellemzően idősort vár → kivesszük a historical sequence részét
        return raw_input.get("sequence", raw_input)

    def run_model(self, prepared_input):
        try:
            model = LSTM_RNN_Model()
            return model.predict(prepared_input)
        except Exception as e:
            return {"error": f"LSTM model error: {e}"}

    def postprocess(self, model_output):
        return {
            "engine": "lstm_rnn",
            "probabilities": model_output.get("probabilities", None),
            "confidence": model_output.get("confidence", 0.80),
            "raw_output": model_output
        }
