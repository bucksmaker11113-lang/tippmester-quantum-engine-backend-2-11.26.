# ============================================================
# CELERY MAIN APP – Full System Version
# ------------------------------------------------------------
# Feladata:
# - háttérfeladatok futtatása (odds fetch, live spike)
# - Redis broker + Redis backend
# - FastAPI-t tehermentesíti
# ============================================================

from celery import Celery

# ------------------------------------------------------------
# CELERY CONFIG
# ------------------------------------------------------------
celery_app = Celery(
    "tippmester_engine",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Alap beállítások
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Budapest",
    enable_utc=True,
)

# ------------------------------------------------------------
# AUTOMATIKUS FELADAT BETÖLTÉS
# ------------------------------------------------------------
# A workers mappából automatikusan tölti a taskokat
celery_app.autodiscover_tasks([
    "performance.workers"
])
