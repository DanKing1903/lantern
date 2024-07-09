import json
import logging.config

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.compare import compare_pdf_to_database
from src.log_config import log_config
from src.pdf_service import PdfService

logging.config.dictConfig(log_config)
logger = logging.getLogger("app-logger")

db = pd.read_csv("data/database.csv")

app = FastAPI(debug=True)

pdf = PdfService(key="TEST_KEY")


class ComparisonRequest(BaseModel):
    file_path: str
    company_name: str


class ComparisonReport(BaseModel):
    databaseData: dict
    pdfExtractedData: dict
    comparison: dict


@app.post("/reports/", response_model=ComparisonReport)
def create_discrepancy_report(comparison: ComparisonRequest):
    try:
        pdf_data = pd.Series(pdf.extract(file_path=comparison.file_path))
    except FileNotFoundError:
        logger.error(
            "Item not found: "
            + json.dumps(
                {
                    "file_path": comparison.file_path,
                    "company_name": comparison.company_name,
                }
            )
        )
        raise HTTPException(status_code=404, detail="Item not found")
    if pdf_data["Company Name"] != comparison.company_name:
        logger.error(
            "Invalid company name: "
            + json.dumps(
                {
                    "file_path": comparison.file_path,
                    "company_name": comparison.company_name,
                }
            )
        )
        raise HTTPException(status_code=422, detail="Incorrect company name")
    try:
        report = compare_pdf_to_database(
            primary_key_value=comparison.company_name, db=db, pdf_data=pdf_data
        )
    except Exception:
        logger.exception(
            "Something went wrong: "
            + json.dumps(
                {
                    "file_path": comparison.file_path,
                    "company_name": comparison.company_name,
                }
            )
        )
        raise HTTPException(status_code=500, detail="Something went wrong")
    return report
