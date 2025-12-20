
import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

def find_buyer_in_sheet():
    print("Connecting to Google Sheets...")
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', './credentials/google-sheets-credentials.json')
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    
    sheet_id = os.getenv('TRANSACTIONS_SPREADSHEET_ID')
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.get_worksheet(0)
    
    # Buyer email is in column 10 (K - 'Реквизиты покупателя')? Or 11?
    # Headers: ['Клиент', ..., 'Сумма платежа. $', 'Платежная система', 'Реквизиты покупателя', ...]
    # Let's search all columns
    
    print("Fetching ALL values...")
    all_values = worksheet.get_all_values()
    
    target = "shotnytjayy" # Typo in user request? "shotbytjayy"
    target1 = "shotbytjayy"
    
    found = False
    for i, row in enumerate(all_values):
        row_str = " ".join(row).lower()
        if target1 in row_str or "shot" in row_str:
            print(f"Row {i+1} Match: {row}")
            found = True
            
    if not found:
        print("No matches for 'shotbytjayy'")

if __name__ == "__main__":
    find_buyer_in_sheet()
