import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROMPT = """
Generi:
- un modo di dire con esempi
- una traccia del giorno. La risposta deve essere 160-180 parole e addattato per il C1 CILS esame

Send it in the following format and all formatting should be email compatible:

Modo di dire: [insert here]

Significato: [insert here]

Esempi:
- [insert here]
- [insert here]

------------------------------

Traccia del Giorno

[insert here]

"""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=800,
    messages=[
        {"role": "user", "content": PROMPT}
    ]
)

content = response.content[0].text

subject = f"Daily Italian - {datetime.now().strftime('%Y-%m-%d')}"

msg = MIMEText(content)
msg["Subject"] = subject
msg["From"] = os.getenv("EMAIL_USER")
msg["To"] = os.getenv("EMAIL_TO")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(
        os.getenv("EMAIL_USER"),
        os.getenv("EMAIL_PASS")
    )
    server.send_message(msg)

print("Email sent.")