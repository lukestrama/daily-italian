import os
import smtplib
import json
from email.mime.text import MIMEText
from datetime import datetime
from anthropic import Anthropic
import re
import json
# from dotenv import load_dotenv

# load_dotenv()

# --- Load history ---
if os.path.exists("history.json"):
    with open("history.json", "r") as f:
        history = json.load(f)
else:
    history = {"modi": [], "topics": []}

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROMPT = f"""
Generate:

1. ONE Italian "modo di dire"
2. ONE writing prompt (traccia)

Rules:
- MUST be different from anything in this list
- Avoid similar meanings or close variants
- Prefer less common expressions
- everything must be italian

Previous modi:
{history['modi']}

Previous topics:
{history['topics']}

Return ONLY valid JSON:
{{
"modo": "",
"meaning": "",
"example": "",
"topic": ""
}}
"""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=500,
    messages=[{"role": "user", "content": PROMPT}]
)

content = response.content[0].text
match = re.search(r"\{.*\}", content, re.DOTALL)
if not match:
    print("No JSON found:")
    print(content)
    raise ValueError("No JSON object found")

# --- Parse JSON safely ---
try:
    data = json.loads(match.group())
except json.JSONDecodeError:
    print("Failed to parse JSON. Raw output:")
    print(content)
    raise

# --- Email formatting ---
email_body = f"""
Modo di dire:
{data['modo']}

Significato:
{data['meaning']}

Esempio:
{data['example']}

---

Traccia:
{data['topic']}
"""

subject = f"Daily Italian - {datetime.now().strftime('%Y-%m-%d')}"

msg = MIMEText(email_body)
msg["Subject"] = subject
msg["From"] = os.getenv("EMAIL_USER")
msg["To"] = os.getenv("EMAIL_TO")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(
        os.getenv("EMAIL_USER"),
        os.getenv("EMAIL_PASS")
    )
    server.send_message(msg)

# --- Update history ---
if data["modo"] not in history["modi"]:
    history["modi"].append(data["modo"])

if data["topic"] not in history["topics"]:
    history["topics"].append(data["topic"])

# keep last 50
history["modi"] = history["modi"][-50:]
history["topics"] = history["topics"][-50:]

with open("history.json", "w") as f:
    json.dump(history, f, indent=2)

print("Email sent.")