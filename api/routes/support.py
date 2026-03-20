"""
Support ticket endpoints.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db
from database.models import SupportTicket

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/tickets")
def create_support_ticket(
    subject: str,
    description: str,
    category: str,
    priority: str = "medium",
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create support ticket.

    Categories: account, billing, technical, medical, other
    Priority: low, medium, high, urgent
    """
    ticket = SupportTicket(
        ticket_id=str(uuid.uuid4()),
        user_id=user["user_id"],
        subject=subject,
        description=description,
        category=category,
        priority=priority,
        status="open",
        created_at=datetime.utcnow()
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "ticket_id": ticket.ticket_id,
        "subject": subject,
        "status": "open",
        "priority": priority,
        "created_at": ticket.created_at
    }


@router.get("/tickets")
def list_support_tickets(
    user: dict = Depends(get_current_user),
    status_filter: str = None,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """
    List support tickets for current user.
    """
    q = db.query(SupportTicket).filter(SupportTicket.user_id == user["user_id"])

    if status_filter:
        q = q.filter(SupportTicket.status == status_filter)

    offset = (page - 1) * per_page
    tickets = q.offset(offset).limit(per_page).order_by(
        SupportTicket.created_at.desc()
    ).all()

    return {
        "total": q.count(),
        "tickets": [
            {
                "ticket_id": t.ticket_id,
                "subject": t.subject,
                "category": t.category,
                "priority": t.priority,
                "status": t.status,
                "assigned_to": t.assigned_to,
                "created_at": t.created_at,
                "updated_at": t.updated_at
            }
            for t in tickets
        ]
    }


@router.get("/tickets/{ticket_id}")
def get_support_ticket(
    ticket_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get support ticket details.
    """
    ticket = db.query(SupportTicket).filter(
        SupportTicket.ticket_id == ticket_id,
        SupportTicket.user_id == user["user_id"]
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return {
        "ticket_id": ticket.ticket_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "assigned_to": ticket.assigned_to,
        "resolution": ticket.resolution,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "resolved_at": ticket.resolved_at
    }


@router.post("/tickets/{ticket_id}/messages")
def add_ticket_message(
    ticket_id: str,
    message: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add message/reply to support ticket.
    """
    ticket = db.query(SupportTicket).filter(
        SupportTicket.ticket_id == ticket_id,
        SupportTicket.user_id == user["user_id"]
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # TODO: Create message record
    # For now, update ticket updated_at timestamp

    ticket.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Reply added to ticket",
        "ticket_id": ticket_id
    }
