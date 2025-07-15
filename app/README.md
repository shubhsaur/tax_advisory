# Tax Advisor App (Phase 1)

## Project Structure

- `backend/` — FastAPI backend, Supabase DB connection, table creation
- `frontend/` — Landing page (HTML/CSS/JS)

## Setup & Usage

### 1. Prerequisites
- Python 3.8+
- Your `.env` file with Supabase DB credentials in the project root (see below)

### 2. Backend Setup
```bash
cd app/backend
pip install -r requirements.txt
uvicorn main:app --reload
```
- On startup, the backend will ensure the `UserFinancials` table exists in Supabase.
- Health check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Frontend
- Open `app/frontend/index.html` directly in your browser.
- (Optional) Serve with a static server for local development.

### 4. Environment Variables
Your `.env` file (in the project root) should include:
```
SUPABASE_DB_URL=your-db-host.supabase.co
SUPABASE_DB_USER=your_db_user
SUPABASE_DB_PASSWORD=your_db_password
SUPABASE_DB_NAME=your_db_name
SUPABASE_DB_PORT=5432
```

---

**Phase 1 Deliverables:**
- Modern landing page
- Automatic creation of `UserFinancials` table in Supabase 