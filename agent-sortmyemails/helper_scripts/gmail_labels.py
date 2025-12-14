def create_label(service, label_name):
    label_body = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }

    try:
        response = service.users().labels().create(userId='me', body=label_body).execute()
        return response["id"]
    except Exception as e:
        # Handle "already exists" or conflict errors (HTTP 409)
        if hasattr(e, 'resp') and e.resp.status == 409:
            print(f"Label '{label_name}' already exists — retrieving ID...")
            labels = service.users().labels().list(userId='me').execute().get("labels", [])
            existing = next((l for l in labels if l["name"] == label_name), None)
            if existing:
                return existing["id"]
        print(f"Label '{label_name}' failed: {e}")
        return None


def apply_label(service, message_id, label_id):
    return service.users().messages().modify(
        userId='me',
        id=message_id,
        body={"addLabelIds": [label_id]}
    ).execute()

def ensure_tracking_label(service, label_name="AI-Sorted"):
    return create_label(service, label_name)

def create_filter_for_sender(service, sender_email, label_id):
    """
    Creates a Gmail filter that applies the given label to all future emails from sender_email.
    """
    filter_content = {
        'criteria': {
            'from': sender_email
        },
        'action': {
            'addLabelIds': [label_id],
            'removeLabelIds': ['INBOX'] 
        }
    }
    
    try:
        service.users().settings().filters().create(userId='me', body=filter_content).execute()
        print(f"✅ Filter created for {sender_email} -> Label ID: {label_id}")
    except Exception as e:
        # Ignore if filter already exists or similar harmless errors?
        # A common error is "Filter limit reached" or similar.
        print(f"⚠️ Could not create filter for {sender_email}: {e}")
