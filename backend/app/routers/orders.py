"""
Orders Router
=============
POST /api/orders/checkout        — validate cart, save order, send email notification
POST /api/orders/whatsapp-link   — generate pre-filled WhatsApp URL
GET  /api/orders/{order_id}      — retrieve order by ID
"""

import os
import logging
from datetime import datetime, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderItem
from app.schemas import CheckoutIn, CheckoutOut, WhatsAppIn, WhatsAppOut, PRICE_MAP
from app.utils.email_service import (
    build_order_email,
    send_email,
)

logger = logging.getLogger(__name__)
router = APIRouter()

STORE_EMAIL   = os.getenv("STORE_EMAIL",    "salamtea.business@gmail.com")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "923009002321")


# ── POST /api/orders/checkout ─────────────────────────────────────────────────

@router.post(
    "/checkout",
    response_model=CheckoutOut,
    status_code=status.HTTP_201_CREATED,
    summary="Place a new order and send email notification",
)
async def checkout(payload: CheckoutIn, request: Request, db: Session = Depends(get_db)):
    """
    1. Validate all cart items against the server-side price map.
    2. Calculate line totals and grand total.
    3. Persist Order + OrderItems to database.
    4. Fire order notification email to store.
    5. Return order confirmation.
    """

    # ── 1. Price validation & line-total calculation ──────────────────────────
    resolved_items = []
    grand_total = 0.0

    for item in payload.cart:
        variety_prices = PRICE_MAP.get(item.tea_variety)
        if not variety_prices:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown tea variety: '{item.tea_variety}'"
            )
        unit_price = variety_prices.get(item.pack_size)
        if unit_price is None:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid pack size '{item.pack_size}' for {item.tea_variety}"
            )
        line_total = unit_price * item.quantity
        grand_total += line_total
        resolved_items.append({
            "tea_variety": item.tea_variety,
            "pack_size":   item.pack_size,
            "quantity":    item.quantity,
            "unit_price":  unit_price,
            "line_total":  line_total,
        })

    # ── 2. Persist to database ────────────────────────────────────────────────
    order = Order(
        customer_name    = payload.customer_name.strip(),
        customer_phone   = payload.customer_phone.strip(),
        customer_email   = (payload.customer_email or "").strip() or None,
        delivery_address = payload.delivery_address.strip(),
        grand_total_rs   = grand_total,
        notes            = (payload.notes or "").strip() or None,
        created_at       = datetime.now(timezone.utc),
    )
    db.add(order)
    db.flush()  # populate order.id before adding items

    for itm in resolved_items:
        db.add(OrderItem(
            order_id    = order.id,
            tea_variety = itm["tea_variety"],
            pack_size   = itm["pack_size"],
            quantity    = itm["quantity"],
            unit_price  = itm["unit_price"],
            line_total  = itm["line_total"],
        ))

    db.commit()
    db.refresh(order)

    logger.info("Order %s created | Customer: %s | Total: Rs %.0f",
                order.id, order.customer_name, grand_total)

    # ── 3. Send email notification (non-blocking — failure does not 500) ──────
    html = build_order_email(
        order_id         = order.id,
        customer_name    = order.customer_name,
        customer_phone   = order.customer_phone,
        customer_email   = order.customer_email or "",
        delivery_address = order.delivery_address,
        items            = resolved_items,
        grand_total      = grand_total,
        created_at       = order.created_at,
        notes            = order.notes or "",
    )

    email_sent = send_email(
        to        = STORE_EMAIL,
        subject   = f"🛒 New Order {order.id} — Rs {grand_total:,.0f} — {order.customer_name}",
        html_body = html,
    )

    if not email_sent:
        logger.warning("Email notification failed for order %s (order still saved)", order.id)

    # ── 4. Return confirmation ────────────────────────────────────────────────
    return CheckoutOut(
        order_id    = order.id,
        status      = order.status,
        grand_total = grand_total,
        message     = (
            "Your order has been placed successfully! "
            "We will contact you shortly to confirm delivery."
        ),
        created_at  = order.created_at.strftime("%d %b %Y, %I:%M %p"),
    )


# ── POST /api/orders/whatsapp-link ────────────────────────────────────────────

@router.post(
    "/whatsapp-link",
    response_model=WhatsAppOut,
    summary="Generate a pre-filled WhatsApp order URL",
)
async def whatsapp_link(payload: WhatsAppIn):
    """
    Build a structured wa.me deep-link with the cart pre-filled.
    The frontend opens this URL to hand the customer off to WhatsApp.
    """

    # Resolve prices
    lines = []
    grand_total = 0.0

    for item in payload.cart:
        variety_prices = PRICE_MAP.get(item.tea_variety)
        if not variety_prices:
            raise HTTPException(status_code=422, detail=f"Unknown variety: {item.tea_variety}")
        unit_price = variety_prices.get(item.pack_size)
        if unit_price is None:
            raise HTTPException(status_code=422, detail=f"Invalid pack: {item.pack_size}")
        line_total = unit_price * item.quantity
        grand_total += line_total
        lines.append(
            f"  - {item.tea_variety} ({item.pack_size}) × {item.quantity}"
            f" = Rs {line_total:,.0f}"
        )

    items_block = "\n".join(lines)

    message = (
        "Hello Salamtea, I would like to place an order:\n\n"
        f"{items_block}\n\n"
        f"💰 Total Price: Rs {grand_total:,.0f}\n\n"
        f"👤 My Name: {payload.customer_name}\n"
        f"📍 Delivery Address: {payload.delivery_address}"
    )

    encoded   = quote(message, safe="")
    url       = f"https://wa.me/{WHATSAPP_PHONE}?text={encoded}"

    return WhatsAppOut(whatsapp_url=url, message_text=message)


# ── GET /api/orders/{order_id} ────────────────────────────────────────────────

@router.get(
    "/{order_id}",
    summary="Retrieve order details by ID",
)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return {
        "order_id":        order.id,
        "status":          order.status,
        "customer_name":   order.customer_name,
        "grand_total_rs":  order.grand_total_rs,
        "created_at":      order.created_at.isoformat(),
        "items": [
            {
                "tea_variety": i.tea_variety,
                "pack_size":   i.pack_size,
                "quantity":    i.quantity,
                "unit_price":  i.unit_price,
                "line_total":  i.line_total,
            }
            for i in order.items
        ],
    }
