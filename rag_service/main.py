from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as rag_router
from .ingest import build_and_upsert_index

app = FastAPI(title="School Climate RAG Service")

# Allow local React dev
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Optional: build index on startup in dev
    # In prod, you may want this as a separate scheduled job.
    # build_and_upsert_index()
    pass

app.include_router(rag_router, prefix="/api")
