"""
ORM Models — Salamtea Database Schema
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4()).replace("-", "").upper()[:12]


# ── Enums ─────────────────────────────────────────────────────────────────────

class TeaVariety(str, enum.Enum):
    black   = "Black Tea"
    green   = "Green Tea"
    ilaichi = "Ilaichi (Cardamom) Tea"


class PackSize(str, enum.Enum):
    g250 = "250g"
    g500 = "500g"
    kg1  = "1kg"
    kg2  = "2kg"


class OrderStatus(str, enum.Enum):
    pending    = "pending"
    confirmed  = "confirmed"
    processing = "processing"
    shipped    = "shipped"
    delivered  = "delivered"
    cancelled  = "cancelled"


# ── Product catalogue (reference table) ──────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id          = Column(String, primary_key=True, default=_uuid)
    tea_variety = Column(String, nullable=False)
    pack_size   = Column(String, nullable=False)
    pack_label  = Column(String, nullable=False)   # e.g. "Everyday Pack"
    price_rs    = Column(Float,  nullable=False)
    in_stock    = Column(Integer, default=1)        # 1=yes / 0=no
    created_at  = Column(DateTime, default=_now)

    order_items = relationship("OrderItem", back_populates="product")


# ── Order & Order Items ───────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id                = Column(String, primary_key=True, default=lambda: "ST" + _uuid())
    customer_name     = Column(String(120), nullable=False)
    customer_phone    = Column(String(30),  nullable=False)
    customer_email    = Column(String(120), nullable=True)
    delivery_address  = Column(Text,        nullable=False)
    grand_total_rs    = Column(Float,       nullable=False)
    status            = Column(String,      default=OrderStatus.pending.value)
    notes             = Column(Text,        nullable=True)
    created_at        = Column(DateTime,    default=_now)
    updated_at        = Column(DateTime,    default=_now, onupdate=_now)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id           = Column(String,  primary_key=True, default=_uuid)
    order_id     = Column(String,  ForeignKey("orders.id"), nullable=False)
    product_id   = Column(String,  ForeignKey("products.id"), nullable=True)
    tea_variety  = Column(String,  nullable=False)
    pack_size    = Column(String,  nullable=False)
    quantity     = Column(Integer, nullable=False, default=1)
    unit_price   = Column(Float,   nullable=False)
    line_total   = Column(Float,   nullable=False)

    order   = relationship("Order",   back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ── Contact Log ───────────────────────────────────────────────────────────────

class ContactLog(Base):
    __tablename__ = "contact_logs"

    id           = Column(String, primary_key=True, default=_uuid)
    sender_name  = Column(String(120), nullable=False)
    sender_phone = Column(String(30),  nullable=False)
    sender_email = Column(String(120), nullable=True)
    message      = Column(Text,        nullable=False)
    ip_address   = Column(String(45),  nullable=True)
    created_at   = Column(DateTime,    default=_now)
