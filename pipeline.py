import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv
from email_fetcher import fetch_unread_emails

# Import your existing modules
from google import genai
from google.genai import types
from test5 import LeadDataCollector, AILeadScorer

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 1. Initialize Gemini Client
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logging.warning("GOOGLE_API_KEY not found in environment variables.")

client = genai.Client(api_key=api_key) if api_key else None

# Train the lead scorer once when the pipeline module is loaded.
logging.info("Training ML lead scorer...")
ml_collector = LeadDataCollector()
ml_scorer = AILeadScorer()
ml_scorer.train(ml_collector.get_synthetic_training_data(1000))


def score_lead(email_content: str, sender: str, ai_data: dict) -> dict:
    """Convert the email and extracted details into the scorer's input format."""
    stated_budget = extract_numeric_budget(ai_data.get("estimated_budget", ""))
    domain = sender.rsplit("@", 1)[-1].split(">", 1)[0].strip() if "@" in sender else ""
    email_address = f"lead@{domain}" if domain else "unknown@example.com"

    return ml_scorer.process_and_score({
        "email": email_address,
        "form_submission_time_sec": 30.0,
        "message": email_content,
        "message_length": len(email_content),
        "time_on_site_mins": 5.0,
        "pages_visited": 1,
        "pricing_page_visits": 0,
        "stated_budget": stated_budget,
        "job_title_provided": 0,
        "requested_demo": int(ai_data.get("client_intent") == "Consultation"),
    })

def analyze_with_ai(email_text: str) -> dict:
    """Uses Gemini to extract structured business details from client inquiry."""
    if not client:
        return {"error": "Gemini Client not initialized"}

    prompt = f"""
    Analyze the following client inquiry email and extract key details into valid JSON format.
    Fields required:
    - client_name: (string or "Unknown")
    - company_name: (string or "Unknown")
    - project_summary: (brief 1-2 sentence description)
    - estimated_budget: (string or "Not Specified")
    - timeline_urgency: ("High", "Medium", or "Low")
    - client_intent: ("New Project", "Consultation", "Support", or "Other")
    - suggested_reply: (A polite, professional draft email response directly addressing the client by name, acknowledging their specific details, and proposing next steps.)

    Client Email:
    \"\"\"{email_text}\"\"\"

    Return ONLY the raw JSON object. Do not include markdown codeblocks or backticks.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        clean_text = (response.text or "").strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        logging.error(f"Error during AI analysis: {e}")
        return {
            "project_summary": email_text[:120],
            "client_intent": "General Inquiry",
            "timeline_urgency": "Medium",
            "estimated_budget": "Not Specified",
            "suggested_reply": "Thank you for your inquiry. We have received your request and will review the details before getting back to you with next steps.",
            "error": str(e)
        }

def extract_nlp_requirements(text: str) -> dict[str, list[str]]:
    """Extracts project requirements using spaCy rule matching."""
    try:
        import spacy
        from spacy.matcher import Matcher

        nlp = spacy.load("en_core_web_sm")
        matcher = Matcher(nlp.vocab)

        # Pattern for modal verbs expressing requirements
        pattern = [
            {"POS": {"IN": ["NOUN", "PRON"]}},
            {"LEMMA": {"IN": ["need", "must", "should", "require", "want"]}},
            {"POS": "VERB", "OP": "+"}
        ]
        matcher.add("REQUIREMENT_PATTERN", [pattern])

        doc = nlp(text)
        matches = matcher(doc)

        requirements = []
        for match_id, start, end in matches:
            span = doc[start:end]
            requirements.append(span.text)

        # Also extract potential technology stack mentions (proper nouns)
        tech_tags = list(set([token.text for token in doc if token.pos_ == "PROPN"]))

        return {
            "requirements": requirements if requirements else ["Review complete project scope"],
            "detected_technologies": tech_tags
        }
    except Exception as e:
        logging.warning(f"spaCy extraction skipped or failed: {e}")
        return {"requirements": [], "detected_technologies": []}


def extract_numeric_budget(budget_str: str) -> int:
    """Convert a budget string such as '$8,000' into an integer."""
    if not budget_str or budget_str == "Not Specified":
        return 0

    numeric_str = "".join(filter(str.isdigit, budget_str))
    return int(numeric_str) if numeric_str else 0


def run_pipeline(email_content: Optional[str] = None) -> dict:
    """Combines email fetching, Gemini AI, and spaCy into a structured lead."""
    sender_info = "Direct Input"

    # Fetch the newest unread email when no manual text is provided.
    if not email_content:
        logging.info("Checking for unread emails via email_fetcher...")
        try:
            unread_emails = fetch_unread_emails()

            if unread_emails:
                latest_email = unread_emails[0]
                sender_info = latest_email.get("sender", "Unknown")
                email_content = (
                    f"From: {sender_info}\n"
                    f"Subject: {latest_email.get('subject')}\n\n"
                    f"{latest_email.get('body')}"
                )
                logging.info("Fetched new email from %s", sender_info)
            else:
                logging.info("No unread emails found in inbox. Using sample inquiry.")
                email_content = (
                    "Hi Team, We need a full-stack automated CRM dashboard built using React and Flask. "
                    "Our budget is around $8,000 and we must complete this within 4 weeks. "
                    "Please let us know your availability. Best, John Doe from Apex Corp."
                )
        except Exception as e:
            logging.error("Email fetching error: %s", e)
            email_content = (
                "Hi Team, We need a full-stack automated CRM dashboard built using React and Flask. "
                "Our budget is around $8,000 and we must complete this within 4 weeks. "
                "Please let us know your availability. Best, John Doe from Apex Corp."
            )

    logging.info("Starting AI Analysis...")
    ai_data = analyze_with_ai(email_content)

    logging.info("Starting Requirement Extraction...")
    nlp_data = extract_nlp_requirements(email_content)

    # Map the email data to the ML model's expected format.
    budget_val = extract_numeric_budget(ai_data.get("estimated_budget", ""))
    ml_input = {
        "email": sender_info,
        "form_submission_time_sec": 120.0,
        "message": email_content,
        "message_length": len(email_content),
        "time_on_site_mins": 5.0,
        "pages_visited": 2,
        "pricing_page_visits": 1,
        "stated_budget": budget_val,
        "job_title_provided": int(ai_data.get("company_name", "Unknown") != "Unknown"),
        "requested_demo": int(
            "demo" in email_content.lower() or "call" in email_content.lower()
        ),
    }

    logging.info("Scoring lead with RandomForest ML model...")
    ml_result = ml_scorer.process_and_score(ml_input)

    lead_record = {
        "client_name": ai_data.get("client_name", "Unknown"),
        "company": ai_data.get("company_name", "Unknown"),
        "intent": ai_data.get("client_intent", "New Project"),
        "summary": ai_data.get("project_summary", ""),
        "budget": ai_data.get("estimated_budget", "Not Specified"),
        "urgency": ai_data.get("timeline_urgency", "Medium"),
        "suggested_reply": ai_data.get("suggested_reply", "Thank you for reaching out."),
        "requirements": nlp_data.get("requirements", []),
        "technologies": nlp_data.get("detected_technologies", []),
        "ml_score": ml_result.get("lead_score", 0),
        "ml_verdict": ml_result.get("verdict", "UNKNOWN"),
        "ml_reason": ml_result.get("reason", ""),
        "status": "New Lead",
        "raw_inquiry": email_content
    }

    logging.info("Pipeline completed successfully.")
    return lead_record

if __name__ == "__main__":
    result = run_pipeline()
    print("\n--- UNIFIED LEAD PROTOTYPE OUTPUT ---")
    print(json.dumps(result, indent=2))