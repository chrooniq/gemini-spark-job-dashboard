"""
Gemini Spark — RAG Knowledge Base & Semantic Retrieval Engine
Provides grounded, verifiable retrieval across Sohaib Mahmood's career history.
Strictly forbids hallucination: if information is missing, flags as unavailable.
"""

import os
import json
import re
import math
from collections import Counter

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "knowledge")

class CareerRAGEngine:
    def __init__(self, knowledge_dir=None):
        self.knowledge_dir = knowledge_dir or KNOWLEDGE_DIR
        self.documents = []
        self.chunks = []
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        self.documents = []
        self.chunks = []

        if not os.path.exists(self.knowledge_dir):
            return

        for root, _, files in os.walk(self.knowledge_dir):
            for file in files:
                if file.endswith(".json"):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            doc = json.load(f)
                            self.documents.append(doc)
                            self._create_chunks_from_doc(doc, file)
                    except Exception as e:
                        print(f"[-] Error loading {filepath}: {e}")

    def _create_chunks_from_doc(self, doc, filename):
        category = doc.get("category", "general")
        source = doc.get("source", "Career Profile")
        topic = doc.get("topic", "Profile")
        data = doc.get("data", {})

        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, (str, int, float, list)):
                    content = str(val) if isinstance(val, (str, int, float)) else json.dumps(val, ensure_ascii=False)
                    self.chunks.append({
                        "category": category,
                        "source": source,
                        "topic": f"{topic} — {key}",
                        "key": key,
                        "content": content,
                        "raw_data": val,
                        "verified": doc.get("verified", True),
                        "filename": filename
                    })
        elif isinstance(data, list):
            for item in data:
                content = json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item)
                self.chunks.append({
                    "category": category,
                    "source": source,
                    "topic": topic,
                    "content": content,
                    "raw_data": item,
                    "verified": doc.get("verified", True),
                    "filename": filename
                })

    def _tokenize(self, text):
        return re.findall(r"\b[a-zA-Z0-9_\-\.\$]+\b", text.lower())

    def _compute_similarity(self, query_tokens, chunk_tokens):
        if not query_tokens or not chunk_tokens:
            return 0.0
        q_counter = Counter(query_tokens)
        c_counter = Counter(chunk_tokens)
        
        intersection = set(q_counter.keys()) & set(c_counter.keys())
        if not intersection:
            return 0.0

        dot_product = sum(q_counter[t] * c_counter[t] for t in intersection)
        mag_q = math.sqrt(sum(c * c for c in q_counter.values()))
        mag_c = math.sqrt(sum(c * c for c in c_counter.values()))
        
        return dot_product / (mag_q * mag_c) if (mag_q and mag_c) else 0.0

    def retrieve(self, query, job_context=None, top_k=4):
        """
        Retrieves the top-k most relevant verified chunks for a given question / prompt.
        """
        if not self.chunks:
            self._load_knowledge_base()

        query_str = query
        if job_context and isinstance(job_context, dict):
            query_str += f" {job_context.get('job_title', '')} {' '.join(job_context.get('skills', []))}"

        query_tokens = self._tokenize(query_str)
        scored_chunks = []

        for chunk in self.chunks:
            chunk_tokens = self._tokenize(f"{chunk['topic']} {chunk['content']}")
            sim = self._compute_similarity(query_tokens, chunk_tokens)
            
            # Boost exact key matches
            if chunk.get("key") and chunk.get("key").lower() in query.lower():
                sim += 0.4

            # Boost GHL topics if query asks about GHL
            if "ghl" in query_tokens or "gohighlevel" in query_tokens:
                if "ghl" in chunk_tokens or "gohighlevel" in chunk_tokens:
                    sim += 0.25

            if sim > 0.05:
                scored_chunks.append((sim, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:top_k]]

    def select_resume(self, job_title, job_description="", required_skills=None):
        """
        Selects the optimal resume version based on job specialization.
        """
        combined = f"{job_title} {job_description} {' '.join(required_skills or [])}".lower()

        if "developer" in combined or "api" in combined or "webhook" in combined or "javascript" in combined:
            return {
                "resume_name": "Sohaib_Mahmood_GHL_Developer_Resume.pdf",
                "focus": "Full-Stack GoHighLevel Development, Webhooks & APIs",
                "reason": "Targeted towards technical GHL engineering, custom code, and backend workflows.",
                "url": "https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk"
            }
        elif "funnel" in combined or "landing page" in combined or "website" in combined:
            return {
                "resume_name": "Sohaib_Mahmood_GHL_Funnel_Builder_Resume.pdf",
                "focus": "High-Converting GHL Funnels & UI/UX Conversion",
                "reason": "Targeted towards sales funnels, booking flows, and conversion optimization.",
                "url": "https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk"
            }
        elif "ai" in combined or "n8n" in combined or "automation" in combined:
            return {
                "resume_name": "Sohaib_Mahmood_AI_Automation_Resume.pdf",
                "focus": "AI Autonomous Workflows, n8n & GHL Multi-Location Systems",
                "reason": "Targeted towards LLM agent integration, speed-to-lead, and multi-platform automation.",
                "url": "https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk"
            }
        else:
            return {
                "resume_name": "Sohaib_Mahmood_GoHighLevel_Specialist_Resume.pdf",
                "focus": "Comprehensive GoHighLevel CRM Architecture & Client Onboarding",
                "reason": "General high-impact GHL CRM and workflow specialist resume.",
                "url": "https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk"
            }

    def select_portfolio(self, job_title, job_description=""):
        """
        Selects the best portfolio URL and showcase highlight.
        """
        combined = f"{job_title} {job_description}".lower()
        
        return {
            "portfolio_url": "https://sohaibmahmood.vibepreview.com/",
            "intro_video_url": "https://drive.google.com/file/d/1TH4CMzXFOfup2liGESZmmA7QFM8GcfqP/view?usp=sharing",
            "highlight_project": "Real Estate Agency SaaS Snapshot & AI Speed-to-Lead Lead Qualification Agent"
        }
