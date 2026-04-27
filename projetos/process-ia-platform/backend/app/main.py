import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth, processes, diagnostics, ai, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Process IA Platform")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(processes.router)
app.include_router(diagnostics.router)
app.include_router(ai.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"message": "Process IA Platform API online"}
