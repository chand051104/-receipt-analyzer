import re, json
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text as extract_text_pdf
from dateutil.parser import parse as parse_date
from datetime import datetime
from database import get_top_vendors


def extract_text_from_file(file_path, filename):
    try:
        if filename.lower().endswith(".pdf"):
            images = convert_from_path(file_path, dpi=300)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)
            if not text.strip():
                text = extract_text_pdf(file_path)
            return text
        elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        elif filename.lower().endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return ""
    except Exception as e:
        print(f"❌ Error reading file {filename}: {e}")
        return ""


def extract_amount(text):
    text = text.replace(",", "").replace("INR", "₹").replace("Rs.", "₹")
    lines = text.splitlines()
    candidates = []

    for line in lines:
        matches = re.findall(r"(₹|\$|€|£)?\s?(\d{2,10}(?:\.\d{1,2})?)", line)
        if not matches:
            continue
        for symbol, number in matches:
            try:
                value = float(number)
            except:
                continue
            score = 0
            line_lower = line.lower()
            if "total amount" in line_lower:
                score += 5
            elif re.search(r"total|amount|paid|net|due|fare|bill|charge", line_lower):
                score += 3
            if re.search(r"rupees|only", line_lower):
                score += 1
            if symbol:
                score += 1
            if re.search(r"round off|balance|tax|receipt no", line_lower):
                score -= 3
            candidates.append((line.strip(), value, symbol.strip() if symbol else "", score))

    if not candidates:
        return ""
    best = max(candidates, key=lambda x: x[3])
    symbol, value = best[2], best[1]
    return f"{symbol}{value}" if symbol else str(value)


def extract_date(text):
    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
        r"\b\w{3,9}\s\d{1,2},\s\d{4}\b",
        r"\b\d{1,2}\s\w{3,9},?\s\d{4}\b",
        r"\b\d{1,2}-[A-Za-z]{3}-\d{4}\b",
    ]
    for line in text.splitlines():
        if "date" in line.lower() or "invoice" in line.lower() or "billed" in line.lower():
            for pat in patterns:
                match = re.search(pat, line)
                if match:
                    try:
                        dt = parse_date(match.group(), fuzzy=True)
                        if 2000 <= dt.year <= datetime.now().year + 1:
                            return str(dt.date())
                    except:
                        continue
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            try:
                dt = parse_date(match.group(), fuzzy=True)
                if 2000 <= dt.year <= datetime.now().year + 1:
                    return str(dt.date())
            except:
                continue
    return ""


def extract_vendor(text):
    lines = text.strip().splitlines()
    top_vendors = get_top_vendors()
    for vendor in top_vendors:
        if vendor.lower() in text.lower():
            return vendor
    potential = []
    for line in lines[:10]:
        clean = line.strip()
        if len(clean) < 3 or len(clean) > 60:
            continue
        if clean.lower().startswith(("tax", "gst", "invoice", "bill", "date", "receipt")):
            continue
        words = clean.split()
        if any(w[0].isupper() for w in words):
            potential.append(clean)
    return potential[0] if potential else "Unknown"


def classify_category(text):
    text = text.lower()
    try:
        with open("category_rules.json", "r") as f:
            rules = json.load(f)
        for category, keywords in rules.items():
            if any(k in text for k in keywords):
                return category
    except:
        pass
    return "Other"


def process_file(file, filename):
    print("🔍 Entered process_file()")
    raw_text = extract_text_from_file(file, filename)

    if not raw_text.strip():
        print("❌ No text found after OCR.")
        return None

    vendor = extract_vendor(raw_text)
    amount_str = extract_amount(raw_text)
    date = extract_date(raw_text)
    category = classify_category(raw_text)

    currency = ""
    amount_val = None
    match = re.match(r"([₹$€£])?(\d+(?:\.\d{1,2})?)", amount_str)
    if match:
        currency = match.group(1) or ""
        amount_val = float(match.group(2))

    print("📁 Filename:", filename)
    print("🧾 Amount:", amount_val)
    print("💱 Currency:", currency)
    print("📆 Date:", date)
    print("🏷️ Vendor:", vendor)
    print("📂 Category:", category)

    return {
        "filename": filename,
        "vendor": vendor,
        "date": date,
        "amount": amount_val,
        "currency": currency,
        "category": category,
    }
