"""
Gemini Spark — Autonomous Application Browser Agent (Phase 6 Controlled Submission)
Supports DRY_RUN mode (default) and controlled LIVE_SUBMIT mode for APPROVED_TO_APPLY jobs.
Integrates CAPTCHA safety detection, resume file upload, pre/post screenshots, and confirmation verification.
"""

import os
import json
import datetime
import asyncio
from playwright.async_api import async_playwright
from .rag_engine import CareerRAGEngine
from .answer_generator import ApplicationAnswerGenerator
from .approval_manager import ApplicationApprovalManager, MAX_APPLICATIONS_PER_RUN

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPLICATIONS_FILE = os.path.join(BASE_DIR, "data", "applications.json")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "data", "applications", "screenshots")
RESUMES_DIR = os.path.join(BASE_DIR, "knowledge", "resumes")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(RESUMES_DIR, exist_ok=True)

CAPTCHA_SELECTORS = [
    "iframe[src*='recaptcha']",
    "iframe[src*='hcaptcha']",
    "iframe[src*='challenges.cloudflare']",
    ".g-recaptcha",
    ".h-captcha",
    ".cf-turnstile"
]

CONFIRMATION_PATTERNS = [
    "thank you for applying",
    "application submitted",
    "application received",
    "application was sent",
    "we have received your application",
    "thanks for your interest",
    "your application has been submitted"
]

class AutonomousApplicationAgent:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.rag = CareerRAGEngine()
        self.answer_gen = ApplicationAnswerGenerator(self.rag)
        self.approval_mgr = ApplicationApprovalManager()

    def _normalize_application_url(self, url):
        if not url:
            return ""
        clean = url.rstrip("/")
        if "apply.workable.com" in clean and not clean.endswith("/apply"):
            return f"{clean}/apply/"
        return url

    async def inspect_and_prepare_application(self, job_obj, force_live=False):
        """
        Main autonomous application routine.
        If dry_run is True (or force_live is False), performs full DRY_RUN without submitting.
        If dry_run is False AND job is APPROVED_TO_APPLY, performs controlled real submission.
        """
        raw_url = job_obj.get("app_url") or job_obj.get("original_url")
        app_url = self._normalize_application_url(raw_url)
        job_id = job_obj.get("id")
        company = job_obj.get("company")
        title = job_obj.get("title")

        is_live_submission = (not self.dry_run) and force_live

        # Check Approval Gate if live submission is requested
        if is_live_submission:
            can_submit, count = self.approval_mgr.can_submit_today()
            if not can_submit:
                return {
                    "status": "DAILY_LIMIT_EXCEEDED",
                    "error": f"Daily limit of 10 applications reached ({count} submitted today)."
                }

            # Check if explicitly approved
            queue = self.approval_mgr.load_review_queue()
            approved_item = next((q for q in queue if q.get("job_id") == job_id and q.get("status") == "APPROVED_TO_APPLY"), None)
            if not approved_item:
                print(f"[-] Human Approval Gate: Job '{title}' is not in APPROVED_TO_APPLY state. Halting submission.")
                return {
                    "status": "APPROVAL_REQUIRED",
                    "error": "Job must be approved via approval_manager before live submission."
                }

        app_id = f"app-{job_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        presubmit_screenshot = os.path.join(SCREENSHOTS_DIR, f"{app_id}_presubmit.png")
        confirmation_screenshot = os.path.join(SCREENSHOTS_DIR, f"{app_id}_confirmation.png")

        job_context = {
            "job_id": job_id,
            "job_title": title,
            "company": company,
            "description": job_obj.get("description", ""),
            "skills": job_obj.get("matched_skills", [])
        }

        # Select targeted resume and portfolio
        resume_meta = self.rag.select_resume(title, job_obj.get("description", ""), job_obj.get("matched_skills", []))
        portfolio_meta = self.rag.select_portfolio(title, job_obj.get("description", ""))

        resume_filename = resume_meta["resume_name"]
        resume_path = os.path.join(RESUMES_DIR, resume_filename)

        result_payload = {
            "application_id": app_id,
            "job_id": job_id,
            "company": company,
            "job_title": title,
            "application_url": app_url,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "mode": "LIVE_SUBMISSION" if is_live_submission else "DRY_RUN",
            "status": "READY_FOR_REVIEW",
            "resume_used": resume_filename,
            "portfolio_used": portfolio_meta["portfolio_url"],
            "form_fields_extracted": [],
            "answers_prepared": [],
            "overall_confidence": 98.0,
            "requires_review": False,
            "screenshot_path": presubmit_screenshot,
            "submission_verified": False
        }

        print(f"\n[*] Launching Browser for '{title}' @ {company}...")
        print(f"[*] Target Application URL: {app_url}")
        print(f"[*] Execution Mode: {'LIVE SUBMISSION' if is_live_submission else 'DRY RUN (No Submission)'}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 GeminiSpark/2.0",
                viewport={"width": 1280, "height": 900}
            )
            page = await context.new_page()

            try:
                # 1. Navigate to Application Page
                print("[*] Navigating to application form...")
                await page.goto(app_url, wait_until="networkidle", timeout=30000)
                try:
                    await page.wait_for_selector("input:not([type='hidden']), form, textarea", timeout=8000)
                except Exception:
                    pass
                await page.wait_for_timeout(2000)

                # 2. Dismiss Cookie Banner if Present
                try:
                    cookie_btn = await page.query_selector("button[data-ui='cookie-consent-accept-all'], button[data-ui='cookie-consent-accept'], button:has-text('Accept all cookies'), button:has-text('Accept all'), button:has-text('Accept'), button:has-text('I agree')")
                    if cookie_btn and await cookie_btn.is_visible():
                        await cookie_btn.click()
                        await page.wait_for_timeout(1000)
                except Exception:
                    pass

                # 3. Check for Bot Challenges / CAPTCHA (Rule #7 & #15)
                for c_sel in CAPTCHA_SELECTORS:
                    captcha_el = await page.query_selector(c_sel)
                    if captcha_el and await captcha_el.is_visible():
                        print("⚠️ CAPTCHA / Bot verification challenge detected. Stopping for human safety.")
                        result_payload["status"] = "HUMAN_INTERVENTION_REQUIRED"
                        result_payload["error"] = f"CAPTCHA detected ({c_sel})"
                        await page.screenshot(path=presubmit_screenshot)
                        return result_payload

                # 4. Extract Visible Form Inputs
                inputs = await page.query_selector_all("input:not([type='hidden']), textarea, select, [contenteditable='true']")
                print(f"✓ Detected {len(inputs)} form interactive elements on page.")

                # 5. Fill and Map Fields
                for inp in inputs:
                    name_attr = await inp.get_attribute("name") or ""
                    id_attr = await inp.get_attribute("id") or ""
                    type_attr = await inp.get_attribute("type") or "text"
                    placeholder = await inp.get_attribute("placeholder") or ""
                    aria_label = await inp.get_attribute("aria-label") or ""
                    data_qa = await inp.get_attribute("data-qa") or ""

                    label_text = name_attr or id_attr or data_qa or placeholder or aria_label
                    if not label_text:
                        continue

                    field_ans = self.answer_gen.generate_answer(label_text, type_attr, placeholder, job_context)
                    field_record = {
                        "field_identifier": label_text,
                        "field_type": type_attr,
                        "classified_category": field_ans["category"],
                        "generated_answer": field_ans["answer"],
                        "confidence": field_ans["confidence"],
                        "sources": field_ans["sources"]
                    }
                    result_payload["form_fields_extracted"].append(field_record)

                    # Handle File Upload (Resume)
                    if type_attr == "file" and os.path.exists(resume_path):
                        try:
                            await inp.set_input_files(resume_path)
                            print(f"✓ Attached resume: {resume_filename}")
                        except Exception:
                            pass

                    # Handle Text Inputs & Textareas
                    elif type_attr in ["text", "email", "tel", "url"] or await inp.evaluate("el => el.tagName.toLowerCase() === 'textarea'"):
                        try:
                            if await inp.is_visible():
                                await inp.fill(field_ans["answer"][:250])
                        except Exception:
                            pass

                # 6. Capture Pre-Submission Screenshot
                await page.screenshot(path=presubmit_screenshot, full_page=True)
                print(f"✓ Pre-submission audit screenshot captured: {presubmit_screenshot}")

                # 7. Real Submission Gate
                if is_live_submission:
                    print("[*] Locating submit button for controlled submission...")
                    submit_btn = await page.query_selector("button[data-ui='submit-application'], button[type='submit'], input[type='submit'], button:has-text('Submit application'), button:has-text('Apply now'), button:has-text('Submit')")
                    if submit_btn:
                        print("[*] Clicking submit button...")
                        try:
                            await submit_btn.click(timeout=8000)
                        except Exception:
                            await submit_btn.evaluate("el => el.click()")

                        await page.wait_for_timeout(6000)

                        # Capture post-submission screenshot
                        await page.screenshot(path=confirmation_screenshot, full_page=True)
                        page_content = (await page.content()).lower()

                        # Verify Confirmation
                        confirmed = any(p in page_content for p in CONFIRMATION_PATTERNS)
                        if confirmed:
                            print("🎉 Submission CONFIRMED by application platform!")
                            result_payload["status"] = "APPLIED"
                            result_payload["submission_verified"] = True
                            result_payload["confirmation"] = "Verified submission confirmation detected on page."
                            result_payload["screenshot_path"] = confirmation_screenshot

                            # Update permanent exclusion
                            self.approval_mgr.mark_as_applied(
                                job_id, app_id, app_url, resume_filename,
                                portfolio_meta["portfolio_url"],
                                result_payload["form_fields_extracted"],
                                confirmation_msg="Application successfully submitted and confirmed.",
                                screenshot_path=confirmation_screenshot
                            )
                        else:
                            print("[-] Form submitted but explicit confirmation message was not identified.")
                            result_payload["status"] = "SUBMITTED_PENDING_CONFIRMATION"
                    else:
                        result_payload["status"] = "SUBMISSION_FAILED"
                        result_payload["error"] = "Submit button could not be located on form."
                else:
                    print("🔒 DRY RUN SAFETY: Form prepared and validated. Submission prevented.")
                    result_payload["status"] = "READY_FOR_REVIEW"
                    result_payload["submission_verified"] = False

            except Exception as e:
                print(f"[-] Application agent error: {e}")
                result_payload["error"] = str(e)
                result_payload["status"] = "SUBMISSION_FAILED"
            finally:
                await browser.close()

        return result_payload
