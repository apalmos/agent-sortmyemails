from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()  # Loads variables from .env into environment

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_categorization_output(output):
    label_map = {}  # label name → list of email indexes
    current_label = None

    for line in output.splitlines():
        if line.startswith("Category:"):
            current_label = line.replace("Category:", "").strip()
            label_map[current_label] = []
        elif line.startswith("Emails:"):
            numbers = re.findall(r'\d+', line)
            if current_label:
                label_map[current_label].extend([int(n)-1 for n in numbers])  # -1 for zero-index
    return label_map

def format_emails_for_prompt(emails, max_body_chars=300):
    formatted = ""
    for i, email_data in enumerate(emails):
        sender = email_data["sender"]
        subject = email_data["subject"]
        body = email_data["body"] or email_data["snippet"]
        body = body[:max_body_chars].replace("\n", " ").strip()
        formatted += f"{i+1}. From: {sender}\n   Subject: {subject}\n   Body: {body}\n\n"
    return formatted


def categorize_emails_with_gpt(emails):

    # if "OPENAI_API_KEY" not in os.environ:
    #     raise ValueError("You must set OPENAI_API_KEY in your environment.")

    email_text = format_emails_for_prompt(emails)

    prompt = f"""
You're an assistant that helps organize email inboxes.

Below is a list of 200 emails. Each has a sender, subject, and body preview.

Your task:
1. Create 10–15 useful folder categories to organize these emails
2. For each category:
    - Give a name
    - Short description
    - List the email numbers that belong to it (e.g., 1, 5, 9)

Email list:
{email_text}

Return only the final organized categories and email assignments in this format:

Category: [Name]
Description: [Short description]
Emails: [numbers separated by commas]

Repeat this for all categories.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
