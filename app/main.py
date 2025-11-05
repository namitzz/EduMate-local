"""
FastAPI wrapper for EduMate single-container web host.

This module provides a unified API that:
1. Mounts static UI files from ui/build (if present)
2. Provides health and model info endpoints
3. Imports and uses existing backend modules (backend/main.py)
4. Falls back to stub implementations if backend is not available
"""
import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

# Add backend to Python path for imports
BACKEND_PATH = Path(__file__).parent.parent / "backend"
if BACKEND_PATH.exists():
    sys.path.insert(0, str(BACKEND_PATH))

# Try to import existing backend application
backend_app = None
try:
    # Try to import the existing FastAPI app from backend
    from main import app as backend_app
    print("[INFO] Successfully imported existing backend app from backend/main.py")
except ImportError as e:
    print(f"[WARNING] Could not import backend app: {e}")
    print("[INFO] Using stub implementation for API endpoints")

# Initialize FastAPI app
app = FastAPI(
    title="EduMate Web Host",
    description="Single-container web host serving API + UI + model",
    version="1.0.0"
)

# Mount existing backend app if available
if backend_app:
    # Mount the existing backend app under /api prefix
    app.mount("/api", backend_app)
    print("[INFO] Mounted existing backend app at /api")

    # --- Redirects for legacy/root API paths to mounted backend (/api) ---
    # These preserve method and body where appropriate by using 307 status codes.
    @app.get("/model-info", include_in_schema=False)
    async def model_info_redirect_get(request: Request):
        """
        Redirect GET /model-info -> /api/model-info.
        """
        return RedirectResponse(url="/api/model-info", status_code=307)

    @app.post("/chat", include_in_schema=False)
    async def chat_redirect_post(request: Request):
        """
        Redirect POST /chat -> /api/chat (307 to preserve POST body).
        Clients that post to /chat will be forwarded to the mounted backend.
        """
        return RedirectResponse(url="/api/chat", status_code=307)

    @app.post("/predict", include_in_schema=False)
    async def predict_redirect_post(request: Request):
        """
        Redirect POST /predict -> /api/predict.
        """
        return RedirectResponse(url="/api/predict", status_code=307)

else:
    # Provide stub API endpoints if backend is not available
    print("[INFO] Backend app not found, providing stub endpoints")
    
    # Stub health endpoint
    @app.get("/api/health")
    def health():
        """Health check endpoint."""
        return {"status": "ok", "service": "edumate-stub"}
    
    # Stub model info endpoint
    @app.get("/api/model-info")
    def model_info():
        """Get model information."""
        model_path = os.getenv("MODEL_PATH", "/app/models")
        return {
            "model_path": model_path,
            "model_loaded": False,
            "message": "Stub implementation - integrate with your model loading logic"
        }
    
    # Stub predict endpoint
    class PredictRequest(BaseModel):
        """Request model for predictions."""
        text: str
        max_length: Optional[int] = 100
    
    @app.post("/api/predict")
    def predict(request: PredictRequest):
        """Stub prediction endpoint."""
        return {
            "prediction": "This is a stub response. Implement your model inference here.",
            "input": request.text,
            "model": "stub"
        }

# Lazy model loader (if backend doesn't provide one)
class ModelLoader:
    """Lazy model loader that reads MODEL_PATH environment variable."""
    
    def __init__(self):
        self.model = None
        self.model_path = os.getenv("MODEL_PATH", "/app/models")
        print(f"[INFO] ModelLoader initialized with path: {self.model_path}")
    
    def load_model(self):
        """Load model lazily on first use."""
        if self.model is None:
            print(f"[INFO] Loading model from {self.model_path}")
            # TODO: Implement actual model loading logic here
            # Example:
            # from transformers import AutoModelForCausalLM, AutoTokenizer
            # self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
            # self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            
            # For now, return a stub
            self.model = {"status": "stub", "path": self.model_path}
            print("[INFO] Model loaded (stub)")
        return self.model

# Global model loader instance
model_loader = ModelLoader()

# Mount static files from ui/build if directory exists
UI_BUILD_PATH = Path(__file__).parent.parent / "ui" / "build"
if UI_BUILD_PATH.exists() and UI_BUILD_PATH.is_dir():
    # Mount static assets
    static_path = UI_BUILD_PATH / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        print(f"[INFO] Mounted static files from {static_path}")
    
    # Serve index.html at root and catch-all routes for SPA
    index_file = UI_BUILD_PATH / "index.html"
    if index_file.exists():
        @app.get("/", response_class=HTMLResponse)
        async def serve_root():
            """Serve the UI root page.""" 
            return index_file.read_text()
        
        @app.get("/{full_path:path}", response_class=HTMLResponse)
        async def serve_spa(full_path: str):
            """Catch-all route for SPA - serves index.html for client-side routing.""" 
            # Don't intercept API routes
            if full_path.startswith("api/"):
                return JSONResponse({"error": "Not found"}, status_code=404)
            return index_file.read_text()
        
        print(f"[INFO] Configured SPA routing with index.html from {UI_BUILD_PATH}")
else:
    print(f"[WARNING] UI build directory not found at {UI_BUILD_PATH}")
    print("[INFO] To add UI: build your frontend and place in ui/build/")
    
    # Provide a simple landing page
    @app.get("/", response_class=HTMLResponse)
    async def landing():
        """Simple landing page when UI is not available."""
        return """
        <html>
            <head><title>EduMate Web Host</title></head>
            <body>
                <h1>EduMate Web Host</h1>
                <p>Backend API is running. UI not yet built.</p>
                <ul>
                    <li><a href="/api/health">Health Check</a></li>
                    <li><a href="/api/model-info">Model Info</a></li>
                    <li><a href="/docs">API Documentation</a></li>
                </ul>
                <p>To add UI: build your frontend and place in <code>ui/build/</code></p>
            </body>
        </html>
        """

# Root-level health check (in addition to /api/health)
@app.get("/health")
def root_health():
    """Root-level health check."""
    return {"status": "ok", "service": "edumate-webhost"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Print startup information."""
    print("=" * 60)
    print("EduMate Web Host Started")
    print("=" * 60)
    print(f"MODEL_PATH: {os.getenv('MODEL_PATH', '/app/models')}")
    print(f"Backend mounted: {backend_app is not None}")
    print(f"UI available: {UI_BUILD_PATH.exists()}")
    print("=" * 60)
