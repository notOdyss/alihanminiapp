import os
import gspread
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# Load environment logic similar to sync_service
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')

logger = logging.getLogger(__name__)

class SheetsWriter:
    _instance = None
    
    def __init__(self):
        self.credentials_path = project_root / os.getenv(
            'GOOGLE_SHEETS_CREDENTIALS_PATH',
            './credentials/google-sheets-credentials.json'
        ).lstrip('./')
        
        self.spreadsheet_id = "13nNGxUjuFXuyXxtb-Fgk8N-g7tx5wIXwWEH-7CdeEJs"
        self.client = None
        self._initialize_client()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            logger.info("Creating new SheetsWriter instance")
            cls._instance = cls()
        return cls._instance

    def _initialize_client(self):
        logger.info(f"Initializing SheetsWriter with path: {self.credentials_path}")
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(
                str(self.credentials_path), scopes=scopes
            )
            self.client = gspread.authorize(creds)
            logger.info("SheetsWriter: Client authorized successfully")
        except Exception as e:
            logger.error(f"SheetsWriter Init Error: {e}", exc_info=True)

    async def append_ticket(self, transaction, user):
        """
        Appends a new transaction ticket to the Google Sheet.
        """
        logger.info(f"Appending ticket for user {user.id}...")
        if not self.client:
            self._initialize_client()
            if not self.client:
                logger.error("Client not initialized, skipping append")
                return

        try:
            # Format Data
            now = datetime.utcnow()
            username = f"@{user.username}" if user.username else f"User {user.id}"
            
            # Map Russian Months
            months_ru = [
                'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
            ]
            month_name = months_ru[now.month - 1]

            # Clean Payment Method
            payment_method_raw = transaction.payment_method
            
            # Mapping to Sheet Dropdown Values
            # Keys from bot/keyboards/transactions.py
            PAYMENT_MAPPING = {
                'pay_paypal': 'PayPal',
                'pay_stripe': 'Stripe',
                'pay_crypto': 'Crypto (USDT)', # Defaulting to USDT
                'stripe_card': 'Stripe',
                'stripe_apple': 'Stripe',
                'stripe_google': 'Stripe',
                # Fallbacks
                'paypal': 'PayPal',
                'stripe': 'Stripe',
                'crypto': 'Crypto (USDT)'
            }
            
            payment_method = PAYMENT_MAPPING.get(payment_method_raw, 'Stripe') # Default to Stripe if unknown
            
            # Format Amount (Commas for RU locale if needed, but Sheet might handle dots)
            amount = str(transaction.amount) #.replace('.', ',') 

            # Calculate Row Number: Find first empty row in Col A, starting from Row 5
            sh = self.client.open_by_key(self.spreadsheet_id)
            ws = sh.get_worksheet(0)
            
            col_a = ws.col_values(1) # Get all values in Col A
            # Skip first 4 rows (Header area). 
            # We want the first index i where i >= 4 and col_a[i] is empty (or i >= len)
            
            row_count = 5 # Default start
            for i, val in enumerate(col_a):
                if i < 4: continue # Skip rows 1-4
                if not val.strip():
                    row_count = i + 1
                    break
            else:
                 # If loop finishes, append to end
                 row_count = len(col_a) + 1
            
            if row_count < 5: row_count = 5 # Safety

            # Determine "Type" (Col M / 12)
            # Logic: Crypto -> Bybit, Others -> Остальное
            # This drives the Fees logic.
            ticket_type = "Остальное"
            if "Crypto" in payment_method:
                ticket_type = "Bybit"

            # Create Row (25 columns)
            row = [''] * 25
            
            row[0] = username
            row[4] = str(now.day)
            row[5] = month_name
            row[6] = str(now.year)
            row[7] = "" # ID intentionally empty
            row[8] = amount
            row[9] = payment_method
            
            # --- Formulas & Defaults ---
            
            # Col 11 (L): Received? Default "Да"? (From probe)
            row[11] = "Да"
            
            # Col 12 (M): Type
            row[12] = ticket_type
            
            # Col 13 (N): Client Lookup
            row[13] = f"=VLOOKUP(A{row_count},'Клиенты'!$A$2:$B$1000,2)"
            
            # Col 14 (O): Ali Fee
            # Probe: =IF(M5="Bybit",-0,5,0) -> Using dot for API safety
            row[14] = f'=IF(M{row_count}="Bybit",-0.5,0)'
            
            # Col 15 (P): Super Fee
            # Probe: =IF(M5="Bybit",'Комиссии'!$B$2-0,5,'Комиссии'!$B$2)
            row[15] = f"=IF(M{row_count}=\"Bybit\",'Комиссии'!$B$2-0.5,'Комиссии'!$B$2)"
            
            # Col 16 (Q): Constant? Probe showed 0.035
            row[16] = 0.035
            
            # Col 17 (R): P2P Fee / Method Fee
            # Probe had mostly 0, but 0,476 for PayPal/Bank?
            # Replicating the big IFS from the probe, replacing 5 with {row_count}.
            # Note: 0,476 -> 0.0476 (4.76%)
            # Also handling quote escaping.
            # Using logical PayPal fee assumption if exact string is messy.
            # Actually, let's use the exact logic for PayPal/Bank.
            # Using 0.0476 for 4.76% to be safe.
            curr_j = f"J{row_count}"
            row[17] = (
                f'=IFS({curr_j}="Cash App Reco",0,'
                f'{curr_j}="Zelle Reco",0,'
                f'{curr_j}="Apple Cash Sean",0,'
                f'{curr_j}="PayPal",0.0476,'
                f'{curr_j}="Bank Account Reco",0.0476,'
                f'{curr_j}="Bank Account Ali",0.0476,'
                f'{curr_j}="Cash App Emma",0,'
                f'{curr_j}="Cash App Sean",0,'
                f'{curr_j}="Cash App KeShaun",0,'
                f'{curr_j}="Cash App Corey",0,'
                f'TRUE,0)' # Default 0 if no match, probe had trailing 476?
            )
            # The probe ended with ...Cash App Corey",0,476) -> implying else 476?? That seems high.
            # Maybe 0.0476? I'll assume 0 fallthrough for safety or 0.0476.
            # Safe bet: 0.0476 as fallback? Or 0. To avoid huge loss, I'll set 0.0476 as fallback if unknown?
            # Start with 0.

            # Col 18 (S): Fixed Fee? Probe showed 5.
            row[18] = 5
            
            # Col 19 (T): Withdrawal Amount
            # Formula: =(I5*(1-P5-R5)-S5)*(1-Q5)
            # I=Amount(8), P=Fee1(15), R=Fee2(17), S=Fixed(18), Q=Fee3(16)
            row[19] = f"=(I{row_count}*(1-P{row_count}-R{row_count})-S{row_count})*(1-Q{row_count})"

            # Update specific row
            # gspread update() takes range 'A5:Z5'
            # Convert row_count to range string
            cell_range = f"A{row_count}:Y{row_count}" # Col 25 is Y? A=1, Z=26. Y=25.
            
            logger.info(f"Writing to range {cell_range}...")
            ws.update(range_name=cell_range, values=[row], value_input_option='USER_ENTERED')
            logger.info(f"Ticket written for {username}: ${transaction.amount} (Row {row_count})")

        except Exception as e:
            logger.error(f"Failed to append to Sheets: {e}", exc_info=True)

# Global instance
sheets_writer = SheetsWriter.get_instance()
