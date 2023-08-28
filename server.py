from fastapi import FastAPI, HTTPException
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
import os

load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
REDIRECT_URI = os.environ.get('REDIRECT_URI')

app = FastAPI()

@app.get("/save_creds/")
async def process_code(code: str):
    print(code)
    print(REDIRECT_URI)
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES,
                redirect_uri=REDIRECT_URI)
    flow.fetch_token(code=code)
    creds = flow.credentials
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    return "Request completed. You can close this window."

