"""
Gemini Spark — Application Approval & Review Queue Manager (Phase 6)
Manages the application lifecycle states:
READY_FOR_REVIEW ➔ APPROVED_TO_APPLY ➔ APPLIED
Enforces safety thresholds (MIN_MATCH_SCORE=85, MAX_PER_RUN=3, MAX_PER_DAY=10).
"""

import os
import json
import datetime
from .rag_engine import CareerRAGEngine
from .answer_generator import ApplicationAnswerGenerator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REVIEW_QUEUE_FILE = os.path.join(BASE_DIR, "data", "application_review_queue.json")
APPLICATIONS_FILE = os.path.join(BASE_DIR, "data", "applications.json")
STATUS_FILE = os.path.join(BASE_DIR, "data", "application_status.json")

MIN_MATCH_SCORE = 85.0
MAX_APPLICATIONS_PER_RUN = 3
MAX_APPLICATIONS_PER_DAY = 10

class ApplicationApprovalManager:
    def __init__(self):
        self.rag = CareerRAGEngine()
        self.answer_gen = ApplicationAnswerGenerator(self.rag)
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs(os.path.dirname(REVIEW_QUEUE_FILE), exist_ok=True)
        if not os.path.exists(REVIEW_QUEUE_FILE):
            with open(REVIEW_QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_review_queue(self):
        try:
            with open(REVIEW_QUEUE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_review_queue(self, queue):
        with open(REVIEW_QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)

    def load_application_history(self):
        if os.path.exists(APPLICATIONS_FILE):
            try:
                with open(APPLICATIONS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def get_applications_submitted_today(self):
        history = self.load_application_history()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        today_str = now_utc.strftime("%Y-%m-%d")
        
        count = 0
        for item in history:
            if item.get("status") == "APPLIED":
                ts = item.get("submitted_at") or item.get("timestamp", "")
                if ts.startswith(today_str):
                    count += 1
        return count

    def can_submit_today(self):
        """Checks daily safety cap."""
        count = self.get_applications_submitted_today()
        return count < MAX_APPLICATIONS_PER_DAY, count

    def prepare_job_for_review(self, job_obj):
        """
        Evaluates a verified GHL job and prepares the complete review payload.
        Sets status = READY_FOR_REVIEW if eligible.
        """
        score = float(job_obj.get("score", 0))
        job_id = job_obj.get("id")
        title = job_obj.get("title")
        company = job_obj.get("company")
        app_url = job_obj.get("app_url") or job_obj.get("original_url")

        # 1. Eligibility Check
        if score < MIN_MATCH_SCORE:
            return None, f"Score {score}% below threshold of {MIN_MATCH_SCORE}%"

        # Check if already applied or in queue
        queue = self.load_review_queue()
        for q in queue:
            if q.get("job_id") == job_id:
                return q, "Already in review queue"

        history = self.load_application_history()
        for h in history:
            if h.get("job_id") == job_id and h.get("status") == "APPLIED":
                return None, "Already applied previously"

        # Select targeted resume & portfolio
        resume_meta = self.rag.select_resume(title, job_obj.get("description", ""), job_obj.get("matched_skills", []))
        portfolio_meta = self.rag.select_portfolio(title, job_obj.get("description", ""))

        # Pre-generate standard answers
        job_context = {
            "job_id": job_id,
            "job_title": title,
            "company": company,
            "description": job_obj.get("description", ""),
            "skills": job_obj.get("matched_skills", [])
        }

        sample_questions = [
            ("Full Name", "text"),
            ("Email", "email"),
            ("Phone", "tel"),
            ("Location", "text"),
            ("How many years of GoHighLevel experience do you have?", "textarea"),
            ("Describe your workflow automation and AI bot experience", "textarea"),
            ("Why are you interested in this role?", "textarea"),
            ("What is your salary expectation?", "text"),
            ("When can you start?", "text")
        ]

        answers = []
        overall_confidence = 100
        requires_review = False

        for q_text, q_type in sample_questions:
            ans = self.answer_gen.generate_answer(q_text, q_type, job_context=job_context)
            answers.append({
                "question": q_text,
                "answer": ans["answer"],
                "category": ans["category"],
                "confidence": ans["confidence"],
                "sources": ans["sources"]
            })
            if ans["confidence"] < 85 or ans["requires_review"]:
                requires_review = True
                overall_confidence = min(overall_confidence, ans["confidence"])

        review_item = {
            "job_id": job_id,
            "company": company,
            "job_title": title,
            "match_score": score,
            "application_url": app_url,
            "selected_resume": resume_meta["resume_name"],
            "selected_resume_focus": resume_meta["focus"],
            "selected_portfolio": portfolio_meta["portfolio_url"],
            "answers": answers,
            "confidence": overall_confidence,
            "requires_review": requires_review,
            "status": "NEEDS_REVIEW" if requires_review else "READY_FOR_REVIEW",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "approved_at": None,
            "approval_notes": ""
        }

        queue.append(review_item)
        self.save_review_queue(queue)
        return review_item, "Successfully queued for review"

    def approve_application(self, job_id, notes="Approved by user"):
        """
        Moves application state from READY_FOR_REVIEW ➔ APPROVED_TO_APPLY.
        """
        queue = self.load_review_queue()
        found = False
        target_item = None

        for item in queue:
            if item.get("job_id") == job_id:
                if item.get("status") == "APPLIED":
                    return False, "Job has already been applied."
                item["status"] = "APPROVED_TO_APPLY"
                item["approved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                item["approval_notes"] = notes
                found = True
                target_item = item
                break

        if found:
            self.save_review_queue(queue)
            return True, f"Application for '{target_item.get('job_title')}' @ {target_item.get('company')} is now APPROVED_TO_APPLY."
        return False, f"Job ID {job_id} not found in review queue."

    def reject_application(self, job_id, reason="User rejected"):
        """
        Rejects an application from the review queue.
        """
        queue = self.load_review_queue()
        for item in queue:
            if item.get("job_id") == job_id:
                item["status"] = "REJECTED_BY_USER"
                item["rejection_reason"] = reason
                self.save_review_queue(queue)
                return True, f"Job {job_id} marked REJECTED_BY_USER."
        return False, f"Job ID {job_id} not found."

    def mark_as_applied(self, job_id, application_id, app_url, resume_used, portfolio_used, answers, confirmation_msg="", screenshot_path=""):
        """
        Marks application state as APPLIED in both review queue, applications.json,
        and application_status.json for permanent exclusion.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 1. Update Review Queue
        queue = self.load_review_queue()
        for item in queue:
            if item.get("job_id") == job_id:
                item["status"] = "APPLIED"
                item["applied_at"] = now_iso
                item["application_id"] = application_id
                item["confirmation_message"] = confirmation_msg
                item["screenshot_path"] = screenshot_path

        self.save_review_queue(queue)

        # 2. Update data/applications.json
        history = self.load_application_history()
        app_record = {
            "application_id": application_id,
            "job_id": job_id,
            "application_url": app_url,
            "submitted_at": now_iso,
            "status": "APPLIED",
            "resume_used": resume_used,
            "portfolio_used": portfolio_used,
            "answers": answers,
            "confirmation": confirmation_msg or "Application received",
            "screenshot_path": screenshot_path,
            "submission_verified": True
        }
        history.append(app_record)
        with open(APPLICATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        # 3. Permanently Sync Status in data/application_status.json
        try:
            status_data = {}
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    status_data = json.load(f)
            
            status_data[job_id] = {
                "status": "Applied",
                "is_active": False,
                "applied_at": now_iso,
                "application_id": application_id
            }
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            print(f"[-] Error syncing application_status.json: {e}")

        return True
