import json
import random
import uuid
from datetime import datetime, timedelta


def generate_random_emails(num_emails):
    base_date = datetime.now()
    subjects = [
        "Topical Seminar Series", "Call for Establishment of New Clubs",
        "Weekly Team Meeting", "Monthly Financial Overview", "Project Kickoff Meeting",
        "Annual Performance Review", "Budget Planning Session", "Quarterly Business Review",
        "Safety Training Session", "Technology Update Webinar",
        "Customer Feedback Analysis", "New Product Line Introduction",
        "Corporate Social Responsibility Update", "Sustainability Initiatives Planning",
        "Holiday Party Planning", "Employee Wellness Program"
    ]
    senders = [
        {"name": "SDS Academic Events", "address": "sdsacademics@cuhk.edu.cn"},
        {"name": "Clubs Union Department", "address": "clubsoffice@link.cuhk.edu.cn"},
        {"name": "Project Management Office", "address": "pmo@company.com"},
        {"name": "Finance Department", "address": "finance@company.com"},
        {"name": "HR Department", "address": "hr@company.com"},
        {"name": "Tech Support", "address": "techsupport@techcompany.com"},
        {"name": "Marketing Team", "address": "marketing@marketingsolutions.com"},
        {"name": "Product Development", "address": "productdev@innovate.com"}
    ]
    importance_levels = ["normal", "high", "low"]

    emails = []
    for _ in range(num_emails):
        random_subject = random.choice(subjects) + " - " + str(uuid.uuid4())  # Ensure unique subjects
        random_sender = random.choice(senders)
        random_importance = random.choice(importance_levels)
        random_date = (base_date - timedelta(days=random.randint(0, 365),
                                             seconds=random.randint(0, 86400))).isoformat() + 'Z'

        email = {
            "@odata.etag": f"W/\"{uuid.uuid4()}\"",
            "id": str(uuid.uuid4()),
            "sentDateTime": random_date,
            "subject": f"【{random_sender['name']}】 {random_subject}",
            "bodyPreview": "This is a randomly generated email body for testing purposes.",
            "importance": random_importance,
            "isRead": random.choice([True, False]),
            "sender": {
                "emailAddress": random_sender
            }
        }
        emails.append(email)

    return emails


# Generate 140000 random emails
random_emails = generate_random_emails(140000)

# Save to a JSON file
with open('random_emails.json', 'w', encoding='utf-8') as f:
    json.dump({"value": random_emails}, f, ensure_ascii=False, indent=4)

print("Generated 140,000 random emails with more diversity and saved to 'random_emails.json'.")