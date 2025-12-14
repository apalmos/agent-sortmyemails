import base64
import email
from googleapiclient.discovery import build
import pickle

def gmail_authenticate():
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    return build('gmail', 'v1', credentials=creds)

def get_message_details(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = message['payload'].get('headers', [])
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
    sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")
    snippet = message.get('snippet', "")
    
    # Try to get body text
    body = ""
    payload = message['payload']
    parts = payload.get('parts', [])
    for part in parts:
        if part['mimeType'] == 'text/plain':
            body = base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8', errors='ignore')
            break
    return {"sender": sender, "subject": subject, "snippet": snippet, "body": body[:500]}

def fetch_recent_emails(n=50, query=None):
    service = gmail_authenticate()
    result = service.users().messages().list(userId='me', maxResults=n, q=query).execute()
    messages = result.get('messages', [])
    
    emails = []
    for msg in messages:
        try:
            detail = get_message_details(service, msg['id'])
            detail["id"] = msg['id']  # ← IMPORTANT: needed for labeling
            emails.append(detail)
        except Exception as e:
            print(f"Failed to fetch message {msg['id']}: {e}")
    return emails


if __name__ == "__main__":
    emails = fetch_recent_emails(200)
    for i, email_data in enumerate(emails[:5]):  # Show first 5 as preview
        print(f"\nEmail {i+1}")
        print(f"From: {email_data['sender']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Snippet: {email_data['snippet']}")
