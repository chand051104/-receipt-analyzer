
# 🧾 Receipt Analyzer App

A full-stack Python + Streamlit application to **upload, parse, and analyze receipts** using OCR and rule-based extraction. It stores results in a SQLite database and provides interactive visualizations, editing, and export functionality.

---

## 🚀 Features

- 📤 Upload receipts (`.jpg`, `.png`, `.pdf`, `.txt`)
- 🔍 Extracts:
  - **Vendor**
  - **Date**
  - **Amount**
  - **Currency**
  - **Category** (auto-tagged)
- 🧠 OCR with Tesseract
- 📂 Rule-based classification from `category_rules.json`
- 📊 View and edit data in an interactive table
- 📈 Visualizations:
  - Category distribution (Bar chart)
  - Monthly spending (Line chart)
- ⬇️ Export as `.csv` or `.json`
- 💾 Stored locally using `SQLite` (`receipts.db`)
- ✅ Auto-sync edits to DB
- 🔁 Optional DB reset button

---

## 🧩 Folder Structure
receipt-analyzer/
├── app.py # Main Streamlit frontend
├── main.py # Optional CLI runner
├── database.py # SQLite DB interface
├── ocr_parser.py # OCR + extraction logic
├── utils.py # File handling, OCR processor
├── category_rules.json # Custom rules for classification
├── receipts.db # SQLite DB (auto-generated)
├── requirements.txt # Python dependencies
├── README.md # 📄 This file
└── .gitignore # Ignore DB, cache, venv



## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/receipt-analyzer.git
cd receipt-analyzer
2. Create virtual environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
3. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Install Tesseract OCR
macOS: brew install tesseract

Ubuntu: sudo apt install tesseract-ocr

Windows: Download Installer

5. Run the app
bash
Copy
Edit
streamlit run app.py
🧠 How It Works
Upload: Drag and drop receipts or PDFs.

OCR: Images and PDFs are processed using pytesseract + pdf2image.

Parsing: ocr_parser.py uses regex + keyword rules to extract:

Vendor

Date

Amount

Currency

Category: Uses category_rules.json to assign a spending category.

Storage: Parsed data is saved in receipts.db (SQLite).

Streamlit UI:

View and edit data

Save edits automatically to DB

Visual summaries

Export buttons (CSV, JSON)

📊 Visualizations
Type	Description
📂 Category Chart	Shows distribution of spending categories
💵 Line Chart	Monthly spending over time

✅ Design Choices
Streamlit used for a fast interactive dashboard.

SQLite for lightweight, file-based storage.

Tesseract OCR for offline image-to-text conversion.

Modular Code: Split into ocr_parser.py, database.py, and utils.py.

Extensible Rules: Easily update category_rules.json for new vendors/categories.

❗ Assumptions
Receipts contain recognizable patterns (e.g. Total, Amount, ₹).

Common date formats: dd-mm-yyyy, yyyy-mm-dd, dd/MM/yyyy

Files are within 200MB and of supported types.

⚠️ Limitations
OCR quality depends on image clarity.

Rule-based parsing may fail for non-standard receipts.

No user authentication (local only).

Multi-language OCR not yet supported.

📦 Dependencies
See requirements.txt. Key libraries:

streamlit

pytesseract

pdf2image

pdfminer.six

pandas

Pillow


