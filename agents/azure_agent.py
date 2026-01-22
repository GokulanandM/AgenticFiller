"""Azure OpenAI agent for form analysis and field mapping."""
import json
import logging
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from models.schemas import FormField, FormFieldType, FieldMapping, MappingResult

logger = logging.getLogger(__name__)


class AzureFormAgent:
    """Agent that uses Azure OpenAI to analyze forms and map data."""
    
    def __init__(self, api_key: str, endpoint: str, deployment_id: str = "gpt-4-turbo"):
        """Initialize Azure OpenAI client."""
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-02-15-preview",
            azure_endpoint=endpoint
        )
        self.deployment_id = deployment_id
    
    def extract_form_fields(self, html_content: str) -> Dict[str, Any]:
        """Extract form fields from HTML using Azure OpenAI."""
        try:
            # Limit HTML content to avoid token limits
            html_snippet = html_content[:8000]
            
            prompt = f"""Analyze the following HTML form and extract all form fields with their properties.

HTML Content:
{html_snippet}

Return a JSON object with this structure:
{{
    "fields": [
        {{
            "field_name": "unique_identifier",
            "label": "Display label",
            "field_type": "text|email|phone|number|date|select|checkbox|radio|textarea",
            "required": true/false,
            "selector": "CSS selector if identifiable",
            "options": ["option1", "option2"]  // for select/radio
        }}
    ],
    "form_title": "Title of the form if found"
}}

Focus on:
- Input fields (text, email, phone, number, date, password)
- Select dropdowns
- Checkboxes and radio buttons
- Textareas
- Required vs optional fields
- Field labels and their associations

Return ONLY valid JSON, no markdown formatting."""

            response = self.client.chat.completions.create(
                model=self.deployment_id,
                messages=[
                    {"role": "system", "content": "You are a form analysis expert. Extract form fields accurately and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            
            result = json.loads(content)
            
            # Convert to FormField objects
            fields = []
            for field_data in result.get("fields", []):
                try:
                    field_type = FormFieldType(field_data.get("field_type", "text").lower())
                    field = FormField(
                        field_name=field_data.get("field_name", ""),
                        label=field_data.get("label", ""),
                        field_type=field_type,
                        required=field_data.get("required", False),
                        selector=field_data.get("selector"),
                        options=field_data.get("options")
                    )
                    fields.append(field)
                except Exception as e:
                    logger.warning(f"Failed to parse field: {field_data}, error: {e}")
            
            return {
                "fields": fields,
                "form_title": result.get("form_title")
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"fields": [], "form_title": None, "error": str(e)}
        except Exception as e:
            logger.error(f"Error extracting form fields: {e}")
            return {"fields": [], "form_title": None, "error": str(e)}
    
    def plan_form_fill(
        self,
        form_fields: List[FormField],
        profile_data: Dict[str, Any]
    ) -> MappingResult:
        """Map profile data to form fields using AI."""
        try:
            # Prepare field descriptions
            fields_desc = []
            for field in form_fields:
                field_info = {
                    "name": field.field_name,
                    "label": field.label,
                    "type": field.field_type.value,
                    "required": field.required,
                    "options": field.options
                }
                fields_desc.append(field_info)
            
            prompt = f"""Map the provided profile data to the form fields. Return a JSON object with mappings.

Form Fields:
{json.dumps(fields_desc, indent=2)}

Profile Data:
{json.dumps(profile_data, indent=2)}

Return JSON with this structure:
{{
    "mappings": [
        {{
            "form_field": "field_name",
            "value": "actual_value_to_fill",
            "confidence": 0.95,
            "source": "which profile field was used"
        }}
    ],
    "missing_fields": ["field_name1", "field_name2"],
    "ambiguous_fields": [
        {{
            "field": "field_name",
            "candidates": ["option1", "option2"],
            "reason": "explanation"
        }}
    ]
}}

Rules:
- Match fields intelligently (e.g., "fullName" = first_name + last_name)
- Set confidence 0.0-1.0 based on match quality
- List required fields that have no data in "missing_fields"
- Handle ambiguous cases (multiple possible values) in "ambiguous_fields"
- For select/radio fields, match value to available options
- Format values appropriately (dates, phone numbers, etc.)

Return ONLY valid JSON."""

            response = self.client.chat.completions.create(
                model=self.deployment_id,
                messages=[
                    {"role": "system", "content": "You are a data mapping expert. Map profile data to form fields accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            
            result = json.loads(content)
            
            # Convert to FieldMapping objects
            mappings = []
            for mapping_data in result.get("mappings", []):
                # Find the corresponding form field to get selector
                form_field = next(
                    (f for f in form_fields if f.field_name == mapping_data.get("form_field")),
                    None
                )
                
                mapping = FieldMapping(
                    form_field=mapping_data.get("form_field", ""),
                    value=mapping_data.get("value"),
                    confidence=mapping_data.get("confidence", 0.5),
                    source=mapping_data.get("source"),
                    selector=form_field.selector if form_field else None
                )
                mappings.append(mapping)
            
            return MappingResult(
                mappings=mappings,
                missing_fields=result.get("missing_fields", []),
                ambiguous_fields=result.get("ambiguous_fields", [])
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse mapping JSON: {e}")
            return MappingResult(mappings=[], missing_fields=[], ambiguous_fields=[])
        except Exception as e:
            logger.error(f"Error planning form fill: {e}")
            return MappingResult(mappings=[], missing_fields=[], ambiguous_fields=[])
