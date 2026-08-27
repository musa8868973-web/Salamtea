# Salamtea — Setup & Deployment Guide

## Prerequisites

| Tool      | Minimum Version | Install                            |
|-----------|-----------------|------------------------------------|
| Python    | 3.11+           | https://www.python.org/downloads/  |
| pip       | 23+             | bundled with Python                |
| Git       | Any             | https://git-scm.com/               |
| VS Code Live Server (optional) | — | VS Code extension |

> **PostgreSQL** is optional. The default setup uses SQLite (zero-config).

---

## 1. Project Structure

```
salamtea/
├── backend/
│   ├── app/
│   │   ├── main.py            ← FastAPI app factory, CORS, routers
│   │   ├── database.py        ← SQLAlchemy engine + session
│   │   ├── models.py          ← ORM models (Order, OrderItem, ContactLog)
│   │   ├── schemas.py         ← Pydantic v2 request/response schemas
│   │   ├── routers/
│   │   │   ├── orders.py      ← /api/orders/* endpoints
│   │   │   └── contact.py     ← /api/contact/send endpoint
│   │   └── utils/
│   │       └── email_service.py ← SMTP email builder & sender
│   ├── run.py                 ← Uvicorn launcher
│   ├── requirements.txt
│   └── .env.example           ← Copy to .env and fill in credentials
│
├── frontend/
│   ├── index.html
│   ├── our-tea.html           ← Cart, pack selector, checkout integration
│   ├── contact-us.html        ← Async API contact form
│   ├── about.html
│   ├── quality.html
│   └── assets/
│       ├── salamtea.js        ← Shared cart, drawer, checkout, WhatsApp JS
│       └── (images…)
│
├── docs/
│   ├── API_REFERENCE.md
│   └── SETUP.md               ← You are here
│
└── README.md
```

---

## 2. Backend Setup

### 2a. Create a virtual environment

```bash
cd salamtea/backend

# Create venv
python -m venv venv

# Activate — macOS/Linux
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate
```

### 2b. Install dependencies

```bash
pip install -r requirements.txt
```

### 2c. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values. **The minimum required** to send emails:

```env
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

> **Gmail App Password setup (5 minutes):**
> 1. Go to your Google Account → Security
> 2. Enable **2-Step Verification** (required)
> 3. Go back to Security → **App Passwords**
> 4. Select app: **Mail**, device: **Other** → type "Salamtea"
> 5. Google generates a 16-character password → paste it as `SMTP_PASSWORD`

The backend works **without** email configured — orders are still saved to the database; you just won't receive email alerts.

### 2d. Start the backend

```bash
python run.py
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process …
```

API docs available at: **http://localhost:8000/api/docs**

---

## 3. Frontend Setup

The frontend is plain HTML/CSS/JS — no build step required.

### Option A: VS Code Live Server (Recommended)

1. Install the **Live Server** extension in VS Code
2. Open the `frontend/` folder in VS Code
3. Right-click `index.html` → **Open with Live Server**
4. It opens on `http://127.0.0.1:5500`

### Option B: Python HTTP server

```bash
cd salamtea/frontend
python -m http.server 5500
# Open http://localhost:5500
```

### Option C: Direct file access

Open `frontend/index.html` directly in your browser.  
Add `null` to `ALLOWED_ORIGINS` in `.env` (already set in the example).

---

## 4. Running Both Servers Together

Open **two terminal windows**:

**Terminal 1 — Backend:**
```bash
cd salamtea/backend
source venv/bin/activate   # or venv\Scripts\activate on Windows
python run.py
```

**Terminal 2 — Frontend:**
```bash
cd salamtea/frontend
python -m http.server 5500
```

---

## 5. Switching from SQLite to PostgreSQL

1. Install PostgreSQL and create a database:
   ```sql
   CREATE USER salamtea_user WITH PASSWORD 'your_password';
   CREATE DATABASE salamtea_db OWNER salamtea_user;
   ```

2. Install the driver:
   ```bash
   pip install psycopg2-binary
   ```

3. Update `.env`:
   ```env
   DATABASE_URL=postgresql://salamtea_user:your_password@localhost:5432/salamtea_db
   ```

4. Restart the backend — SQLAlchemy creates the tables automatically.

---

## 6. Production Deployment

### 6a. Backend on a VPS / cloud server

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn (4 workers)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

Set `APP_RELOAD=false` in `.env` for production.

### 6b. Nginx reverse proxy (recommended)

```nginx
server {
    listen 80;
    server_name api.salamtea.pk;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6c. Frontend on shared hosting / Netlify / Vercel

1. Update `API_BASE` in `frontend/assets/salamtea.js`:
   ```js
   API_BASE: 'https://api.salamtea.pk/api',
   ```
2. Update `ALLOWED_ORIGINS` in backend `.env`:
   ```env
   ALLOWED_ORIGINS=https://salamtea.pk,https://www.salamtea.pk
   ```
3. Upload the `frontend/` folder to your host.

---

## 7. Testing the APIs

### Test the health endpoint:
```bash
curl http://localhost:8000/api/health
```

### Test contact form:
```bash
curl -X POST http://localhost:8000/api/contact/send \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"03001234567","message":"Hello from curl!"}'
```

### Test checkout:
```bash
curl -X POST http://localhost:8000/api/orders/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Customer",
    "customer_phone": "03001234567",
    "delivery_address": "House 1, Test Street, Peshawar",
    "cart": [{"tea_variety":"Black Tea","pack_size":"500g","quantity":2}]
  }'
```

### Test WhatsApp link:
```bash
curl -X POST http://localhost:8000/api/orders/whatsapp-link \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Customer",
    "delivery_address": "Peshawar",
    "cart": [{"tea_variety":"Green Tea","pack_size":"1kg","quantity":1}]
  }'
```

Or visit the Swagger UI at **http://localhost:8000/api/docs** to test interactively.

---

## 8. Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install -r requirements.txt` inside the activated venv |
| CORS error in browser | Add the frontend origin to `ALLOWED_ORIGINS` in `.env` and restart |
| Email not received | Check `SMTP_USER`/`SMTP_PASSWORD` in `.env`; confirm App Password (not regular Gmail password) |
| `Address already in use` on port 8000 | Run `lsof -i:8000` and kill the process, or change `APP_PORT` in `.env` |
| SQLite `database is locked` | Don't run multiple uvicorn workers with SQLite; switch to PostgreSQL for multi-worker prod |
| Cart not persisting across pages | Ensure `salamtea.js` is loaded on every page and you're not in Incognito mode |
