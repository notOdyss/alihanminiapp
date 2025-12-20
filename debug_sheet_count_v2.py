
import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

def count_in_sheet():
    print("Connecting to Google Sheets...")
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', './credentials/google-sheets-credentials.json')
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    
    sheet_id = os.getenv('TRANSACTIONS_SPREADSHEET_ID')
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.get_worksheet(0)
    
    print("Fetching ALL values (this might take a moment)...")
    all_values = worksheet.get_all_values()
    
    print(f"Total Rows in Sheet: {len(all_values)}")
    
    target = "thxfortheslapali"
    count_exact = 0
    count_partial = 0
    matches = []
    
    for i, row in enumerate(all_values):
        # Username is usually in column 0 (A)
        username = row[0].strip() if row else ""
        
        if target.lower() == username.lower().replace('@', ''):
            count_exact += 1
            matches.append(f"Row {i+1}: {username} (Exact)")
            
        elif target.lower() in username.lower():
            count_partial += 1
            matches.append(f"Row {i+1}: {username} (Partial)")
            
    print(f"\n--- RESULTS FOR '{target}' ---")
    print(f"Exact Matches found: {count_exact}")
    print(f"Partial Matches found: {count_partial}")
    print(f"Total Matches: {count_exact + count_partial}")
    
    print("\n--- SAMPLE MATCHES ---")
    for m in matches[:10]:
        print(m)
        
    print("\n--- COMPARISON ---")
    print("Database has: 10")
    print(f"Sheet has: {count_exact + count_partial}")

if __name__ == "__main__":
    count_in_sheet()
