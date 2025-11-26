from backend.api.push_api import send_push_to_all

class LiveEngineAdapter(EngineBase):
    name = "LiveEngineAdapter"

    def run_pipeline(self, data):
        result = self.model.predict(data)

        if result["odds_spike"] and result["value"] > 1.05:
            send_push_to_all({
                "market": result["market"],
                "odds": result["odds"],
                "value": result["value"]
            })

        return result
