"""
Admin and platform management endpoints.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_roles, get_db
from database.models import User, DoctorApproval, ProcessingJob, Alert, SupportTicket, AuditLog

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def get_admin_dashboard(
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Get platform dashboard stats (admin only).
    """
    total_users = db.query(User).count()
    patients = db.query(User).filter(User.role == "patient").count()
    doctors = db.query(User).filter(User.role == "doctor").count()
    pending_approvals = db.query(DoctorApproval).filter(
        DoctorApproval.status == "pending"
    ).count()
    active_alerts = db.query(Alert).filter(
        Alert.is_acknowledged == False
    ).count()

    return {
        "total_users": total_users,
        "patient_count": patients,
        "doctor_count": doctors,
        "pending_doctor_approvals": pending_approvals,
        "active_clinical_alerts": active_alerts
    }


@router.get("/users")
def list_users(
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    role: str = None,
    is_active: bool = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """
    List all users with filtering (admin only).
    """
    q = db.query(User)

    if role:
        q = q.filter(User.role == role)

    if is_active is not None:
        q = q.filter(User.is_active == is_active)

    offset = (page - 1) * per_page
    users = q.offset(offset).limit(per_page).all()

    return {
        "total": q.count(),
        "users": [
            {
                "user_id": u.user_id,
                "email": u.email,
                "name": u.name,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at
            }
            for u in users
        ]
    }


@router.post("/users/{user_id}/suspend")
def suspend_user(
    user_id: str,
    reason: str,
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Suspend user account (admin only).
    """
    target_user = db.query(User).filter(User.user_id == user_id).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    target_user.is_active = False

    # Log action
    audit = AuditLog(
        timestamp=datetime.utcnow(),
        event_type="user_suspension",
        user_id=user["user_id"],
        action=f"Suspended user {user_id}: {reason}",
        resource="users",
        success=True
    )
    db.add(audit)
    db.commit()

    return {"message": f"User {user_id} suspended"}


@router.post("/users/{user_id}/reinstate")
def reinstate_user(
    user_id: str,
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Reinstate user account (admin only).
    """
    target_user = db.query(User).filter(User.user_id == user_id).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    target_user.is_active = True

    # Log action
    audit = AuditLog(
        timestamp=datetime.utcnow(),
        event_type="user_reinstatement",
        user_id=user["user_id"],
        action=f"Reinstated user {user_id}",
        resource="users",
        success=True
    )
    db.add(audit)
    db.commit()

    return {"message": f"User {user_id} reinstated"}


@router.get("/doctors/pending")
def get_pending_doctor_approvals(
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Get pending doctor approvals (admin only).
    """
    approvals = db.query(DoctorApproval).filter(
        DoctorApproval.status == "pending"
    ).order_by(DoctorApproval.submitted_at).all()

    return {
        "pending_count": len(approvals),
        "approvals": [
            {
                "doctor_id": a.doctor_id,
                "status": a.status,
                "submitted_at": a.submitted_at,
                "submitted_docs": a.submitted_docs
            }
            for a in approvals
        ]
    }


@router.post("/doctors/{doctor_id}/approve")
def approve_doctor(
    doctor_id: str,
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Approve doctor registration (admin only).
    """
    approval = db.query(DoctorApproval).filter(
        DoctorApproval.doctor_id == doctor_id
    ).first()

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor approval not found"
        )

    approval.status = "verified"
    approval.admin_id = user["user_id"]
    approval.reviewed_at = datetime.utcnow()

    db.commit()

    return {"message": f"Doctor {doctor_id} approved"}


@router.post("/doctors/{doctor_id}/reject")
def reject_doctor(
    doctor_id: str,
    reason: str,
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Reject doctor registration (admin only).
    """
    approval = db.query(DoctorApproval).filter(
        DoctorApproval.doctor_id == doctor_id
    ).first()

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor approval not found"
        )

    approval.status = "rejected"
    approval.admin_id = user["user_id"]
    approval.reviewer_notes = reason
    approval.reviewed_at = datetime.utcnow()

    db.commit()

    return {"message": f"Doctor {doctor_id} rejected"}


@router.get("/jobs/failed")
def get_failed_jobs(
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get failed processing jobs (admin only).
    """
    q = db.query(ProcessingJob).filter(ProcessingJob.status == "failed")

    offset = (page - 1) * per_page
    jobs = q.offset(offset).limit(per_page).all()

    return {
        "total": q.count(),
        "jobs": [
            {
                "job_id": j.job_id,
                "job_type": j.job_type,
                "attempts": j.attempts,
                "error": j.error,
                "queued_at": j.queued_at
            }
            for j in jobs
        ]
    }


@router.post("/jobs/{job_id}/retry")
def retry_failed_job(
    job_id: str,
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Retry a failed processing job (admin only).
    """
    job = db.query(ProcessingJob).filter(ProcessingJob.job_id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.attempts >= job.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max retry attempts exceeded"
        )

    job.status = "pending"
    job.attempts += 1
    job.error = None

    db.commit()

    return {"message": f"Job {job_id} queued for retry"}


@router.get("/alerts")
def list_alerts(
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    severity: str = None,
    acknowledged: bool = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """
    List clinical alerts (admin only).
    """
    q = db.query(Alert)

    if severity:
        q = q.filter(Alert.severity == severity)

    if acknowledged is not None:
        q = q.filter(Alert.is_acknowledged == acknowledged)

    offset = (page - 1) * per_page
    alerts = q.offset(offset).limit(per_page).order_by(Alert.created_at.desc()).all()

    return {
        "total": q.count(),
        "alerts": [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "is_acknowledged": a.is_acknowledged,
                "created_at": a.created_at
            }
            for a in alerts
        ]
    }


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: str,
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Mark alert as resolved (admin only).
    """
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    alert.is_acknowledged = True
    alert.acknowledged_by = user["user_id"]
    alert.acknowledged_at = datetime.utcnow()

    db.commit()

    return {"message": f"Alert {alert_id} resolved"}


@router.get("/support-tickets")
def list_support_tickets(
    user: dict = Depends(require_roles(["admin", "support", "superadmin"])),
    status: str = None,
    priority: str = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """
    List support tickets (support staff only).
    """
    q = db.query(SupportTicket)

    if status:
        q = q.filter(SupportTicket.status == status)

    if priority:
        q = q.filter(SupportTicket.priority == priority)

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
                "priority": t.priority,
                "status": t.status,
                "created_at": t.created_at
            }
            for t in tickets
        ]
    }


@router.post("/support-tickets/{ticket_id}/assign")
def assign_ticket(
    ticket_id: str,
    assigned_to: str,
    user: dict = Depends(require_roles(["admin", "support", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Assign support ticket to agent.
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    ticket.assigned_to = assigned_to
    ticket.status = "in_progress"

    db.commit()

    return {"message": f"Ticket {ticket_id} assigned"}


@router.post("/support-tickets/{ticket_id}/resolve")
def resolve_ticket(
    ticket_id: str,
    resolution: str,
    user: dict = Depends(require_roles(["admin", "support", "superadmin"])),
    db: Session = Depends(get_db)
):
    """
    Mark support ticket as resolved.
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    ticket.status = "resolved"
    ticket.resolution = resolution
    ticket.resolved_at = datetime.utcnow()

    db.commit()

    return {"message": f"Ticket {ticket_id} resolved"}


@router.get("/audit-logs")
def get_audit_logs(
    user: dict = Depends(require_roles(["admin", "superadmin"])),
    event_type: str = None,
    user_id: str = None,
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get paginated audit logs (admin only).
    """
    q = db.query(AuditLog)

    if event_type:
        q = q.filter(AuditLog.event_type == event_type)

    if user_id:
        q = q.filter(AuditLog.user_id == user_id)

    offset = (page - 1) * per_page
    logs = q.offset(offset).limit(per_page).order_by(
        AuditLog.timestamp.desc()
    ).all()

    return {
        "total": q.count(),
        "audit_logs": [
            {
                "timestamp": l.timestamp,
                "event_type": l.event_type,
                "user_id": l.user_id,
                "action": l.action,
                "success": l.success
            }
            for l in logs
        ]
    }
