"""
Contact Router
==============
POST /api/contact/send  — receive enquiry, log to DB, email to store
"""

import os
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ContactLog
from app.schemas import ContactIn, ContactOut
from app.utils.email_service import build_contact_email, send_email

logger = logging.getLogger(__name__)
router = APIRouter()

STORE_EMAIL = os.getenv("STORE_EMAIL", "salamtea.business@gmail.com")


@router.post(
    "/send",
    response_model=ContactOut,
    status_code=status.HTTP_200_OK,
    summary="Submit a contact enquiry from the website form",
)
async def send_contact(
    payload: ContactIn,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    1. Validate and sanitise the enquiry.
    2. Persist to contact_logs table.
    3. Send formatted HTML email to the store.
    4. Return success/failure response.
    """

    now        = datetime.now(timezone.utc)
    ip_address = request.client.host if request.client else None

    # ── Persist ───────────────────────────────────────────────────────────────
    log = ContactLog(
        sender_name  = payload.name.strip(),
        sender_phone = payload.phone.strip(),
        sender_email = (payload.email or "").strip() or None,
        message      = payload.message.strip(),
        ip_address   = ip_address,
        created_at   = now,
    )
    db.add(log)
    db.commit()

    logger.info("Contact enquiry from %s (%s)", payload.name, payload.phone)

    # ── Send email ────────────────────────────────────────────────────────────
    html = build_contact_email(
        sender_name  = log.sender_name,
        sender_phone = log.sender_phone,
        sender_email = log.sender_email or "",
        message      = log.message,
        received_at  = now,
    )

    email_sent = send_email(
        to        = STORE_EMAIL,
        subject   = f"✉ Website Enquiry from {log.sender_name} — Salamtea",
        html_body = html,
    )

    if not email_sent:
        logger.warning(
            "Email delivery failed for contact from %s (message still saved)", payload.name
        )

    return ContactOut(
        success = True,
        message = (
            "Thank you for reaching out! "
            "We've received your message and will get back to you shortly."
        ),
    )
