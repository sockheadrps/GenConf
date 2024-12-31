import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .db.db_manager import DatabaseManager
import uvicorn
import os

# get the path to the 

generators = [
            "GEN-A3", "GEN-A2", "GEN-B3", "GEN-B2", "GEN-C3", "GEN-C2",
            "GEN-D3", "GEN-D2", "GEN-R3", "GEN-R2", "GEN-A1", "GEN-B1",
            "GEN-C1", "GEN-D1", "GEN-E2", "GEN-R1", "GEN-H3", "GEN-I3",
            "GEN-J3", "GEN-G3", "GEN-F3", "GEN-E3"
        ]


base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "quarto", "quarto_output")

app = FastAPI()
app.mount("/dashboard", StaticFiles(directory=static_dir), name="dashboard")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

db = DatabaseManager()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db.init_db()

@app.get("/generators")
async def get_generators():
    return JSONResponse(content={"generators": generators})

@app.get("/records/{month}")
async def get_records(month: str):
    return JSONResponse(content={"records": db.gen_records_month(month)})

@app.post("/record")
async def record_data(data: dict):
    print("Received data:", data)

    generator = data['generator']
    pre_run_data = data['preRunData']
    post_run_data = data['postRunData']
    db.save_check_data(generator, pre_run_data, post_run_data)
    return JSONResponse(content={"message": "Data received successfully"})


@app.get("/gen_data/{month}/{generator}")
async def get_gen_data(month: str, generator: str):
    data = db.get_gen_data(month, generator)
    return JSONResponse(content=data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
