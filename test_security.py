import hmac
import hashlib
import json
import urllib.parse
from api.main import validate_telegram_data

def test_telegram_validation():
    # 1. Setup mock data
    bot_token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    user_data = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "language_code": "en",
        "allows_write_to_pm": True
    }
    user_json = json.dumps(user_data)
    
    # 2. Construct init_data dict without hash
    data_dict = {
        "query_id": "AAG...",
        "user": user_json,
        "auth_date": "1700000000"
    }
    
    # 3. Calculate valid hash
    data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(data_dict.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    valid_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    # 4. Create full init_data strings
    valid_init_data = f"query_id=AAG...&user={urllib.parse.quote(user_json)}&auth_date=1700000000&hash={valid_hash}"
    invalid_init_data = f"query_id=AAG...&user={urllib.parse.quote(user_json)}&auth_date=1700000000&hash=invalid_hash"
    
    # 5. Run tests
    print("Testing Valid Hash...")
    assert validate_telegram_data(valid_init_data, bot_token) == True
    print("✅ Valid Hash passed")
    
    print("Testing Invalid Hash...")
    assert validate_telegram_data(invalid_init_data, bot_token) == False
    print("✅ Invalid Hash passed")
    
    print("Testing Tampered Data...")
    tampered_data = valid_init_data.replace("1700000000", "1700000001") # Change date
    assert validate_telegram_data(tampered_data, bot_token) == False
    print("✅ Tampered Data passed")

if __name__ == "__main__":
    try:
        test_telegram_validation()
        print("\nAll security tests passed! 🔒")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
