# VCF ↔ Excel Contact Converter

A premium, lightweight, and secure local web application to convert vCard (.vcf) files to Excel spreadsheets (.xlsx) and vice versa. It runs entirely on your local machine, ensuring complete privacy for your contact data.

## ✨ Features

- **vCard to Excel Conversion:**
  - Robust support for vCard versions 2.1, 3.0, and 4.0.
  - Seamlessly decodes folded lines and Quoted-Printable strings (often found in older Android exports).
  - Normalizes multiple phone numbers, emails, addresses, and custom tags.
  - **Live Contact Grid:** Edit, add, search, or delete contacts directly inside your browser before exporting.
  
- **Excel to vCard Conversion:**
  - Smart **Column Mapping Assistant** that automatically detects headers (e.g. "Work Phone", "Last Name").
  - Dropdown matching interface to manually correct mappings.
  - Supports combining split fields (e.g., First Name + Last Name) and splitting grouped numbers (e.g. multiple phone numbers in one cell).
  
- **Stunning UI:**
  - Sleek modern dark mode with glassmorphic cards and glowing visual states.
  - Animated drag-and-drop file uploaders.
  
- **Lightweight & Portable:**
  - Standard pure Python library implementation without heavy bioinformatics dependencies.
  - Zero files are written to disk during translation (processed in-memory using `BytesIO`).

---

## 🚀 How to Run

### Windows (Quick Start)
Simply double-click the **`run.bat`** file in the project folder. This will:
1. Detect Python.
2. Initialize a secure Python virtual environment (`.venv`).
3. Install dependencies (`Flask` and `openpyxl`).
4. Start the local server and automatically launch it in your default browser at `http://127.0.0.1:5000`.

### macOS / Linux (Terminal)
Open your terminal inside the project directory and run:
```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Start the server
python app.py
```
Then, open your web browser and navigate to `http://127.0.0.1:5000`.

---

## 🧪 Running Tests

A comprehensive unit test suite is included in `test_converter.py`. To run the tests:
```bash
# Ensure virtual environment is active
python -m unittest test_converter.py
```

---

## 📁 Directory Structure

```
vcf2excel/
├── converter/            # Core conversion algorithms
│   ├── __init__.py
│   ├── vcard_parser.py   # Advanced line unfolding and QP decoder
│   ├── vcard_writer.py   # vCard 3.0 builder with line folding
│   └── excel_handler.py  # styled Excel generator using openpyxl
├── static/               # Frontend assets
│   ├── css/
│   │   └── style.css     # Premium styling and design system
│   └── js/
│       └── main.js       # App state and dynamic interaction layer
├── templates/
│   └── index.html        # Main SPA UI structure
├── requirements.txt      # python dependencies
├── run.bat               # Windows launcher script
├── test_converter.py     # Automated tests suite
└── README.md             # Documentation
```
