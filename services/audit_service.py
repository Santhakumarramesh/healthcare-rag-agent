"""
Audit Logging Service - Compliance and security tracking.

Features:
- Action logging for compliance
- User activity tracking
- Security event monitoring
- HIPAA-compliant audit trails
"""
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque
from enum import Enum
from loguru import logger


class AuditEventType(str, Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    QUERY_SUBMITTED = "query_submitted"
    REPORT_UPLOADED = "report_uploaded"
    REPORT_ACCESSED = "report_accessed"
    DATA_EXPORTED = "data_exported"
    SETTINGS_CHANGED = "settings_changed"
    ALERT_TRIGGERED = "alert_triggered"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    PERMISSION_DENIED = "permission_denied"
    SECURITY_VIOLATION = "security_violation"


class AuditService:
    """
    Audit logging service for compliance and security.

    Tracks all user actions and system events for:
    - HIPAA compliance
    - Security monitoring
    - User activity tracking
    - Forensic analysis
    """

    def __init__(self, max_logs: int = 10000):
        """
        Initialize audit service.

        Args:
            max_logs: Maximum number of logs to keep in memory
        """
        self.logs: deque = deque(maxlen=max_logs)
        self.max_logs = max_logs

        logger.info(f"[AuditService] Initialized with max_logs={max_logs}")

    def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        action: str = "",
        resource: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Log an audit event.

        Args:
            event_type: Type of event
            user_id: User ID performing action
            user_email: User email
            user_role: User role
            action: Description of action
            resource: Resource accessed/modified
            details: Additional event details
            ip_address: Client IP address
            success: Whether action succeeded
            error_message: Error message if failed
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "user_email": user_email,
            "user_role": user_role,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address,
            "success": success,
            "error_message": error_message
        }

        self.logs.append(event)

        # Log to file for persistence
        log_level = "success" if success else "warning"
        getattr(logger, log_level)(
            f"[AuditLog] {event_type} | User: {user_email or 'anonymous'} | "
            f"Action: {action} | Success: {success}"
        )

    def log_login(self, user_id: str, user_email: str, user_role: str, ip_address: Optional[str] = None):
        """Log user login"""
        self.log_event(
            event_type=AuditEventType.USER_LOGIN,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action="User logged in",
            ip_address=ip_address,
            success=True
        )

    def log_query(
        self,
        user_id: Optional[str],
        query: str,
        query_type: str,
        confidence: float,
        session_id: str
    ):
        """Log query submission"""
        self.log_event(
            event_type=AuditEventType.QUERY_SUBMITTED,
            user_id=user_id,
            action=f"Query submitted: {query_type}",
            resource=f"session:{session_id}",
            details={
                "query_preview": query[:100],
                "query_type": query_type,
                "confidence": confidence,
                "query_length": len(query)
            },
            success=True
        )

    def log_report_upload(
        self,
        user_id: Optional[str],
        filename: str,
        file_size: int,
        session_id: str
    ):
        """Log report upload"""
        self.log_event(
            event_type=AuditEventType.REPORT_UPLOADED,
            user_id=user_id,
            action=f"Report uploaded: {filename}",
            resource=f"session:{session_id}",
            details={
                "filename": filename,
                "file_size_bytes": file_size
            },
            success=True
        )

    def log_alert(
        self,
        user_id: Optional[str],
        alert_type: str,
        severity: str,
        message: str
    ):
        """Log clinical alert"""
        self.log_event(
            event_type=AuditEventType.ALERT_TRIGGERED,
            user_id=user_id,
            action=f"Alert triggered: {alert_type}",
            details={
                "alert_type": alert_type,
                "severity": severity,
                "message": message
            },
            success=True
        )

    def log_permission_denied(
        self,
        user_id: Optional[str],
        user_email: Optional[str],
        user_role: Optional[str],
        attempted_action: str,
        required_role: str
    ):
        """Log permission denied"""
        self.log_event(
            event_type=AuditEventType.PERMISSION_DENIED,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=f"Permission denied: {attempted_action}",
            details={
                "attempted_action": attempted_action,
                "required_role": required_role
            },
            success=False,
            error_message=f"User role '{user_role}' insufficient for action requiring '{required_role}'"
        )

    def get_logs(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve audit logs with filters.

        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of logs to return

        Returns:
            List of matching audit logs
        """
        filtered_logs = list(self.logs)

        # Apply filters
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.get("user_id") == user_id]

        if event_type:
            filtered_logs = [log for log in filtered_logs if log.get("event_type") == event_type]

        if start_time:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log["timestamp"]) >= start_time
            ]

        if end_time:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log["timestamp"]) <= end_time
            ]

        # Return most recent first
        filtered_logs.reverse()

        return filtered_logs[:limit]

    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent activity for a user"""
        return self.get_logs(user_id=user_id, limit=limit)

    def get_security_events(self, limit: int = 100) -> List[Dict]:
        """Get recent security-related events"""
        security_types = [
            AuditEventType.PERMISSION_DENIED,
            AuditEventType.SECURITY_VIOLATION,
            AuditEventType.USER_LOGIN
        ]

        security_logs = []
        for log in reversed(list(self.logs)):
            if log.get("event_type") in security_types:
                security_logs.append(log)
                if len(security_logs) >= limit:
                    break

        return security_logs

    def get_statistics(self) -> Dict:
        """Get audit log statistics"""
        total_logs = len(self.logs)

        # Count by event type
        by_event_type = {}
        for log in self.logs:
            event_type = log.get("event_type")
            by_event_type[event_type] = by_event_type.get(event_type, 0) + 1

        # Count successes/failures
        successes = sum(1 for log in self.logs if log.get("success"))
        failures = total_logs - successes

        # Count unique users
        unique_users = len(set(log.get("user_id") for log in self.logs if log.get("user_id")))

        # Recent activity (last hour)
        one_hour_ago = datetime.now().timestamp() - 3600
        recent_logs = [
            log for log in self.logs
            if datetime.fromisoformat(log["timestamp"]).timestamp() > one_hour_ago
        ]

        return {
            "total_logs": total_logs,
            "by_event_type": by_event_type,
            "success_count": successes,
            "failure_count": failures,
            "unique_users": unique_users,
            "recent_activity_count": len(recent_logs),
            "oldest_log": self.logs[0]["timestamp"] if self.logs else None,
            "newest_log": self.logs[-1]["timestamp"] if self.logs else None
        }


# Singleton instance
audit_service = AuditService()
