"""
Salamtea Email Service
======================
Sends formatted HTML email notifications via SMTP (Gmail App Password,
SendGrid SMTP relay, or Mailgun SMTP relay).

All credentials come from environment variables — never hard-coded.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from typing import List

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


# ── SMTP config from environment ──────────────────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER",     "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL    = os.getenv("FROM_EMAIL",    SMTP_USER)
STORE_EMAIL   = os.getenv("STORE_EMAIL",   "salamtea.business@gmail.com")
STORE_PHONE   = os.getenv("STORE_PHONE",   "+92-300-9002321")


# ── Brand colours ─────────────────────────────────────────────────────────────
GREEN  = "#3f5d16"
CREAM  = "#f6f1e8"
DARK   = "#25251f"
MUTED  = "#6d685f"


# ── Shared HTML shell ─────────────────────────────────────────────────────────
def _wrap(body_html: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#eee8dc;font-family:Georgia,'Times New Roman',serif;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#eee8dc;padding:32px 16px;">
    <tr><td align="center">

      <!-- Card -->
      <table width="600" cellpadding="0" cellspacing="0"
             style="max-width:600px;width:100%;background:{CREAM};border:1px solid #d9d1c3;border-radius:6px;overflow:hidden;">

        <!-- Header -->
        <tr>
          <td style="background:{GREEN};padding:28px 32px;text-align:center;">
            <p style="margin:0;font-family:Georgia,serif;font-size:26px;font-weight:700;color:#fff;letter-spacing:.5px;">
              Salamtea
            </p>
            <p style="margin:4px 0 0;font-size:11px;color:rgba(255,255,255,.75);letter-spacing:2px;font-family:Arial,sans-serif;">
              A MATTER OF GOOD TASTE · SINCE 1955
            </p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px 36px 28px;">
            {body_html}
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:{GREEN};padding:16px 32px;text-align:center;">
            <p style="margin:0;font-size:10px;color:rgba(255,255,255,.7);font-family:Arial,sans-serif;letter-spacing:1px;">
              Salamtea · Peshawar, Pakistan · {STORE_PHONE}
            </p>
            <p style="margin:4px 0 0;font-size:9px;color:rgba(255,255,255,.5);font-family:Arial,sans-serif;">
              {STORE_EMAIL}
            </p>
          </td>
        </tr>

      </table>

    </td></tr>
  </table>

</body>
</html>"""


# ── Order notification email ──────────────────────────────────────────────────
def build_order_email(
    order_id: str,
    customer_name: str,
    customer_phone: str,
    customer_email: str,
    delivery_address: str,
    items: List[dict],        # [{tea_variety, pack_size, quantity, unit_price, line_total}]
    grand_total: float,
    created_at: datetime,
    notes: str = "",
) -> str:
    """Return fully formatted order notification HTML."""

    ts = created_at.strftime("%d %b %Y, %I:%M %p (UTC)")

    # Build items table rows
    rows_html = ""
    for itm in items:
        rows_html += f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #e8e2d8;font-size:13px;color:{DARK};">
            {itm['tea_variety']}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #e8e2d8;font-size:13px;text-align:center;color:{DARK};">
            {itm['pack_size']}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #e8e2d8;font-size:13px;text-align:center;color:{DARK};">
            {itm['quantity']}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #e8e2d8;font-size:13px;text-align:right;color:{DARK};">
            Rs {itm['unit_price']:,.0f}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #e8e2d8;font-size:13px;text-align:right;font-weight:600;color:{GREEN};">
            Rs {itm['line_total']:,.0f}
          </td>
        </tr>"""

    notes_row = f"""
      <tr>
        <td colspan="2" style="padding-top:14px;">
          <p style="margin:0 0 4px;font-size:11px;color:{MUTED};font-family:Arial,sans-serif;letter-spacing:.5px;">NOTES</p>
          <p style="margin:0;font-size:13px;color:{DARK};">{notes}</p>
        </td>
      </tr>""" if notes else ""

    body = f"""
    <!-- Heading -->
    <h2 style="margin:0 0 6px;font-size:22px;color:{GREEN};">🛒 New Order Received</h2>
    <p style="margin:0 0 24px;font-size:12px;color:{MUTED};font-family:Arial,sans-serif;">
      Order ID: <strong style="color:{DARK};">{order_id}</strong> &nbsp;·&nbsp; {ts}
    </p>

    <!-- Customer details -->
    <table width="100%" cellpadding="0" cellspacing="0"
           style="background:#f0ece4;border:1px solid #ddd5c8;border-radius:4px;margin-bottom:22px;">
      <tr>
        <td style="padding:16px 18px;">
          <p style="margin:0 0 2px;font-size:11px;color:{MUTED};font-family:Arial,sans-serif;letter-spacing:.8px;">CUSTOMER DETAILS</p>
        </td>
      </tr>
      <tr>
        <td style="padding:0 18px 16px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td width="50%" style="padding:5px 0;font-size:13px;color:{MUTED};">Full Name</td>
              <td style="padding:5px 0;font-size:13px;font-weight:600;color:{DARK};">{customer_name}</td>
            </tr>
            <tr>
              <td style="padding:5px 0;font-size:13px;color:{MUTED};">Phone / WhatsApp</td>
              <td style="padding:5px 0;font-size:13px;font-weight:600;color:{DARK};">{customer_phone}</td>
            </tr>
            <tr>
              <td style="padding:5px 0;font-size:13px;color:{MUTED};">Email Address</td>
              <td style="padding:5px 0;font-size:13px;color:{DARK};">{customer_email or '—'}</td>
            </tr>
            <tr>
              <td style="padding:5px 0;font-size:13px;color:{MUTED};vertical-align:top;">Delivery Address</td>
              <td style="padding:5px 0;font-size:13px;color:{DARK};">{delivery_address}</td>
            </tr>
            {notes_row}
          </table>
        </td>
      </tr>
    </table>

    <!-- Order items table -->
    <p style="margin:0 0 10px;font-size:11px;color:{MUTED};font-family:Arial,sans-serif;letter-spacing:.8px;">ORDER ITEMS</p>
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border:1px solid #ddd5c8;border-radius:4px;border-collapse:collapse;margin-bottom:18px;">
      <thead>
        <tr style="background:#e8e2d8;">
          <th style="padding:10px 12px;text-align:left;font-size:11px;font-family:Arial,sans-serif;color:{MUTED};letter-spacing:.5px;font-weight:600;">
            TEA VARIETY
          </th>
          <th style="padding:10px 12px;text-align:center;font-size:11px;font-family:Arial,sans-serif;color:{MUTED};letter-spacing:.5px;font-weight:600;">
            SIZE
          </th>
          <th style="padding:10px 12px;text-align:center;font-size:11px;font-family:Arial,sans-serif;color:{MUTED};letter-spacing:.5px;font-weight:600;">
            QTY
          </th>
          <th style="padding:10px 12px;text-align:right;font-size:11px;font-family:Arial,sans-serif;color:{MUTED};letter-spacing:.5px;font-weight:600;">
            UNIT PRICE
          </th>
          <th style="padding:10px 12px;text-align:right;font-size:11px;font-family:Arial,sans-serif;color:{MUTED};letter-spacing:.5px;font-weight:600;">
            SUBTOTAL
          </th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>

    <!-- Grand total -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
      <tr>
        <td></td>
        <td width="200" style="background:{GREEN};padding:14px 18px;border-radius:4px;text-align:right;">
          <p style="margin:0;font-size:11px;color:rgba(255,255,255,.75);font-family:Arial,sans-serif;letter-spacing:1px;">
            GRAND TOTAL
          </p>
          <p style="margin:4px 0 0;font-size:22px;font-weight:700;color:#fff;">
            Rs {grand_total:,.0f}
          </p>
        </td>
      </tr>
    </table>

    <p style="margin:0;font-size:12px;color:{MUTED};font-family:Arial,sans-serif;line-height:1.6;">
      Please contact the customer to confirm the order and arrange delivery.<br>
      <strong style="color:{DARK};">Reply-to:</strong> {customer_email or customer_phone}
    </p>
    """

    return _wrap(body, f"New Order {order_id} — Salamtea")


# ── Contact enquiry email ─────────────────────────────────────────────────────
def build_contact_email(
    sender_name: str,
    sender_phone: str,
    sender_email: str,
    message: str,
    received_at: datetime,
) -> str:
    ts = received_at.strftime("%d %b %Y, %I:%M %p (UTC)")

    body = f"""
    <h2 style="margin:0 0 6px;font-size:22px;color:{GREEN};">✉ New Website Enquiry</h2>
    <p style="margin:0 0 24px;font-size:12px;color:{MUTED};font-family:Arial,sans-serif;">
      Received: {ts}
    </p>

    <table width="100%" cellpadding="0" cellspacing="0"
           style="background:#f0ece4;border:1px solid #ddd5c8;border-radius:4px;margin-bottom:22px;">
      <tr><td style="padding:16px 18px;">
        <p style="margin:0 0 2px;font-size:11px;color:{MUTED};font-family:Arial,sans-serif;letter-spacing:.8px;">SENDER DETAILS</p>
      </td></tr>
      <tr><td style="padding:0 18px 16px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="40%" style="padding:5px 0;font-size:13px;color:{MUTED};">Name</td>
            <td style="padding:5px 0;font-size:13px;font-weight:600;color:{DARK};">{sender_name}</td>
          </tr>
          <tr>
            <td style="padding:5px 0;font-size:13px;color:{MUTED};">Phone / WhatsApp</td>
            <td style="padding:5px 0;font-size:13px;font-weight:600;color:{DARK};">{sender_phone}</td>
          </tr>
          <tr>
            <td style="padding:5px 0;font-size:13px;color:{MUTED};">Email</td>
            <td style="padding:5px 0;font-size:13px;color:{DARK};">{sender_email or '—'}</td>
          </tr>
        </table>
      </td></tr>
    </table>

    <p style="margin:0 0 8px;font-size:11px;color:{MUTED};font-family:Arial,sans-serif;letter-spacing:.8px;">MESSAGE</p>
    <div style="background:#f0ece4;border-left:3px solid {GREEN};padding:14px 16px;border-radius:0 4px 4px 0;margin-bottom:24px;">
      <p style="margin:0;font-size:14px;color:{DARK};line-height:1.65;">{message.replace(chr(10), '<br>')}</p>
    </div>

    <p style="margin:0;font-size:12px;color:{MUTED};font-family:Arial,sans-serif;">
      You can reply directly to this email or contact via WhatsApp:&nbsp;
      <strong style="color:{DARK};">{sender_phone}</strong>
    </p>
    """

    return _wrap(body, f"Website Enquiry from {sender_name} — Salamtea")


# ── SMTP send function ────────────────────────────────────────────────────────
def send_email(to: str, subject: str, html_body: str) -> bool:
    """
    Send an HTML email via configured SMTP server.

    Returns True on success, False on failure (logs error).
    Never raises — callers should not crash if email fails.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning(
            "SMTP credentials not configured. Email NOT sent. "
            "Set SMTP_USER and SMTP_PASSWORD in your .env file."
        )
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Salamtea Store <{FROM_EMAIL}>"
        msg["To"]      = to
        msg["Reply-To"] = FROM_EMAIL

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to, msg.as_string())

        logger.info("Email sent to %s | Subject: %s", to, subject)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP authentication failed. Check SMTP_USER / SMTP_PASSWORD in .env "
            "(Gmail: use an App Password, not your regular password)."
        )
    except smtplib.SMTPException as exc:
        logger.error("SMTP error sending to %s: %s", to, exc)
    except Exception as exc:
        logger.error("Unexpected email error: %s", exc)

    return False
