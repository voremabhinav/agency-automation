from enum import Enum
# Lead Status
class LeadStatus(Enum):
    NEW = "New"
    REMINDER = "Reminders"
    AI_EMAIL_REPLY = "AI - Email Replies"
    HR_REVIEW = "HR Review"
    APPROVED = "Approved"


# Lead class
class Lead:
    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message
        self.status = LeadStatus.NEW
        self.reminder = None

    # Display lead information
    def display_lead(self):
        print("\n----- Lead Details -----")
        print("Name    :", self.name)
        print("Email   :", self.email)
        print("Message :", self.message)
        print("Status  :", self.status.value)

    # Change lead status
    def update_status(self, new_status):
        self.status = new_status
        print("\nStatus changed to:", self.status.value)

    # Add reminder
    def add_reminder(self, reminder):
        self.reminder = reminder
        self.update_status(LeadStatus.REMINDER)
        print("Reminder:", reminder)

    # AI email reply
    def ai_email_reply(self):
        self.update_status(LeadStatus.AI_EMAIL_REPLY)

        reply = f"""
Hello {self.name},

Thank you for contacting us.

We have received your requirements:
"{self.message}"

Our team will review your requirements and get back to you.

Regards,
HR Team
"""

        print("\n----- AI Email Reply -----")
        print(reply)

    # HR review
    def hr_review(self, approved):
        self.update_status(LeadStatus.HR_REVIEW)

        if approved:
            self.update_status(LeadStatus.APPROVED)
            print("HR Review: Lead Approved")
        else:
            print("HR Review: More information is required.")


# ---------------------------------
# Main Program
# ---------------------------------

# Create a new lead
lead = Lead(
    "Rahul",
    "rahul@gmail.com",
    "I need a website for my business."
)

# 1. New Lead
lead.display_lead()

# 2. Reminder
lead.add_reminder("Follow up after 24 hours")

# 3. AI Email Reply
lead.ai_email_reply()

# 4. HR Review
lead.hr_review(approved=True)

# Final status
lead.display_lead()
