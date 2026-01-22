"""Main FastAPI application for form automation agent."""
import uuid
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from config import settings, get_settings
from models.schemas import (
    TestConnectionRequest, TestConnectionResponse,
    AnalyzeFormRequest, AnalyzeFormResponse,
    FillFormRequest, FillFormResponse,
    FormSchema, ProfileData
)
from agents.azure_agent import AzureFormAgent
from agents.form_filler import FormFiller
from utils.safety import policy
from utils.logger import setup_logging, audit_logger

# Setup logging
setup_logging(settings.log_level, settings.log_file)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    # Startup
    logger.info("Starting Form Automation Agent...")
    logger.info(f"Settings: Debug={settings.debug}, Approval Required={settings.require_approval}")
    yield
    # Shutdown
    logger.info("Shutting down Form Automation Agent...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Safe and legitimate form automation agent with compliance features",
    lifespan=lifespan
)

# Mount static files and templates
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")
    templates = None


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main UI."""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse("""
    <html>
        <head><title>Form Automation Agent</title></head>
        <body>
            <h1>Form Automation Agent</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
            <p>Visit <a href="/ui">/ui</a> for the web interface.</p>
        </body>
    </html>
    """)


@app.get("/ui", response_class=HTMLResponse)
async def ui(request: Request):
    """Serve the web UI."""
    if templates:
        return templates.TemplateResponse("ui.html", {"request": request})
    return HTMLResponse("""
    <html>
        <head>
            <title>Form Automation Agent - UI</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                .container { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
                input, textarea, select { width: 100%; padding: 8px; margin: 5px 0; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .log { background: #000; color: #0f0; padding: 10px; font-family: monospace; max-height: 400px; overflow-y: auto; }
            </style>
        </head>
        <body>
            <h1>Form Automation Agent</h1>
            <p>Please use the API endpoints directly or check the /docs page for Swagger UI.</p>
        </body>
    </html>
    """)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "approval_required": settings.require_approval
    }


@app.post("/test-connection", response_model=TestConnectionResponse)
async def test_connection(request: TestConnectionRequest):
    """Test Azure OpenAI connection."""
    try:
        agent = AzureFormAgent(
            api_key=request.api_key,
            endpoint=request.endpoint,
            deployment_id=request.deployment_id
        )
        
        # Test with a simple prompt
        response = agent.client.chat.completions.create(
            model=request.deployment_id,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Connection successful' if you can read this."}
            ],
            max_tokens=10
        )
        
        message = response.choices[0].message.content
        
        return TestConnectionResponse(
            success=True,
            message="Connection successful",
            model_info={
                "model": request.deployment_id,
                "response": message
            }
        )
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return TestConnectionResponse(
            success=False,
            message=f"Connection failed: {str(e)}"
        )


@app.post("/analyze-form", response_model=AnalyzeFormResponse)
async def analyze_form(request: AnalyzeFormRequest):
    """Analyze a form and extract its schema."""
    log = []
    
    try:
        # Check authorization
        if not policy.verify_authorization(str(request.form_url)):
            log.append(f"⚠️  Form URL not in allowed list: {request.form_url}")
            # Allow localhost for development
            if "localhost" not in str(request.form_url) and "127.0.0.1" not in str(request.form_url):
                raise HTTPException(
                    status_code=403,
                    detail="Form URL not authorized. Please add it to the allowed forms list."
                )
        
        # Get API credentials (use request or settings)
        api_key = request.api_key or settings.azure_api_key
        endpoint = request.endpoint or settings.azure_endpoint
        
        if not api_key or not endpoint:
            raise HTTPException(
                status_code=400,
                detail="Azure OpenAI credentials required (api_key and endpoint)"
            )
        
        log.append(f"✅ Starting form analysis for {request.form_url}")
        
        # Step 1: Extract HTML from form page
        filler = FormFiller(headless=True)
        page_result = await filler.analyze_form_page(str(request.form_url))
        
        if not page_result["success"]:
            return AnalyzeFormResponse(
                success=False,
                error=page_result.get("error", "Failed to load form page"),
                execution_log=page_result.get("execution_log", [])
            )
        
        log.extend(page_result.get("execution_log", []))
        html_content = page_result["html"]
        
        # Step 2: Use Azure OpenAI to extract form fields
        log.append("✅ Analyzing form structure with AI...")
        agent = AzureFormAgent(
            api_key=api_key,
            endpoint=endpoint,
            deployment_id=request.deployment_id
        )
        
        extraction_result = agent.extract_form_fields(html_content)
        
        if "error" in extraction_result:
            log.append(f"❌ Error extracting fields: {extraction_result['error']}")
            return AnalyzeFormResponse(
                success=False,
                error=extraction_result["error"],
                execution_log=log
            )
        
        fields = extraction_result.get("fields", [])
        log.append(f"✅ Extracted {len(fields)} form fields")
        
        # Create form schema
        form_schema = FormSchema(
            form_url=request.form_url,
            fields=fields,
            form_title=extraction_result.get("form_title")
        )
        
        return AnalyzeFormResponse(
            success=True,
            form_schema=form_schema,
            execution_log=log
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Form analysis error: {e}", exc_info=True)
        log.append(f"❌ Fatal error: {str(e)}")
        return AnalyzeFormResponse(
            success=False,
            error=str(e),
            execution_log=log
        )


@app.post("/fill-form", response_model=FillFormResponse)
async def fill_form(request: FillFormRequest):
    """Fill and submit a form."""
    log = []
    submission_id = str(uuid.uuid4())
    
    try:
        # Check authorization
        if not policy.verify_authorization(str(request.form_url)):
            if "localhost" not in str(request.form_url) and "127.0.0.1" not in str(request.form_url):
                raise HTTPException(
                    status_code=403,
                    detail="Form URL not authorized"
                )
        
        # Check approval requirement
        if settings.require_approval and not request.user_confirmed:
            return FillFormResponse(
                success=False,
                status="FAILED",
                error="User approval required before submission",
                execution_log=["⚠️  Approval required - set user_confirmed=true"]
            )
        
        # Get API credentials
        api_key = request.api_key or settings.azure_api_key
        endpoint = request.endpoint or settings.azure_endpoint
        
        if not api_key or not endpoint:
            raise HTTPException(
                status_code=400,
                detail="Azure OpenAI credentials required"
            )
        
        log.append(f"✅ Starting form filling for {request.form_url}")
        
        # Step 1: Analyze form to get schema
        analyze_request = AnalyzeFormRequest(
            form_url=request.form_url,
            api_key=api_key,
            endpoint=endpoint,
            deployment_id=request.deployment_id
        )
        
        analysis_result = await analyze_form(analyze_request)
        
        if not analysis_result.success or not analysis_result.form_schema:
            return FillFormResponse(
                success=False,
                status="FAILED",
                error="Failed to analyze form",
                execution_log=analysis_result.execution_log
            )
        
        form_schema = analysis_result.form_schema
        log.extend(analysis_result.execution_log)
        
        # Step 2: Map profile data to form fields
        log.append("✅ Mapping profile data to form fields...")
        agent = AzureFormAgent(
            api_key=api_key,
            endpoint=endpoint,
            deployment_id=request.deployment_id
        )
        
        profile_dict = request.profile_data.model_dump(exclude_none=True)
        mapping_result = agent.plan_form_fill(form_schema.fields, profile_dict)
        
        if mapping_result.missing_fields:
            log.append(f"⚠️  Missing fields: {', '.join(mapping_result.missing_fields)}")
        
        log.append(f"✅ Created {len(mapping_result.mappings)} field mappings")
        
        # Step 3: Fill and submit form
        log.append("✅ Filling form fields...")
        filler = FormFiller(headless=True)
        
        fill_result = await filler.fill_form(
            form_url=str(request.form_url),
            mappings=mapping_result.mappings,
            form_fields=form_schema.fields
        )
        
        log.extend(fill_result.get("execution_log", []))
        
        # Step 4: Audit logging
        await audit_logger.log_submission({
            "id": submission_id,
            "type": "SUBMISSION_COMPLETED",
            "form_url": str(request.form_url),
            "user_id": "anonymous",  # Would be from auth in production
            "status": fill_result.get("status", "UNKNOWN"),
            "data": profile_dict,
            "fields_filled": fill_result.get("fields_filled", 0),
            "user_confirmed": request.user_confirmed,
            "error": fill_result.get("error")
        })
        
        # Record in policy audit
        policy.audit_submission({
            "user_id": "anonymous",
            "form_url": str(request.form_url),
            "fields": mapping_result.mappings,
            "data_source": "USER_INPUT",
            "status": fill_result.get("status", "UNKNOWN"),
            "user_confirmed": request.user_confirmed,
            "errors": [fill_result.get("error")] if fill_result.get("error") else []
        })
        
        return FillFormResponse(
            success=fill_result.get("success", False),
            status=fill_result.get("status", "FAILED"),
            fields_filled=fill_result.get("fields_filled", 0),
            execution_log=log,
            error=fill_result.get("error"),
            submission_id=submission_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Form filling error: {e}", exc_info=True)
        log.append(f"❌ Fatal error: {str(e)}")
        
        # Audit the failure
        await audit_logger.log_submission({
            "id": submission_id,
            "type": "SUBMISSION_FAILED",
            "form_url": str(request.form_url),
            "status": "FAILED",
            "error": str(e),
            "user_confirmed": request.user_confirmed
        })
        
        return FillFormResponse(
            success=False,
            status="FAILED",
            error=str(e),
            execution_log=log,
            submission_id=submission_id
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
