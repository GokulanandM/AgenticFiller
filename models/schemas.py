"""Pydantic models for request/response schemas."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum


class FormFieldType(str, Enum):
    """Supported form field types."""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FILE = "file"
    PASSWORD = "password"


class FormField(BaseModel):
    """Represents a form field."""
    field_name: str = Field(..., description="Internal field identifier")
    label: str = Field(..., description="Display label for the field")
    field_type: FormFieldType = Field(..., description="Type of input field")
    required: bool = Field(default=False, description="Whether field is required")
    selector: Optional[str] = Field(None, description="CSS selector for the field")
    options: Optional[List[str]] = Field(None, description="Options for select/radio fields")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Validation constraints")


class FormSchema(BaseModel):
    """Complete form schema with all fields."""
    form_url: HttpUrl
    fields: List[FormField] = Field(default_factory=list)
    form_title: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)


class FieldMapping(BaseModel):
    """Mapping between data source and form field."""
    form_field: str = Field(..., description="Target form field name")
    value: Any = Field(..., description="Value to fill")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    source: Optional[str] = Field(None, description="Source of the mapping")
    selector: Optional[str] = Field(None, description="CSS selector for the field")


class MappingResult(BaseModel):
    """Result of field mapping operation."""
    mappings: List[FieldMapping] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    ambiguous_fields: List[Dict[str, Any]] = Field(default_factory=list)


class ProfileData(BaseModel):
    """User profile data for form filling."""
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    dob: Optional[str] = None
    education: Optional[str] = None
    cgpa: Optional[float] = None
    experience: Optional[int] = None
    skills: Optional[str] = None
    additional_info: Optional[str] = None
    # Allow additional fields
    class Config:
        extra = "allow"


class TestConnectionRequest(BaseModel):
    """Request to test Azure OpenAI connection."""
    api_key: str
    endpoint: str
    deployment_id: str = "gpt-4-turbo"


class TestConnectionResponse(BaseModel):
    """Response from connection test."""
    success: bool
    message: str
    model_info: Optional[Dict[str, Any]] = None


class AnalyzeFormRequest(BaseModel):
    """Request to analyze a form."""
    form_url: HttpUrl
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    deployment_id: str = "gpt-4-turbo"


class AnalyzeFormResponse(BaseModel):
    """Response from form analysis."""
    success: bool
    form_schema: Optional[FormSchema] = None
    error: Optional[str] = None
    execution_log: List[str] = Field(default_factory=list)


class FillFormRequest(BaseModel):
    """Request to fill and submit a form."""
    form_url: HttpUrl
    profile_data: ProfileData
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    deployment_id: str = "gpt-4-turbo"
    require_approval: bool = True
    user_confirmed: bool = False


class FillFormResponse(BaseModel):
    """Response from form filling operation."""
    success: bool
    status: str = Field(..., description="SUCCESS, FAILED, UNCLEAR")
    fields_filled: int = 0
    execution_log: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    submission_id: Optional[str] = None
    confirmation_url: Optional[str] = None
