# ============================================================
# MAIN FASTAPI BACKEND APP – FULL SYSTEM VERSION
# API + WebSocket + Push + OddsFeed + Workers kompatibilis
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import router as api_router
from api.websocket_routes import ws_router

app = FastAPI(
    title="Tippmester Quantum Engine",
    description="Full backend engine with strategy, odds feed, live websocket, push, workers",
    version="2.0.0"
)

# ------------------------------------------------------------
# CORS – frontend engedélyezése
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # ha lesz domain: ["https://tippmester.hu"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# API végpontok
# ------------------------------------------------------------
app.include_router(api_router, prefix="/api")

# ------------------------------------------------------------
# Websocket útvonalak
# ------------------------------------------------------------
app.include_router(ws_router)

# ------------------------------------------------------------
# Root teszt
# ------------------------------------------------------------
@app.get("/")
def status():
    return {
        "status": "ok",
        "engine": "quantum",
        "version": "2.0.0",
        "message": "Backend online"
    }

# ------------------------------------------------------------
# Futtatás (uvicorn)
# ------------------------------------------------------------
# uvicorn main:app --host 0.0.0.0 --port 8000
