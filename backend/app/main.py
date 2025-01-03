import json
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.genfuel import FuelEstimator
from .db.db_manager import DatabaseManager
from .api.report import get_report_data, generate_zip_reports, generate_csv_reports, generate_excel_reports
import uvicorn
import os
from contextlib import asynccontextmanager
import pandas as pd
from pathlib import Path
import zipfile
import io


# get the path to the

generators = [
    "GEN-A3", "GEN-A2", "GEN-B3", "GEN-B2", "GEN-C3", "GEN-C2",
    "GEN-D3", "GEN-D2", "GEN-R3", "GEN-R2", "GEN-A1", "GEN-B1",
    "GEN-C1", "GEN-D1", "GEN-E2", "GEN-R1", "GEN-H3", "GEN-I3",
    "GEN-J3", "GEN-G3", "GEN-F3", "GEN-E3"
]


base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "quarto", "quarto_output")

report_dir = Path(os.path.join(base_dir, "data", "reports"))
app = FastAPI()
# app.mount("/dashboard", StaticFiles(directory=static_dir), name="dashboard")
# app.mount("/zip_reports", StaticFiles(directory=str(report_dir)), name="reports")
# app.mount("/reports", StaticFiles(directory=report_dir), name="reports")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Database instance
db = DatabaseManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and clean up resources."""
    db.init_db()
    yield


@app.get("/reports/{month}/{report_type}")
async def get_reports(month: str, report_type: str):
    report = get_report_data(month, report_type)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report not found for month {
                            month} and report type {report_type}")
    return JSONResponse(content={"report": report})


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


@app.get("/generate_reports/{month}/{option}")
async def generate_reports_endpoint(month: str, option: str):
    if option == "zip":
        generate_zip_reports(month)
    if option == "csv":
        generate_csv_reports(month)
    if option == "xlsx":
        generate_excel_reports(month)
        return FileResponse(report_dir / month / f"{month.lower()}_reports.xlsx")

    # Get path to generated zip file
    zip_path = report_dir / month / f"{month.lower()}_reports.zip"

    # Create in-memory buffer and copy zip contents
    zip_buffer = io.BytesIO()
    with open(zip_path, 'rb') as f:
        zip_buffer.write(f.read())

    # Reset buffer position
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{month}_reports.zip"'}
    )


@app.get("/gen_data/{month}/{generator}")
async def get_gen_data(month: str, generator: str):
    try:
        data = db.get_gen_data(month, generator)
        if data is None:
            raise HTTPException(status_code=404, detail=f"Data not found for month {
                                month} and generator {generator}")
        return JSONResponse(content=data)
    except:
        raise HTTPException(status_code=404, detail=f"Data not found for month {
                            month} and generator {generator}")

@app.get("/gen_fuel_estimate/{month}")
async def get_gen_fuel_estimate(month: str):
    data = FuelEstimator(month).to_json()
    
    return JSONResponse(content=data)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8100)
