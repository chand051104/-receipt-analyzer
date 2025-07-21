from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ReceiptData, SearchQuery
from ocr_parser import extract_text, parse_receipt
from database import init_db, insert_receipt, get_all_receipts
import io

app = FastAPI(title="Receipt Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.post("/upload/")
async def upload_receipt(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = extract_text(contents, file.filename)
        parsed = parse_receipt(text)
        parsed['filename'] = file.filename
        insert_receipt(parsed)
        return {"status": "success", "parsed": parsed}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/receipts/")
def list_receipts():
    rows = get_all_receipts()
    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "filename": row[1],
            "vendor": row[2],
            "date": row[3],
            "amount": row[4],
            "category": row[5],
            "currency": row[6]
        })
    return result
