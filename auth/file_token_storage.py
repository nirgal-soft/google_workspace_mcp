# auth/file_token_storage.py

import os
import json
import logging
from typing import Optional
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

TOKEN_STORAGE_DIR = "/tmp/mcp-tokens"

def load_credentials_from_file_storage(session_id: str) -> Optional[Credentials]:
    """Load credentials from file storage based on session ID"""
    try:
        token_file = os.path.join(TOKEN_STORAGE_DIR, f"{session_id}.json")
        print(f"[FILE_STORAGE] Looking for token file: {token_file}")
        
        if not os.path.exists(token_file):
            print(f"[FILE_STORAGE] No token file found for session: {session_id}")
            logger.debug(f"No token file found for session: {session_id}")
            return None
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        # Create credentials object
        credentials = Credentials(
            token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=token_data.get('scopes', [])
        )
        
        print(f"[FILE_STORAGE] SUCCESS: Loaded credentials from file for session: {session_id}, user: {token_data.get('email')}")
        logger.info(f"Loaded credentials from file for session: {session_id}, user: {token_data.get('email')}")
        return credentials
        
    except Exception as e:
        logger.error(f"Error loading credentials from file for session {session_id}: {e}")
        return None

def save_credentials_to_file_storage(session_id: str, user_email: str, credentials: Credentials):
    """Save credentials to file storage"""
    try:
        os.makedirs(TOKEN_STORAGE_DIR, exist_ok=True)
        
        token_data = {
            "user_id": f"user-{session_id}",
            "email": user_email,
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": credentials.expiry.isoformat() if credentials.expiry else None,
            "scopes": credentials.scopes or []
        }
        
        token_file = os.path.join(TOKEN_STORAGE_DIR, f"{session_id}.json")
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        logger.info(f"Saved credentials to file for session: {session_id}, user: {user_email}")
        
    except Exception as e:
        logger.error(f"Error saving credentials to file for session {session_id}: {e}")