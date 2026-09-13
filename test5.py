import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class LeadDataCollector:
    """Collects incoming lead data (form submissions & website behavior)."""
    
    @staticmethod
    def get_synthetic_training_data(n_samples=1000):
        """Generates mock dataset representing historical lead behavior."""
        np.random.seed(42)
        
        data = {
            "email": [f"user{i}@" + np.random.choice(["company.com", "gmail.com", "tempmail.org", "disposable.net", "bot-domain.ru"]) for i in range(n_samples)],
            "form_submission_time_sec": np.random.uniform(1.0, 180.0, n_samples),
            "message_length": np.random.randint(0, 500, n_samples),
            "time_on_site_mins": np.random.uniform(0.1, 45.0, n_samples),
            "pages_visited": np.random.randint(1, 25, n_samples),
            "pricing_page_visits": np.random.randint(0, 8, n_samples),
            "stated_budget": np.random.choice([0, 500, 2500, 10000, 50000], n_samples),
            "job_title_provided": np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
            "requested_demo": np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        }
        df = pd.DataFrame(data)
        
        score = (
            (df['time_on_site_mins'] > 5).astype(int) * 2 +
            (df['pricing_page_visits'] > 1).astype(int) * 2 +
            (df['stated_budget'] >= 2500).astype(int) * 3 +
            (df['requested_demo'] == 1).astype(int) * 3 -
            (df['email'].str.contains("tempmail|disposable|bot-domain")).astype(int) * 10
        )
        df['is_genuine'] = (score >= 4).astype(int)
        return df


class SpamJunkFilter:
    """Hard-filtering checks before sending leads to the AI model."""
    
    DISPOSABLE_DOMAINS = ["tempmail.org", "disposable.net", "guerrillamail.com", "trashmail.com", "bot-domain.ru"]
    SPAM_KEYWORDS = ["crypto", "casino", "seo service", "buy followers", "fast loan"]
    
    @classmethod
    def evaluate_junk(cls, lead: dict) -> tuple[bool, str]:
        email = lead.get("email", "").lower()
        domain = email.split("@")[-1] if "@" in email else ""
        form_time = lead.get("form_submission_time_sec", 0)
        message = lead.get("message", "").lower()

        if domain in cls.DISPOSABLE_DOMAINS:
            return True, "JUNK: Disposable/Bot Email Domain Detected"
            
        if form_time < 3.0:
            return True, "JUNK: Bot Activity (Form filled under 3 seconds)"
            
        if any(keyword in message for keyword in cls.SPAM_KEYWORDS):
            return True, "JUNK: Spam Keywords Detected in Message"

        return False, "CLEAN"


class AILeadScorer:
    """Trains on patterns, calculates lead scores, and makes final decisions."""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_cols = [
            "form_submission_time_sec", "message_length", "time_on_site_mins",
            "pages_visited", "pricing_page_visits", "email_is_business",
            "stated_budget", "job_title_provided", "requested_demo"
        ]

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts engineered signals from raw metrics."""
        df_feats = df.copy()
        
        free_providers = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        df_feats["email_domain"] = df_feats["email"].apply(lambda x: x.split("@")[-1] if "@" in x else "")
        df_feats["email_is_business"] = (~df_feats["email_domain"].isin(free_providers)).astype(int)
        
        return df_feats[self.feature_cols]

    def train(self, raw_data: pd.DataFrame):
        X = self._engineer_features(raw_data)
        y = raw_data["is_genuine"]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        print(">> AI Lead Detection Model successfully trained.")

    def process_and_score(self, lead_data: dict) -> dict:
        """Evaluates clean leads through Spam Filter -> Signal Processing -> AI Lead Scoring."""
        
        is_junk, junk_reason = SpamJunkFilter.evaluate_junk(lead_data)
        if is_junk:
            return {
                "email": lead_data.get("email"),
                "status": "FILTERED OUT",
                "lead_score": 0,
                "verdict": "SPAM / JUNK",
                "reason": junk_reason
            }

        df_single = pd.DataFrame([lead_data])
        X_single = self._engineer_features(df_single)
        X_scaled = self.scaler.transform(X_single)
        
        conversion_prob = self.model.predict_proba(X_scaled)[0][1]
        lead_score = int(round(conversion_prob * 100))

        if lead_score >= 70:
            verdict = "GENUINE CUSTOMER (High Intent)"
        elif lead_score >= 40:
            verdict = "POTENTIAL CUSTOMER (Needs Nurturing)"
        else:
            verdict = "TIME WASTER (Low Engagement)"

        return {
            "email": lead_data.get("email"),
            "status": "PROCESSED",
            "lead_score": lead_score,
            "verdict": verdict,
            "reason": f"Signal checks completed with a score of {lead_score}/100"
        }


def collect_lead_input_from_user() -> dict:
    """Helper function to collect live data inputs from the console."""
    print("\n--- Enter New Lead Information ---")
    email = input("Email address: ").strip()
    
    while True:
        try:
            form_time = float(input("Form submission time in seconds (e.g., 45.0): "))
            break
        except ValueError:
            print("Invalid input. Please enter a numerical value.")
            
    message = input("Message text: ").strip()
    message_length = len(message)
    
    while True:
        try:
            time_on_site = float(input("Time on site in minutes (e.g., 12.5): "))
            pages_visited = int(input("Total pages visited: "))
            pricing_visits = int(input("Pricing page visits: "))
            budget = float(input("Stated budget ($): "))
            break
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    job_title = input("Was a job title provided? (yes/no): ").strip().lower()
    job_title_provided = 1 if job_title in ['yes', 'y', '1'] else 0

    demo = input("Requested a demo? (yes/no): ").strip().lower()
    requested_demo = 1 if demo in ['yes', 'y', '1'] else 0

    return {
        "email": email,
        "form_submission_time_sec": form_time,
        "message": message,
        "message_length": message_length,
        "time_on_site_mins": time_on_site,
        "pages_visited": pages_visited,
        "pricing_page_visits": pricing_visits,
        "stated_budget": budget,
        "job_title_provided": job_title_provided,
        "requested_demo": requested_demo
    }


if __name__ == "__main__":
    collector = LeadDataCollector()
    training_data = collector.get_synthetic_training_data(1000)
    
    ai_system = AILeadScorer()
    ai_system.train(training_data)

    print("\nReal-time lead scoring system is running.")
    
    while True:
        lead = collect_lead_input_from_user()
        
        result = ai_system.process_and_score(lead)
        
        print("\n" + "="*60)
        print("INCOMING LEAD DETECTION RESULTS")
        print("="*60)
        print(f"Lead Email:  {result['email']}")
        print(f"Status:      {result['status']}")
        print(f"Score:       {result['lead_score']}/100")
        print(f"Verdict:     {result['verdict']}")
        print(f"Details:     {result['reason']}")
        print("="*60)
        
        cont = input("\nWould you like to score another lead? (yes/no): ").strip().lower()
        if cont not in ['yes', 'y']:
            print("Exiting real-time lead scorer. Goodbye!")
            break