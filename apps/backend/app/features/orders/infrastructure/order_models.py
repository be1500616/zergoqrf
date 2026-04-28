"""Order database models.

This module contains SQLAlchemy models for order management,
mapping domain entities to database tables.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..domain.order_enums import OrderStatus, PaymentStatus, PaymentMethod

Base = declarative_base()


class OrderModel(Base):
    """SQLAlchemy model for orders table."""
    
    __tablename__ = "orders"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    
    # Order identification
    order_number = Column(String(20), unique=True, nullable=False, index=True)
    
    # Restaurant and table context
    restaurant_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    table_id = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    
    # Customer context
    user_id = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255), nullable=True)
    
    # Cart session reference
    cart_session_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    
    # Dual status tracking
    order_status = Column(
        ENUM(OrderStatus, name="order_status"), 
        nullable=False, 
        default=OrderStatus.PLACED,
        index=True
    )
    payment_status = Column(
        ENUM(PaymentStatus, name="payment_status"), 
        nullable=False, 
        default=PaymentStatus.PAYMENT_PENDING,
        index=True
    )
    payment_method = Column(
        ENUM(PaymentMethod, name="payment_method"), 
        nullable=False, 
        default=PaymentMethod.CASH
    )
    
    # Order details
    special_instructions = Column(Text, nullable=True)
    estimated_preparation_time = Column(Integer, default=30)
    
    # Pricing (GST compliant)
    subtotal = Column(Numeric(10, 2), nullable=False)
    gst_rate = Column(Numeric(5, 4), nullable=False, default=Decimal('0.05'))
    gst_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Payment collection reference
    payment_reference = Column(String(50), unique=True, nullable=False, index=True)
    
    # Status timestamps
    placed_at = Column(DateTime(timezone=True), default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    preparing_at = Column(DateTime(timezone=True), nullable=True)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    payment_collected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
    payment_collections = relationship("PaymentCollectionModel", back_populates="order", cascade="all, delete-orphan")


class OrderItemModel(Base):
    """SQLAlchemy model for order_items table."""
    
    __tablename__ = "order_items"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    
    # Order relationship
    order_id = Column(PostgresUUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    
    # Menu item relationship
    restaurant_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    menu_item_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    
    # Item details (snapshot)
    item_name = Column(String(255), nullable=False)
    item_description = Column(Text, nullable=True)
    base_price = Column(Numeric(8, 2), nullable=False)
    
    # Quantity and customizations
    quantity = Column(Integer, nullable=False, default=1)
    customizations = Column(JSON, default={})
    special_instructions = Column(Text, nullable=True)
    
    # Pricing
    unit_price = Column(Numeric(8, 2), nullable=False)
    total_price = Column(Numeric(8, 2), nullable=False)
    
    # Status
    is_available = Column(Boolean, default=True)
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    order = relationship("OrderModel", back_populates="items")


class PaymentCollectionModel(Base):
    """SQLAlchemy model for payment_collections table."""
    
    __tablename__ = "payment_collections"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    
    # Order relationship
    order_id = Column(PostgresUUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    payment_reference = Column(String(50), nullable=False, index=True)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(
        ENUM(PaymentMethod, name="payment_method"), 
        nullable=False, 
        default=PaymentMethod.CASH
    )
    
    # Collection details
    collected_by = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    collected_at = Column(DateTime(timezone=True), default=func.now())
    
    # Notes and verification
    collection_notes = Column(Text, nullable=True)
    verification_code = Column(String(10), nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    order = relationship("OrderModel", back_populates="payment_collections")


class OrderPaymentHistoryModel(Base):
    """SQLAlchemy model for order_payment_history table."""
    
    __tablename__ = "order_payment_history"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    
    # Order relationship
    order_id = Column(PostgresUUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    
    # Status change details
    previous_order_status = Column(ENUM(OrderStatus, name="order_status"), nullable=True)
    new_order_status = Column(ENUM(OrderStatus, name="order_status"), nullable=True)
    previous_payment_status = Column(ENUM(PaymentStatus, name="payment_status"), nullable=True)
    new_payment_status = Column(ENUM(PaymentStatus, name="payment_status"), nullable=True)
    
    # Change context
    changed_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    change_reason = Column(Text, nullable=True)
    change_notes = Column(Text, nullable=True)
    
    # Audit timestamp
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
