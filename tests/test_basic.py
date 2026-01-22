"""Basic unit tests for form automation agent."""
import pytest
from utils.safety import FormAutomationPolicy
from models.schemas import FormField, FormFieldType, ProfileData


def test_policy_authorization():
    """Test form authorization policy."""
    policy = FormAutomationPolicy()
    
    # Test localhost authorization
    assert policy.verify_authorization("http://localhost:3000/test-form")
    assert policy.verify_authorization("https://localhost:3000/test-form")
    
    # Test unauthorized form
    assert not policy.verify_authorization("https://unauthorized-site.com/form")


def test_policy_rate_limit():
    """Test rate limiting."""
    policy = FormAutomationPolicy()
    
    # Should allow initial submissions
    assert policy.check_rate_limit()
    
    # Record multiple submissions
    for _ in range(5):
        policy.record_submission()
    
    # Should still be under limit (10 per hour)
    assert policy.check_rate_limit()


def test_form_field_creation():
    """Test FormField model creation."""
    field = FormField(
        field_name="email",
        label="Email Address",
        field_type=FormFieldType.EMAIL,
        required=True
    )
    
    assert field.field_name == "email"
    assert field.field_type == FormFieldType.EMAIL
    assert field.required is True


def test_profile_data_validation():
    """Test ProfileData model."""
    profile = ProfileData(
        full_name="John Doe",
        email="john@example.com",
        phone="+1-555-1234"
    )
    
    assert profile.full_name == "John Doe"
    assert profile.email == "john@example.com"
    assert profile.phone == "+1-555-1234"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
