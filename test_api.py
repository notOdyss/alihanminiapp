#!/usr/bin/env python3
"""
Тестирование API endpoints
"""
import json
import urllib.parse
import requests

# Создаем мок Telegram initData для тестирования
def create_test_init_data(username):
    """Создание тестового initData для Telegram"""
    user_data = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": username.lstrip('@'),
        "language_code": "en"
    }

    user_json = json.dumps(user_data)
    user_encoded = urllib.parse.quote(user_json)

    # Простой initData без валидации hash (для тестирования)
    init_data = f"user={user_encoded}"
    return init_data

# Test с реальным пользователем из базы
test_username = "memphees"  # Топ клиент по обороту
init_data = create_test_init_data(test_username)

headers = {
    "X-Telegram-Init-Data": init_data
}

base_url = "http://localhost:8080/api"

print("=" * 60)
print(f"ТЕСТИРОВАНИЕ API ДЛЯ @{test_username}")
print("=" * 60)

# Test 1: Health check
print("\n1. Health Check...")
response = requests.get(f"{base_url}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 2: Balance
print("\n2. Balance...")
response = requests.get(f"{base_url}/balance", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Total: ${data['total']:.2f}")
    print(f"   PayPal: ${data['paypal']:.2f}")
    print(f"   Stripe: ${data['stripe']:.2f}")
    print(f"   Withdrawal: ${data['withdrawal']:.2f}")
else:
    print(f"   Error: {response.text}")

# Test 3: Statistics
print("\n3. Statistics...")
response = requests.get(f"{base_url}/statistics", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Total Checks: {data['totalChecks']}")
    print(f"   Total Sum: ${data['totalSum']:.2f}")
    print(f"   Avg Check: ${data['avgCheck']:.2f}")
    print(f"   Avg Checks/Month: {data['avgChecksMonth']:.1f}")
    print(f"   Avg Sum/Month: ${data['avgSumMonth']:.2f}")
else:
    print(f"   Error: {response.text}")

# Test 4: Transactions
print("\n4. Transactions (last 10)...")
response = requests.get(f"{base_url}/transactions?limit=10", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Total: {data['total']}")
    print(f"   Showing: {len(data['transactions'])}")
    for i, tx in enumerate(data['transactions'][:5], 1):
        print(f"   {i}. {tx['payment_method']}: ${tx['amount']:.2f} - {tx['status']} - {tx['created_at'][:10]}")
else:
    print(f"   Error: {response.text}")

print("\n" + "=" * 60)
print("✅ ТЕСТЫ ЗАВЕРШЕНЫ")
print("=" * 60)
