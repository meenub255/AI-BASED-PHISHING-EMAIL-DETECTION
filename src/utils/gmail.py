import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Dict, Any

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"Please provide '{credentials_path}' from Google Cloud Console. "
                        "Follow the instructions in implementation_plan.md."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_latest_emails(self, max_results=5, labels=['INBOX', 'SPAM']) -> List[Dict[str, Any]]:
        """Fetch the latest messages from specified labels using OR logic."""
        try:
            query = " OR ".join([f"label:{label.lower()}" for label in labels]) if labels else ""
            results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])

            email_data_list = []
            for msg in messages:
                msg_full = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                payload = msg_full.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
                
                # Get Body
                body = ""
                if 'data' in payload.get('body', {}):
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                elif 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                
                email_data_list.append({
                    "id": msg['id'],
                    "subject": subject,
                    "from": sender,
                    "body_text": body,
                    "headers": f"Subject: {subject}\nFrom: {sender}"
                })
            
            return email_data_list

        except Exception as error:
            print(f"An error occurred: {error}")
            return []

if __name__ == "__main__":
    # Test connection
    try:
        gmail = GmailService()
        print("Listing available labels:")
        labels_results = gmail.service.users().labels().list(userId='me').execute()
        for label in labels_results.get('labels', []):
            print(f"- {label['name']} (ID: {label['id']})")
            
        emails = gmail.get_latest_emails(max_results=5, labels=None)
        if emails:
            print(f"Connection Successful! Found {len(emails)} emails.")
            for e in emails:
                print(f"- {e['subject']} (ID: {e['id']})")
        else:
            print("Connected, but no emails found in INBOX or SPAM.")
    except Exception as e:
        print(f"Setup Error: {e}")
