from helper_scripts.categorize import categorize_emails_with_gpt, parse_categorization_output
from helper_scripts.fetch_emails import fetch_recent_emails, gmail_authenticate
from helper_scripts.gmail_labels import create_label, apply_label, ensure_tracking_label, create_filter_for_sender
from datetime import datetime, timedelta
import re

def extract_email_address(sender_str):
    # Extracts "email@example.com" from "Name <email@example.com>"
    match = re.search(r'<([^>]+)>', sender_str)
    if match:
        return match.group(1)
    # Fallback if no brackets
    return sender_str.strip()

def get_or_create_labels(service, label_names):
    label_ids = {}
    existing_labels = service.users().labels().list(userId='me').execute().get("labels", [])
    existing_map = {label['name']: label['id'] for label in existing_labels}

    for name in label_names:
        if name in existing_map:
            label_ids[name] = existing_map[name]
        else:
            label_id = create_label(service, name)
            if label_id:
                label_ids[name] = label_id
    return label_ids

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

if __name__ == "__main__":
    # Fetch emails from the last 7 days, excluding ones already labeled "AI-Sorted"
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d")
    print("Fetching recent emails...")
    emails = fetch_recent_emails(n=50, query=f"after:{last_week} -label:AI-Sorted")
    
    if not emails:
        print("✅ No new emails to process.")
        exit()

    batches = list(chunk_list(emails, 50))
    service = gmail_authenticate()
    tracking_label_id = ensure_tracking_label(service)

    for batch_index, batch in enumerate(batches, 1):
        print(f"\n📦 Processing batch {batch_index}/{len(batches)} (emails {len(batch)})")
        
        # 1. Ask GPT to categorize
        categorized_output = categorize_emails_with_gpt(batch)
        label_map = parse_categorization_output(categorized_output)
        
        # 2. Get/Create all labels mentioned by GPT
        needed_labels = list(label_map.keys())
        label_id_map = get_or_create_labels(service, needed_labels)

        # 3. Apply labels and create filters
        for label_name, email_indexes in label_map.items():
            if label_name not in label_id_map:
                continue
                
            label_id = label_id_map[label_name]
            
            for i in email_indexes:
                if 0 <= i < len(batch):
                    email_data = batch[i]
                    msg_id = email_data.get("id")
                    
                    # Apply label to current email
                    apply_label(service, msg_id, label_id)
                    apply_label(service, msg_id, tracking_label_id)  # mark as processed
                    
                    # Create filter for future emails from this sender
                    sender_clean = extract_email_address(email_data.get("sender", ""))
                    if sender_clean:
                        create_filter_for_sender(service, sender_clean, label_id)
