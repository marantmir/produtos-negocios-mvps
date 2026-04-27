from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.routers import auth, processes, ai, diagnostics, reports

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

allowed_origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(processes.router)
app.include_router(ai.router)
app.include_router(diagnostics.router)
app.include_router(reports.router)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
