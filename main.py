from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pathlib import Path
from elementary_school.elementary_school import app as elementary_school_app
from middle_school.middle_school import app as middle_school_app
from high_school.high_school import app as high_school_app
from app1.app1 import app as app1_app
from app2.app2 import app as app2_app

app = FastAPI(title="에듀빌 드림로직")

base_dir = Path(__file__).parent
static_dir = base_dir / "static"

app.mount("/static", StaticFiles(directory=static_dir), name="main-static")
app.mount("/elementary_school", elementary_school_app)
app.mount("/middle_school", middle_school_app)
app.mount("/high_school", high_school_app)
app.mount("/app1", app1_app)
app.mount("/app2", app2_app)

@app.get("/")
async def root():
    return FileResponse(static_dir / "index.html")
