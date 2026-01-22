"""Playwright-based form filling automation."""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser
from models.schemas import FieldMapping, FormField
from utils.safety import policy

logger = logging.getLogger(__name__)


class FormFiller:
    """Automated form filling using Playwright."""
    
    def __init__(self, headless: bool = True):
        """Initialize form filler."""
        self.headless = headless
        self.browser: Optional[Browser] = None
    
    async def analyze_form_page(self, form_url: str) -> Dict[str, Any]:
        """Analyze a form page and extract HTML."""
        log = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                
                log.append(f"✅ Navigating to {form_url}")
                await page.goto(form_url, wait_until="networkidle", timeout=30000)
                
                # Wait a bit for dynamic content
                await asyncio.sleep(2)
                
                # Extract HTML
                html_content = await page.content()
                
                # Try to find form element
                form_element = await page.query_selector("form")
                if not form_element:
                    log.append("⚠️  No <form> element found, looking for input fields")
                
                log.append(f"✅ Page loaded, HTML extracted ({len(html_content)} chars)")
                
                await browser.close()
                
                return {
                    "success": True,
                    "html": html_content,
                    "url": form_url,
                    "execution_log": log
                }
                
        except Exception as e:
            log.append(f"❌ Error analyzing form page: {str(e)}")
            logger.error(f"Form analysis error: {e}", exc_info=True)
            return {
                "success": False,
                "html": "",
                "url": form_url,
                "error": str(e),
                "execution_log": log
            }
    
    async def fill_form(
        self,
        form_url: str,
        mappings: List[FieldMapping],
        form_fields: Optional[List[FormField]] = None
    ) -> Dict[str, Any]:
        """Fill and submit a form."""
        log = []
        fields_filled = 0
        
        try:
            # Check authorization
            if not policy.verify_authorization(form_url):
                return {
                    "success": False,
                    "status": "FAILED",
                    "error": "Form URL not authorized",
                    "execution_log": ["❌ Unauthorized form URL"],
                    "fields_filled": 0
                }
            
            # Check rate limit
            if not policy.check_rate_limit():
                return {
                    "success": False,
                    "status": "FAILED",
                    "error": "Rate limit exceeded",
                    "execution_log": ["❌ Too many submissions in the last hour"],
                    "fields_filled": 0
                }
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                
                log.append(f"✅ Navigating to {form_url}")
                await page.goto(form_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(1)
                
                # Fill each field
                for mapping in mappings:
                    field_name = mapping.form_field
                    value = mapping.value
                    selector = mapping.selector
                    
                    try:
                        # If no selector provided, try common patterns
                        if not selector:
                            # Try by name, id, or label
                            selectors_to_try = [
                                f'input[name="{field_name}"]',
                                f'input[id="{field_name}"]',
                                f'textarea[name="{field_name}"]',
                                f'select[name="{field_name}"]',
                            ]
                            element = None
                            for sel in selectors_to_try:
                                element = await page.query_selector(sel)
                                if element:
                                    selector = sel
                                    break
                        else:
                            element = await page.query_selector(selector)
                        
                        if not element:
                            log.append(f"⚠️  Field not found: {field_name} (selector: {selector})")
                            continue
                        
                        # Get element type
                        tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                        input_type = await element.get_attribute("type") or ""
                        
                        # Fill based on type
                        if tag_name == "select":
                            await page.select_option(selector, str(value))
                            log.append(f"✅ Selected: {field_name} = {value}")
                            fields_filled += 1
                        elif input_type == "checkbox":
                            if value:
                                await element.click()
                            log.append(f"✅ Checkbox: {field_name} = {value}")
                            fields_filled += 1
                        elif input_type == "radio":
                            await element.click()
                            log.append(f"✅ Radio: {field_name} = {value}")
                            fields_filled += 1
                        elif tag_name == "textarea":
                            await page.fill(selector, str(value))
                            log.append(f"✅ Filled textarea: {field_name} = {value}")
                            fields_filled += 1
                        else:
                            # Regular input field
                            await page.fill(selector, str(value))
                            log.append(f"✅ Filled: {field_name} = {value}")
                            fields_filled += 1
                        
                    except Exception as e:
                        log.append(f"❌ Error filling {field_name}: {str(e)}")
                        logger.warning(f"Error filling field {field_name}: {e}")
                
                # Check for CAPTCHA
                captcha_selectors = [
                    '[class*="captcha"]',
                    '[id*="captcha"]',
                    '[class*="recaptcha"]',
                    '[id*="recaptcha"]',
                    'iframe[src*="recaptcha"]'
                ]
                
                captcha_detected = False
                for selector in captcha_selectors:
                    if await page.query_selector(selector):
                        captcha_detected = True
                        break
                
                if captcha_detected:
                    log.append("❌ CAPTCHA detected - cannot proceed without manual intervention")
                    await browser.close()
                    return {
                        "success": False,
                        "status": "FAILED",
                        "error": "CAPTCHA detected",
                        "execution_log": log,
                        "fields_filled": fields_filled
                    }
                
                # Find submit button
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Send")',
                    'button:has-text("Apply")',
                    'form button:last-child',  # Last button in form
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    submit_button = await page.query_selector(selector)
                    if submit_button:
                        log.append(f"✅ Submit button found: {selector}")
                        break
                
                if not submit_button:
                    log.append("⚠️  Submit button not found with common selectors")
                    # Try to find any button in the form
                    submit_button = await page.query_selector("form button")
                    if submit_button:
                        log.append("✅ Found button in form")
                
                if submit_button:
                    # Wait a moment before submitting
                    await asyncio.sleep(1)
                    
                    log.append("🟡 Submitting form...")
                    await submit_button.click()
                    
                    # Wait for response
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                        await asyncio.sleep(2)  # Give time for redirect/confirmation
                    except Exception as e:
                        log.append(f"⚠️  Timeout waiting for response: {e}")
                    
                    # Check for success indicators
                    page_text = (await page.locator("body").text_content() or "").lower()
                    success_indicators = [
                        "success", "confirmation", "thank you", "submitted",
                        "application received", "accepted", "successful"
                    ]
                    
                    if any(indicator in page_text for indicator in success_indicators):
                        log.append("✅ SUCCESS: Form submission confirmed!")
                        status = "SUCCESS"
                    else:
                        log.append("❓ Response unclear - check manually")
                        status = "UNCLEAR"
                    
                    # Record submission for rate limiting
                    policy.record_submission()
                    
                    await browser.close()
                    
                    return {
                        "success": True,
                        "status": status,
                        "execution_log": log,
                        "fields_filled": fields_filled
                    }
                else:
                    log.append("❌ Submit button not found")
                    await browser.close()
                    return {
                        "success": False,
                        "status": "FAILED",
                        "error": "No submit button found",
                        "execution_log": log,
                        "fields_filled": fields_filled
                    }
                
        except Exception as e:
            log.append(f"❌ FATAL ERROR: {str(e)}")
            logger.error(f"Form filling error: {e}", exc_info=True)
            return {
                "success": False,
                "status": "FAILED",
                "error": str(e),
                "execution_log": log,
                "fields_filled": fields_filled
            }
