from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pathlib import Path

app = FastAPI()
static_dir = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=static_dir), name="app1-static")

@app.get("/")
async def index():
    return FileResponse(static_dir / "index.html")
