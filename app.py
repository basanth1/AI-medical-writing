"""
Clinical Trial Document Generation System
FastAPI Application — works with Vite React frontend on port 5173
"""
# ── Suppress third-party version-mismatch warnings before any imports ─────────
import warnings
warnings.filterwarnings("ignore", message=".*urllib3.*doesn't match a supported version.*")
warnings.filterwarnings("ignore", message=".*chardet.*doesn't match a supported version.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.*")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
import logging, uvicorn, os

from backend.core.config import get_settings
from backend.api.routes import router
from backend.api.admin_routes            import admin_router  # ← NEW
from backend.api.auth                    import auth_router, AuthMiddleware
from backend.api.admin_overrides_loader  import apply_overrides

apply_overrides()


logging.basicConfig(
    level=getattr(logging, get_settings().log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

cfg = get_settings()

app = FastAPI(
    title="Clinical Trial Document Generation API",
    description=(
        "RAG-powered generation of regulatory-grade clinical trial documents "
        "(CSP, ICF, CSR, SAP) using Groq LLM + FAISS vector store. "
        "Compliance validation against ICH E6/E3, FDA, and EMA guidelines."
    ),
    version=cfg.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)
app.include_router(auth_router) 
app.include_router(router, prefix="/api/v1")
app.include_router(admin_router)

@app.get("/admin", include_in_schema=False)
def admin_root():
    return RedirectResponse(url="/admin/ui")

# ── Serve built frontend in production ─────────────────────────────────────────
DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")
PUBLIC = os.path.join(os.path.dirname(__file__), "frontend", "public")
if os.path.isdir(PUBLIC):
    app.mount("/brand-assets", StaticFiles(directory=PUBLIC), name="brand-assets")

if os.path.isdir(DIST):
    assets = os.path.join(DIST, "assets")
    if os.path.isdir(assets):
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        if full_path.startswith(("admin", "api", "auth", "login", "docs", "redoc")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        idx = os.path.join(DIST, "index.html")
        return FileResponse(idx) if os.path.isfile(idx) else {
            "error": "Frontend not built. Run: cd frontend && npm run build"
        }
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "message": "Clinical Trial DocGen API",
            "docs":    "/docs",
            "health":  "/api/v1/health",
            "frontend": "Run `npm run dev` in the frontend/ directory (port 5173)",
        }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=cfg.api_host,
        port=cfg.api_port,
        reload=cfg.api_reload,
    )
