"""
One-time Google OAuth2 setup script.

Run this once from your local machine to get a refresh token that the
HR Recruiter Agent will use to access Gmail, Google Drive, and Calendar.

Usage:
  1. Complete the Google Cloud setup steps in SETUP_GUIDE.md
  2. Download your OAuth credentials JSON from Google Cloud Console
  3. Run:  python setup/google_auth.py --credentials path/to/credentials.json
  4. A browser window will open — log in with your HR Google account
  5. Copy the three values printed at the end into app/HRRecruiterAgent/.env

Requirements:
  pip install google-auth-oauthlib
"""
import argparse
import json
import os
import sys


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]


def main():
    parser = argparse.ArgumentParser(description="Get Google OAuth2 refresh token for HR Agent")
    parser.add_argument(
        "--credentials",
        default="credentials.json",
        help="Path to the OAuth2 credentials JSON downloaded from Google Cloud Console",
    )
    args = parser.parse_args()

    if not os.path.exists(args.credentials):
        print(f"\nError: credentials file not found at '{args.credentials}'")
        print("\nTo get credentials.json:")
        print("  1. Go to https://console.cloud.google.com/apis/credentials")
        print("  2. Click 'Create Credentials' → 'OAuth client ID'")
        print("  3. Application type: Desktop app")
        print("  4. Download the JSON file")
        print(f"  5. Save it as '{args.credentials}' and re-run this script\n")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
    except ImportError:
        print("\nError: google-auth-oauthlib not installed.")
        print("Run:  pip install google-auth-oauthlib\n")
        sys.exit(1)

    print("\nStarting Google OAuth2 flow...")
    print("A browser window will open. Log in with the Google account the HR Agent should use.")
    print("(This is a one-time step — the refresh token does not expire unless revoked.)\n")

    flow = InstalledAppFlow.from_client_secrets_file(args.credentials, scopes=SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    # Load client id/secret from the credentials file
    with open(args.credentials) as f:
        cred_data = json.load(f)
    client_info = cred_data.get("installed") or cred_data.get("web", {})
    client_id = client_info.get("client_id", "")
    client_secret = client_info.get("client_secret", "")
    refresh_token = creds.refresh_token

    if not refresh_token:
        print("\nWarning: No refresh token returned.")
        print("This can happen if you already authorized this app.")
        print("Go to https://myaccount.google.com/permissions, revoke access, and re-run.\n")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("SUCCESS — Add these three lines to app/HRRecruiterAgent/.env")
    print("=" * 60)
    print(f"GOOGLE_CLIENT_ID={client_id}")
    print(f"GOOGLE_CLIENT_SECRET={client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
    print("=" * 60)
    print("\nAlso save these to agentcore/.env.local for deployed environments.\n")


if __name__ == "__main__":
    main()
