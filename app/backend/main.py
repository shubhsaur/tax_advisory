from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import tempfile
from .create_table import create_table
from .db import get_connection
import PyPDF2
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import uuid
from datetime import datetime
import re
import requests

app = FastAPI(title="Tax Advisor Backend")

# Path to the frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

# Mount static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.on_event("startup")
def startup_event():
    create_table()

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

def call_gemini_for_extraction(text):
    prompt = (
        "You are an expert at extracting structured data from messy salary slip or Form 16 text. "
        "For each of the following fields, look for the number that appears after the field name (case-insensitive): "
        "gross_salary, basic_salary, hra_received, rent_paid, deduction_80c, deduction_80d, standard_deduction, professional_tax, tds. "
        "Map the following synonyms:\n"
        "- 'Basic', 'Basic Pay' → 'basic_salary'\n"
        "- 'HRA', 'House Rent Allowance' → 'hra_received'\n"
        "Return ONLY a valid JSON object with these keys. If a field is not found, use an empty string. "
        "Do not include any explanation or extra text. "
        "Example 1:\n"
        "Text:\n"
        "QuantumNest Ltd\nSalary Slip for 03/2025\n\nName: Priya Desai   Department: HR\nDesignation: Marketing Executive   Bank Name: SBI\nLocation: Pune   Account No: 11122234\n\nEarnings  Deductions\nSr No  Salary Head  Amount  Sr No  Salary Head  Amount\n1 Basic  32000  1 Professional Tax  200\n2 Dearness Allowance  4800  2 TDS 1500\n3 House Rent Allowance  16000  3 EPF 1840\n4 Conveyance Allowance  1200\n5 Medical Allowance  1250\n6 Special Allowance  2750\n\nGross Salary  58000  Total Deduction  5540\nReimbursement  1000\nNet Salary  53460\n"
        "Output:\n"
        "{\n"
        "  \"gross_salary\": \"58000\",\n"
        "  \"basic_salary\": \"32000\",\n"
        "  \"hra_received\": \"16000\",\n"
        "  \"rent_paid\": \"\",\n"
        "  \"deduction_80c\": \"\",\n"
        "  \"deduction_80d\": \"\",\n"
        "  \"standard_deduction\": \"\",\n"
        "  \"professional_tax\": \"200\",\n"
        "  \"tds\": \"1500\"\n"
        "}\n"
        "Now extract from this text:\n"
        + text
    )
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=20)
        response.raise_for_status()
        result = response.json()
        import json as pyjson
        import re as pyre
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        match = pyre.search(r'\{[\s\S]*\}', text_response)
        if match:
            return pyjson.loads(match.group(0))
        else:
            return {}
    except Exception as e:
        print('Gemini extraction error:', e)
        return {}

def extract_user_financials(text):
    fields = call_gemini_for_extraction(text)
    # Fallback: if all fields are empty, use regex extraction
    if not any(fields.values()):
        def extract(pattern, text):
            match = re.search(pattern, text, re.IGNORECASE)
            return match.group(1).replace(',', '').strip() if match else ''
        fields = {
            "gross_salary": extract(r"gross\s*salary\s*[:\-]?\s*([\d,\.]+)", text),
            "basic_salary": extract(r"basic\s*salary\s*[:\-]?\s*([\d,\.]+)", text),
            "hra_received": extract(r"hra\s*received\s*[:\-]?\s*([\d,\.]+)", text),
            "rent_paid": extract(r"rent\s*paid\s*[:\-]?\s*([\d,\.]+)", text),
            "deduction_80c": extract(r"80c\s*[:\-]?\s*([\d,\.]+)", text),
            "deduction_80d": extract(r"80d\s*[:\-]?\s*([\d,\.]+)", text),
            "standard_deduction": extract(r"standard\s*deduction\s*[:\-]?\s*([\d,\.]+)", text),
            "professional_tax": extract(r"professional\s*tax\s*[:\-]?\s*([\d,\.]+)", text),
            "tds": extract(r"tds\s*[:\-]?\s*([\d,\.]+)", text),
            "created_at": ""
        }
    return {
        "gross_salary": fields.get("gross_salary", ""),
        "basic_salary": fields.get("basic_salary", ""),
        "hra_received": fields.get("hra_received", ""),
        "rent_paid": fields.get("rent_paid", ""),
        "deduction_80c": fields.get("deduction_80c", ""),
        "deduction_80d": fields.get("deduction_80d", ""),
        "standard_deduction": fields.get("standard_deduction", ""),
        "professional_tax": fields.get("professional_tax", ""),
        "tds": fields.get("tds", ""),
        "created_at": ""
    }

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        # Try text extraction with PyPDF2
        extracted_text = ""
        try:
            with open(tmp_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""
        except Exception:
            extracted_text = ""
        # If no text, try OCR with pytesseract
        if not extracted_text.strip():
            try:
                images = convert_from_path(tmp_path)
                for img in images:
                    extracted_text += pytesseract.image_to_string(img)
            except Exception:
                pass
        os.remove(tmp_path)
        if not extracted_text.strip():
            return JSONResponse(status_code=422, content={"error": "Could not extract text from PDF."})
        # Map extracted text to UserFinancials fields (dummy for now)
        user_financials = extract_user_financials(extracted_text)
        return {"fields": user_financials, "raw_text": extracted_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/save-financials")
async def save_financials(request: Request):
    data = await request.json()
    # Generate a session_id and created_at
    session_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    def to_null(val):
        return val if val not in ("", None) else None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO UserFinancials (
                    session_id, gross_salary, basic_salary, hra_received, rent_paid, deduction_80c, deduction_80d, standard_deduction, professional_tax, tds, created_at
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                session_id,
                to_null(data.get('gross_salary')),
                to_null(data.get('basic_salary')),
                to_null(data.get('hra_received')),
                to_null(data.get('rent_paid')),
                to_null(data.get('deduction_80c')),
                to_null(data.get('deduction_80d')),
                to_null(data.get('standard_deduction')),
                to_null(data.get('professional_tax')),
                to_null(data.get('tds')),
                created_at
            ])
            conn.commit()
        conn.close()
        return {"success": True, "session_id": session_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/calculate-tax")
async def calculate_tax(request: Request):
    data = await request.json()
    # Convert all values to float or 0
    def to_num(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0
    gross_salary = to_num(data.get('gross_salary'))
    basic_salary = to_num(data.get('basic_salary'))
    hra_received = to_num(data.get('hra_received'))
    rent_paid = to_num(data.get('rent_paid'))
    deduction_80c = to_num(data.get('deduction_80c'))
    deduction_80d = to_num(data.get('deduction_80d'))
    standard_deduction = 50000.0
    professional_tax = to_num(data.get('professional_tax'))
    tds = to_num(data.get('tds'))

    # Old Regime Calculation (FY 2024-25)
    # Deductions: Standard Deduction, HRA, Professional Tax, 80C, 80D
    total_deductions_old = standard_deduction + professional_tax + deduction_80c + deduction_80d
    # HRA Exemption (simplified): min(HRA received, 50% of basic, rent_paid - 10% of basic)
    hra_exempt = min(
        hra_received,
        0.5 * basic_salary,
        max(0, rent_paid - 0.1 * basic_salary)
    )
    total_deductions_old += hra_exempt
    taxable_income_old = max(0, gross_salary - total_deductions_old)
    def old_regime_tax(taxable):
        tax = 0
        if taxable > 250000:
            if taxable <= 500000:
                tax += (taxable - 250000) * 0.05
            elif taxable <= 1000000:
                tax += 250000 * 0.05
                tax += (taxable - 500000) * 0.2
            else:
                tax += 250000 * 0.05
                tax += 500000 * 0.2
                tax += (taxable - 1000000) * 0.3
        return tax
    old_tax = old_regime_tax(taxable_income_old)
    old_tax += 0.04 * old_tax  # 4% cess
    # New Regime Calculation (FY 2024-25)
    # Only Standard Deduction
    taxable_income_new = max(0, gross_salary - standard_deduction)
    def new_regime_tax(taxable):
        tax = 0
        slabs = [
            (300000, 0.0),
            (600000, 0.05),
            (900000, 0.1),
            (1200000, 0.15),
            (1500000, 0.2),
            (float('inf'), 0.3)
        ]
        prev = 0
        for limit, rate in slabs:
            if taxable > limit:
                tax += (limit - prev) * rate
                prev = limit
            else:
                tax += (taxable - prev) * rate
                break
        return tax
    new_tax = new_regime_tax(taxable_income_new)
    new_tax += 0.04 * new_tax  # 4% cess
    return {
        "old": {
            "taxable_income": round(taxable_income_old, 2),
            "tax": round(old_tax, 2)
        },
        "new": {
            "taxable_income": round(taxable_income_new, 2),
            "tax": round(new_tax, 2)
        }
    } 