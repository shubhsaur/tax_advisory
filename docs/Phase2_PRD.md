# Phase 2 PRD: PDF Upload, Extraction, and Manual Data Review

## Overview
Phase 2 enables users to upload their Indian salary slip or Form 16 (PDF), automatically extract relevant financial data using a combination of PyPDF2, pytesseract (for OCR), and Gemini LLM, and review/edit the extracted data in a modern, stepper-style form. All fields from the UserFinancials schema are editable. The backend handles PDF parsing and returns structured data to the frontend, which is then posted back to the backend after user review. Uploaded PDFs are stored temporarily and deleted after processing.

## Deliverables
- **PDF Upload:**
  - User can upload a PDF (salary slip or Form 16; text-based or scanned).
  - Frontend provides a modern, intuitive upload interface as the first step in a stepper UI.
- **Data Extraction:**
  - Backend processes the PDF using PyPDF2, pytesseract, and Gemini LLM to extract financial data.
  - Supports both text-based and scanned PDFs.
  - If extraction fails, show an error and allow the user to retry.
- **Manual Data Review:**
  - After extraction, the user is shown a stepper form pre-filled with the extracted data.
  - All fields from the UserFinancials schema are editable.
  - No validation required at this stage.
  - User can review and edit all fields before submitting.
  - Stepper UI includes smooth animations between steps.
- **Data Submission:**
  - On completion, the reviewed/edited data is POSTed to the backend for saving.
- **Temporary File Storage:**
  - Uploaded PDFs are stored on an ephemeral disk and deleted after processing.

## Acceptance Criteria
- User can upload a PDF (salary slip or Form 16).
- Extracted data is shown in a stepper form for review and editing.
- User can edit all fields and submit the data.
- Data is sent to the backend and saved.
- Uploaded PDFs are deleted after processing.

## UI/UX Requirements
- Use a modern, intuitive stepper interface with smooth animations.
- Maintain branding and style consistency with Phase 1 (Aptos Display font, blue highlights, light theme).

## References
- See [PRD.md](./PRD.md) and [Phase1_Requirements.md](./Phase1_Requirements.md) for context and schema. 