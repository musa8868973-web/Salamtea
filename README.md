# Salamtea — D2C Tea Store

> *A Matter of Good Taste · Since 1955*

Production-ready D2C e-commerce stack for **Salamtea**, a premium Pakistani tea brand.  
Built as a lightweight, deployment-friendly full-stack application — no frontend framework required.

---

## Tech Stack

| Layer      | Technology                                                 |
|------------|------------------------------------------------------------|
| Backend    | **FastAPI** (Python 3.11+) · Async · Uvicorn               |
| Database   | **SQLite** (dev) / **PostgreSQL** (prod) via SQLAlchemy ORM|
| Validation | **Pydantic v2**                                            |
| Email      | **SMTP** (Gmail App Password / Mailgun / SendGrid)         |
| Frontend   | Vanilla **HTML5 / CSS3 / JavaScript** (no build step)      |
| Cart       | `localStorage` (zero-dependency, works offline)            |

---

## Features

### 🛒 Full Cart System
- Pack-size selector (250g / 500g / 1kg / 2kg) with real pricing
- Slide-out cart drawer accessible from every page
- Quantity controls (+ / −) and item removal
- Grand total updated in real-time

### 📦 Checkout Flow
- Multi-field checkout modal with validation
- Server-side price verification (tamper-proof)
- Order saved to database with unique Order ID
- **Automated HTML email** sent to `salamtea.business@gmail.com`

### 💬 WhatsApp Ordering
- "Order via WhatsApp" on every product card and in the cart
- Structured, pre-filled WhatsApp message via `wa.me` deep-link
- Routed directly to `+92-300-9002321`

### ✉️ Contact Form
- Async AJAX submission (no page reload)
- Logged to database + HTML email to store
- Inline success/error feedback

---

## Quick Start

```bash
# 1. Clone / extract the project
cd salamtea/backend

# 2. Create and activate virtual environment
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# → Edit .env with your SMTP credentials

# 5. Start backend (auto-creates database)
python run.py
# ✅ http://localhost:8000/api/docs

# 6. Serve frontend (new terminal)
cd ../frontend
python -m http.server 5500
# ✅ http://localhost:5500
```

For detailed instructions, see **[docs/SETUP.md](docs/SETUP.md)**.

---

## API Endpoints

| Method | Endpoint                      | Description                          |
|--------|-------------------------------|--------------------------------------|
| `POST` | `/api/orders/checkout`        | Place order + send email notification |
| `POST` | `/api/orders/whatsapp-link`   | Generate pre-filled WhatsApp URL     |
| `GET`  | `/api/orders/{order_id}`      | Retrieve order by ID                 |
| `POST` | `/api/contact/send`           | Submit contact enquiry               |
| `GET`  | `/api/health`                 | Health check                         |

Full reference: **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)**

---

## Product Pricing

| Tea Variety            | 250g   | 500g   | 1kg    | 2kg    |
|------------------------|--------|--------|--------|--------|
| Black Tea              | Rs 450 | Rs 850 | Rs 1,600 | Rs 3,100 |
| Green Tea              | Rs 500 | Rs 950 | Rs 1,800 | Rs 3,500 |
| Ilaichi (Cardamom) Tea | Rs 550 | Rs 1,050 | Rs 2,000 | Rs 3,900 |

Prices are validated **server-side** — the frontend cannot override them.

---

## Project Structure

```
salamtea/
├── backend/
│   ├── app/
│   │   ├── main.py            ← FastAPI app, CORS middleware
│   │   ├── database.py        ← SQLAlchemy engine + session factory
│   │   ├── models.py          ← ORM: Order, OrderItem, ContactLog, Product
│   │   ├── schemas.py         ← Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── orders.py      ← Checkout + WhatsApp link APIs
│   │   │   └── contact.py     ← Contact form API
│   │   └── utils/
│   │       └── email_service.py ← Branded HTML email builder + SMTP sender
│   ├── run.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── index.html             ← Home page
│   ├── our-tea.html           ← Product catalogue + cart integration
│   ├── contact-us.html        ← Contact form (async API)
│   ├── about.html
│   ├── quality.html
│   └── assets/
│       └── salamtea.js        ← Cart state, drawer UI, checkout modal, WhatsApp
│
├── docs/
│   ├── API_REFERENCE.md
│   └── SETUP.md
│
└── README.md
```

---

## Email Notifications

Orders and contact enquiries trigger **branded HTML emails** to `salamtea.business@gmail.com`.

**Order email includes:**
- Unique Order ID and timestamp
- Customer name, phone, email, delivery address
- Itemised order breakdown (variety · size · qty · price · subtotal)
- Grand total highlighted in brand green

Configure via Gmail App Password (see [docs/SETUP.md](docs/SETUP.md#gmail-app-password)).

---

## Security Notes

- Prices are **re-computed server-side** from the master price map — frontend values are ignored.
- CORS is scoped to explicitly listed origins (`ALLOWED_ORIGINS` in `.env`).
- SMTP credentials never leave the backend `.env` file.
- Input is validated and length-limited at the Pydantic layer before DB writes.
- SQLite WAL mode is enabled automatically by SQLAlchemy for concurrent reads.

---

## Contact

**Salamtea** · Peshawar, Pakistan  
📞 0300 9002321  
✉️ salamtea.business@gmail.com

---

*© 2026 Salamtea. All rights reserved.*
