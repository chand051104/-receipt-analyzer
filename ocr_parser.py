import pytesseract
import re
import io
from pdf2image import convert_from_bytes
from PIL import Image
from datetime import datetime
from pdfminer.high_level import extract_text as extract_pdf_text

SUPPORTED_CURRENCIES = r"[₹$€£]?"

def extract_text(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        try:
            text = extract_pdf_text(io.BytesIO(file_bytes))
            if text.strip():
                return text
        except:
            pass
        images = convert_from_bytes(file_bytes)
        return "\n".join(pytesseract.image_to_string(img) for img in images)
    elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
        img = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(img)
    elif filename.lower().endswith(".txt"):
        return file_bytes.decode("utf-8")
    else:
        raise ValueError("Unsupported file format")

def extract_vendor(text: str) -> str:
    lines = text.strip().splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    for line in lines[:6]:
        if any(c.isalpha() for c in line) and not re.search(r'(total|amount)', line, re.I):
            return line.strip()
    return "Unknown Vendor"

def extract_amount(text: str) -> float:
    patterns = [
        rf'(Total Amount|Grand Total|Amount Paid|Total)\s*[:\-]?\s*{SUPPORTED_CURRENCIES}?\s*([\d,]+\.?\d{{0,2}})',
        rf'{SUPPORTED_CURRENCIES}\s*([\d,]+\.\d{{2}})'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            if isinstance(matches[0], tuple):
                return float(matches[0][1].replace(',', ''))
            else:
                return float(matches[0].replace(',', ''))
    all_numbers = re.findall(r'[\₹$€£]?\s*([\d,]+\.\d{2})', text)
    if all_numbers:
        return max(float(n.replace(',', '')) for n in all_numbers)
    return 0.0

def extract_currency(text: str) -> str:
    symbol_match = re.search(r'[₹$€£]', text)
    return symbol_match.group(0) if symbol_match else "₹"

def extract_date(text: str) -> datetime:
    patterns = [
        r'\b(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})\b',
        r'\b(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})\b',
        r'\b(\d{1,2} \w{3,9} \d{2,4})\b'
    ]
    date_formats = [
        "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y",
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
        "%d %B %Y", "%d %b %Y"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
    return datetime.now()

def parse_receipt(text: str) -> dict:
    vendor = extract_vendor(text)
    amount = extract_amount(text)
    date = extract_date(text)
    currency = extract_currency(text)
    known_vendors = {
        "Amazon": "Shopping", "Flipkart": "Shopping", "Swiggy": "Food",
        "Zomato": "Food", "Reliance": "Grocery", "BESCOM": "Electricity",
        "ACT": "Internet", "Airtel": "Internet", "Vodafone": "Internet"
    }
    category = next((cat for v, cat in known_vendors.items() if v.lower() in vendor.lower()), "Other")
    return {
        "vendor": vendor,
        "amount": amount,
        "date": date,
        "category": category,
        "currency": currency
    }
