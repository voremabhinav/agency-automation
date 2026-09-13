import os
import json
import logging
from dotenv import load_dotenv

# Import your existing modules
from google import genai
from google.genai import types

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 1. Initialize Gemini Client
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logging.warning("GOOGLE_API_KEY not found in environment variables.")

client = genai.Client(api_key=api_key) if api_key else None

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

    Client Email:
    \"\"\"{email_text}\"\"\"

    Return ONLY the raw JSON object. Do not include markdown codeblocks or backticks.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt,
        )
        clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        logging.error(f"Error during AI analysis: {e}")
        return {
            "project_summary": email_text[:120],
            "client_intent": "General Inquiry",
            "timeline_urgency": "Medium",
            "estimated_budget": "Not Specified",
            "error": str(e)
        }

def extract_nlp_requirements(text: str) -> list:
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

def run_pipeline(email_content: str = None) -> dict:
    """
    Main controller:
    Takes an email text (or fetches the latest), runs AI analysis,
    extracts requirements, and compiles a unified lead object.
    """
    # 1. Fetch Email Content
    if not email_content:
        logging.info("No text provided. Attempting to fetch email via email_fetcher...")
        try:
            from email_fetcher import fetch_latest_email
            email_content = fetch_latest_email()
        except Exception as e:
            logging.info("Falling back to sample client inquiry for testing.")
            email_content = (
                "Hi Team, We need a full-stack automated CRM dashboard built using React and Flask. "
                "Our budget is around $8,000 and we must complete this within 4 weeks. "
                "Please let us know your availability. Best, John Doe from Apex Corp."
            )

    logging.info("Starting AI Analysis...")
    ai_data = analyze_with_ai(email_content)

    logging.info("Starting Requirement Extraction...")
    nlp_data = extract_nlp_requirements(email_content)

    # 3. Combine into unified Lead Record
    lead_record = {
        "client_name": ai_data.get("client_name", "Unknown"),
        "company": ai_data.get("company_name", "Unknown"),
        "intent": ai_data.get("client_intent", "New Project"),
        "summary": ai_data.get("project_summary", ""),
        "budget": ai_data.get("estimated_budget", "Not Specified"),
        "urgency": ai_data.get("timeline_urgency", "Medium"),
        "requirements": nlp_data.get("requirements", []),
        "technologies": nlp_data.get("detected_technologies", []),
        "status": "New Lead",
        "raw_inquiry": email_content
    }

    logging.info("Pipeline completed successfully.")
    return lead_record

if __name__ == "__main__":
    result = run_pipeline()
    print("\n--- UNIFIED LEAD PROTOTYPE OUTPUT ---")
    print(json.dumps(result, indent=2))