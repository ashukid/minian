from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def connect_gcloud():
    # connect
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


def list_files():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        folder_ids = []
        file_ids = []

        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                folder_ids.append(item['id'])
                print(f"folder - {item['name']}")
            else:
                file_ids.append(item['id'])
                print(f"file - {item['name']}")

        print(f"Total folders {len(folder_ids)} - Total files {len(file_ids)}")
        return folder_ids, file_ids
