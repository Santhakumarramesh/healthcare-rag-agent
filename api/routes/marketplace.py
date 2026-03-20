"""
Marketplace product and order endpoints.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db
from database.models import Product, Order, OrderItem

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.get("/products")
def list_products(
    category: str = None,
    condition_tag: str = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """
    List marketplace products with filtering.

    Filter by:
    - category
    - condition_tag
    """
    q = db.query(Product).filter(Product.is_active == True)

    if category:
        q = q.filter(Product.category == category)

    if condition_tag:
        q = q.filter(Product.conditions.contains([condition_tag]))

    offset = (page - 1) * per_page
    products = q.offset(offset).limit(per_page).all()

    return {
        "total": q.count(),
        "products": [
            {
                "product_id": p.product_id,
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "price": p.price,
                "image_url": p.image_url,
                "tags": p.tags,
                "conditions": p.conditions,
                "stock": p.stock
            }
            for p in products
        ]
    }


@router.get("/products/{product_id}")
def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """
    Get product details.
    """
    product = db.query(Product).filter(Product.product_id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return {
        "product_id": product.product_id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "price": product.price,
        "image_url": product.image_url,
        "tags": product.tags,
        "conditions": product.conditions,
        "stock": product.stock
    }


@router.post("/orders")
def create_order(
    items: list,  # [{product_id, quantity}, ...]
    shipping_address: dict,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create marketplace order.

    items: List of {product_id, quantity}
    """
    # Calculate total
    total = 0
    order_items = []

    for item in items:
        product = db.query(Product).filter(
            Product.product_id == item["product_id"]
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item['product_id']} not found"
            )

        if product.stock < item["quantity"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}"
            )

        item_total = product.price * item["quantity"]
        total += item_total

        order_items.append({
            "product_id": product.id,
            "quantity": item["quantity"],
            "unit_price": product.price
        })

    # Create order
    order = Order(
        order_id=str(uuid.uuid4()),
        user_id=user["user_id"],
        status="pending",
        total=total,
        shipping_address=shipping_address
    )

    db.add(order)
    db.flush()

    # Add order items
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"]
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)

    return {
        "order_id": order.order_id,
        "status": order.status,
        "total": order.total,
        "items_count": len(order_items),
        "created_at": order.created_at
    }


@router.get("/orders")
def list_orders(
    user: dict = Depends(get_current_user),
    status_filter: str = None,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """
    List orders for current user.
    """
    q = db.query(Order).filter(Order.user_id == user["user_id"])

    if status_filter:
        q = q.filter(Order.status == status_filter)

    offset = (page - 1) * per_page
    orders = q.offset(offset).limit(per_page).order_by(
        Order.created_at.desc()
    ).all()

    return {
        "total": q.count(),
        "orders": [
            {
                "order_id": o.order_id,
                "status": o.status,
                "total": o.total,
                "items_count": len(o.items),
                "created_at": o.created_at
            }
            for o in orders
        ]
    }


@router.get("/orders/{order_id}")
def get_order(
    order_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order details with items and tracking.
    """
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.user_id == user["user_id"]
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    return {
        "order_id": order.order_id,
        "status": order.status,
        "total": order.total,
        "shipping_address": order.shipping_address,
        "payment_status": order.payment_status,
        "items": [
            {
                "product_id": oi.product.product_id,
                "product_name": oi.product.name,
                "quantity": oi.quantity,
                "unit_price": oi.unit_price
            }
            for oi in items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }
