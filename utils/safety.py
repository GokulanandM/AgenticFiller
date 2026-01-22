"""Safety constraints and policy enforcement."""
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FormAutomationPolicy:
    """Define allowed forms, data sources, and operations."""
    
    def __init__(self):
        self.allowed_forms: Dict[str, str] = {
            # Form URL → authorization level
            "http://localhost:3000/test-form": "DEVELOPMENT",
            "https://localhost:3000/test-form": "DEVELOPMENT",
            # Add more authorized forms here
        }
        
        self.allowed_data_sources = [
            "USER_INPUT",           # Manual entry in UI
            "CSV_UPLOAD",           # Trusted CSV files
            "DATABASE",             # Internal authenticated DB
            "API_WEBHOOK",          # Approved data provider APIs
        ]
        
        self.approval_required = True
        self.max_submissions_per_hour = 10
        self.rate_limit_delay_seconds = 6
        self.require_human_confirmation = True
        self.max_retry_attempts = 3
        
        # Track submissions for rate limiting
        self.submission_timestamps: List[datetime] = []
    
    def verify_authorization(self, form_url: str, user_id: Optional[str] = None) -> bool:
        """Verify user is authorized for this form."""
        # Normalize URL (remove trailing slash, convert to lowercase for comparison)
        normalized_url = str(form_url).rstrip('/').lower()
        
        # Check exact match
        if normalized_url in {url.lower().rstrip('/') for url in self.allowed_forms.keys()}:
            return True
        
        # Check if it's a localhost/development URL
        if normalized_url.startswith(('http://localhost', 'https://localhost', 'http://127.0.0.1')):
            logger.warning(f"Localhost form detected: {form_url} - allowing for development")
            return True
        
        # For production, require explicit authorization
        logger.warning(f"Unauthorized form URL: {form_url}")
        return False
    
    def check_rate_limit(self) -> bool:
        """Check if submission rate limit is exceeded."""
        now = datetime.now()
        # Remove timestamps older than 1 hour
        self.submission_timestamps = [
            ts for ts in self.submission_timestamps
            if (now - ts).total_seconds() < 3600
        ]
        
        if len(self.submission_timestamps) >= self.max_submissions_per_hour:
            return False
        
        return True
    
    def record_submission(self):
        """Record a submission for rate limiting."""
        self.submission_timestamps.append(datetime.now())
    
    def audit_submission(self, submission_record: dict) -> dict:
        """Log every submission for compliance."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": submission_record.get("user_id", "anonymous"),
            "form_url": submission_record.get("form_url"),
            "fields_filled": len(submission_record.get("fields", [])),
            "data_source": submission_record.get("data_source", "USER_INPUT"),
            "status": submission_record.get("status"),
            "approval_given": submission_record.get("user_confirmed", False),
            "error_log": submission_record.get("errors", []),
        }
        logger.info(f"AUDIT: {record}")
        return record
    
    def add_allowed_form(self, form_url: str, authorization_level: str = "SELF_OWNED"):
        """Add a new form to the allowed list."""
        self.allowed_forms[form_url] = authorization_level
        logger.info(f"Added authorized form: {form_url} with level {authorization_level}")


# Global policy instance
policy = FormAutomationPolicy()
