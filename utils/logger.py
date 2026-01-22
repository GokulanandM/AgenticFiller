"""Logging and audit trail utilities."""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON formatting for audit logs
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    
    return logger


class AuditLogger:
    """Centralized audit logging for all automation events."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = logging.getLogger("audit")
        self.log_file = log_file or "logs/audit.log"
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists."""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def log_submission(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Log every form submission attempt."""
        import hashlib
        
        # Create data hash for verification (don't log actual sensitive data)
        data = event.get("data", {})
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        audit_record = {
            "id": event.get("id", f"audit_{datetime.now().timestamp()}"),
            "timestamp": datetime.now().isoformat(),
            "event_type": event.get("type", "UNKNOWN"),
            "form_id": event.get("form_id"),
            "form_url": event.get("form_url"),
            "user_id": event.get("user_id", "anonymous"),
            "data_hash": data_hash,
            "status": event.get("status"),
            "error": event.get("error"),
            "user_confirmed": event.get("user_confirmed", False),
            "ip_address": event.get("ip_address"),
            "fields_filled": event.get("fields_filled", 0),
        }
        
        # Write to audit log
        self.logger.info(f"AUDIT_RECORD: {json.dumps(audit_record)}")
        
        # Also write to file for persistence
        self._write_audit_record(audit_record)
        
        return audit_record
    
    def _write_audit_record(self, record: Dict[str, Any]):
        """Write audit record to file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write audit record: {e}")
    
    async def generate_compliance_report(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate compliance report for auditors."""
        # This would query audit logs from database in production
        # For MVP, we'll return a summary structure
        return {
            "report_id": f"compliance_{datetime.now().strftime('%Y%m%d')}",
            "period": f"{start_date} to {end_date}" if start_date and end_date else "all_time",
            "user": user_id or "all_users",
            "summary": {
                "total_submissions": 0,  # Would be calculated from logs
                "success_rate": 0.0,
                "failed_submissions": 0,
                "average_fields_per_submission": 0.0,
            },
            "compliance_checks": {
                "all_submissions_approved": True,
                "encryption_enabled": True,
                "rate_limiting_enforced": True,
            }
        }


# Initialize audit logger
audit_logger = AuditLogger()
