# Salamtea API Reference

**Base URL (local dev):** `http://localhost:8000/api`  
**Interactive Docs:** `http://localhost:8000/api/docs` (Swagger UI)  
**ReDoc:** `http://localhost:8000/api/redoc`

---

## Authentication

No API key is required for the current version. CORS is configured to only accept requests from the allowed origins listed in `.env`.

---

## Orders

### POST `/api/orders/checkout`

Places a new order, saves it to the database, and fires an HTML email notification to the store.

**Request Body (JSON)**

```json
{
  "customer_name":    "Ahmed Khan",
  "customer_phone":   "03009876543",
  "customer_email":   "ahmed@example.com",
  "delivery_address": "House 12, Street 4, Hayatabad Phase 1, Peshawar",
  "notes":            "Please deliver after 6 PM.",
  "cart": [
    { "tea_variety": "Black Tea",              "pack_size": "500g", "quantity": 2 },
    { "tea_variety": "Ilaichi (Cardamom) Tea", "pack_size": "250g", "quantity": 1 }
  ]
}
```

| Field              | Type     | Required | Constraints                                              |
|--------------------|----------|----------|----------------------------------------------------------|
| `customer_name`    | string   | ✅        | 2–120 chars                                              |
| `customer_phone`   | string   | ✅        | 7–30 chars, digits + symbols                             |
| `customer_email`   | string   | ❌        | Valid email or null                                      |
| `delivery_address` | string   | ✅        | 10–500 chars                                             |
| `notes`            | string   | ❌        | Up to 500 chars                                          |
| `cart`             | array    | ✅        | At least 1 item                                          |
| `cart[].tea_variety` | string | ✅        | `"Black Tea"`, `"Green Tea"`, `"Ilaichi (Cardamom) Tea"` |
| `cart[].pack_size`  | string  | ✅        | `"250g"`, `"500g"`, `"1kg"`, `"2kg"`                    |
| `cart[].quantity`   | integer | ✅        | 1–100                                                    |

**Response `201 Created`**

```json
{
  "order_id":    "ST9A3F7B12C4",
  "status":      "pending",
  "grand_total": 2150.0,
  "message":     "Your order has been placed successfully! We will contact you shortly.",
  "created_at":  "27 Aug 2026, 10:45 AM"
}
```

**Errors**

| Status | Reason                                |
|--------|---------------------------------------|
| `422`  | Validation error (see `detail` field) |
| `500`  | Internal server error                 |

---

### POST `/api/orders/whatsapp-link`

Generates a pre-filled `wa.me` deep-link for WhatsApp ordering.

**Request Body (JSON)**

```json
{
  "customer_name":    "Ahmed Khan",
  "delivery_address": "House 12, Street 4, Hayatabad",
  "cart": [
    { "tea_variety": "Green Tea", "pack_size": "1kg", "quantity": 1 }
  ]
}
```

**Response `200 OK`**

```json
{
  "whatsapp_url":  "https://wa.me/923009002321?text=Hello%20Salamtea...",
  "message_text":  "Hello Salamtea, I would like to place an order:\n\n  - Green Tea (1kg) × 1 = Rs 1,800\n\n💰 Total Price: Rs 1,800\n\n👤 My Name: Ahmed Khan\n📍 Delivery Address: House 12, Street 4, Hayatabad"
}
```

---

### GET `/api/orders/{order_id}`

Retrieve a saved order by its ID.

**Response `200 OK`**

```json
{
  "order_id":       "ST9A3F7B12C4",
  "status":         "pending",
  "customer_name":  "Ahmed Khan",
  "grand_total_rs": 2150.0,
  "created_at":     "2026-08-27T10:45:00+00:00",
  "items": [
    { "tea_variety": "Black Tea", "pack_size": "500g", "quantity": 2, "unit_price": 850, "line_total": 1700 },
    { "tea_variety": "Ilaichi (Cardamom) Tea", "pack_size": "250g", "quantity": 1, "unit_price": 550, "line_total": 550 }
  ]
}
```

---

## Contact

### POST `/api/contact/send`

Submits a customer enquiry. Saves to the database and emails the store.

**Request Body (JSON)**

```json
{
  "name":    "Sara Ahmed",
  "phone":   "03001234567",
  "email":   "sara@example.com",
  "message": "Do you offer bulk discounts for corporate orders?"
}
```

| Field     | Type   | Required | Constraints  |
|-----------|--------|----------|--------------|
| `name`    | string | ✅        | 2–120 chars  |
| `phone`   | string | ✅        | 7–30 chars   |
| `email`   | string | ❌        | Valid email  |
| `message` | string | ✅        | 5–2000 chars |

**Response `200 OK`**

```json
{
  "success": true,
  "message": "Thank you for reaching out! We've received your message and will get back to you shortly."
}
```

---

## Health

### GET `/api/health`

```json
{ "status": "ok", "service": "Salamtea API v1.0.0" }
```

---

## Product Price Map

Server-side authoritative pricing (also validated on backend):

| Tea Variety              | 250g   | 500g   | 1kg    | 2kg    |
|--------------------------|--------|--------|--------|--------|
| Black Tea                | Rs 450 | Rs 850 | Rs 1,600 | Rs 3,100 |
| Green Tea                | Rs 500 | Rs 950 | Rs 1,800 | Rs 3,500 |
| Ilaichi (Cardamom) Tea   | Rs 550 | Rs 1,050 | Rs 2,000 | Rs 3,900 |

---

## Error Format

All errors follow a consistent structure:

```json
{ "detail": "Human-readable error message" }
```

Validation errors from Pydantic return `422 Unprocessable Entity` with a detailed `detail` array.
