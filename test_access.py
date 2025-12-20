#!/usr/bin/env python3
"""
Тестирование системы доступа с порогом $500
"""
import json
import urllib.parse
import requests

def create_test_init_data(username, user_id=123456789):
    """Создание тестового initData для Telegram"""
    user_data = {
        "id": user_id,
        "first_name": "Test",
        "last_name": "User",
        "username": username.lstrip('@'),
        "language_code": "en"
    }

    user_json = json.dumps(user_data)
    user_encoded = urllib.parse.quote(user_json)
    init_data = f"user={user_encoded}"
    return init_data

base_url = "http://localhost:8080/api"

print("=" * 60)
print("ТЕСТИРОВАНИЕ СИСТЕМЫ ДОСТУПА С ПОРОГОМ $500")
print("=" * 60)

# Тест 1: Клиент с высоким оборотом (> $500)
print("\n1. Клиент с высоким оборотом (@memphees - $110K)")
username = "memphees"
init_data = create_test_init_data(username)
headers = {"X-Telegram-Init-Data": init_data}

response = requests.get(f"{base_url}/access-status", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Доступ: {data['has_access']}")
    print(f"   💰 Заработано: ${data['total_earnings']:.2f}")
    print(f"   🎯 Порог: ${data['threshold_amount']:.2f}")
    print(f"   📊 Прогресс: {data['progress_percentage']:.1f}%")
    print(f"   👑 Админ: {data['is_admin']}")
else:
    print(f"   ❌ Error: {response.text}")

# Тест 2: Клиент с низким оборотом (< $500) - если есть
print("\n2. Попытка доступа клиента с низким оборотом")
username = "lowuser123"  # Не существующий пользователь
init_data = create_test_init_data(username)
headers = {"X-Telegram-Init-Data": init_data}

response = requests.get(f"{base_url}/balance", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 403:
    print(f"   ✅ Доступ правильно заблокирован")
    print(f"   Сообщение: {response.json()['detail']}")
elif response.status_code == 200:
    print(f"   ⚠️  Доступ получен (возможно новый клиент)")
else:
    print(f"   ❌ Error: {response.text}")

# Тест 3: Access status для низкого клиента
response = requests.get(f"{base_url}/access-status", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"   Доступ: {data['has_access']}")
    print(f"   Заработано: ${data['total_earnings']:.2f}")
    print(f"   До порога: ${data['threshold_amount'] - data['total_earnings']:.2f}")

# Тест 4: Список топ клиентов с доступом
print("\n3. Топ клиенты (должны иметь доступ)")
top_clients = ["yallarecooked", "destined2win", "nn453"]
for username in top_clients:
    init_data = create_test_init_data(username)
    headers = {"X-Telegram-Init-Data": init_data}

    response = requests.get(f"{base_url}/access-status", headers=headers)
    if response.status_code == 200:
        data = response.json()
        status_icon = "✅" if data['has_access'] else "❌"
        print(f"   {status_icon} @{username}: ${data['total_earnings']:.2f} ({data['progress_percentage']:.0f}%)")

print("\n" + "=" * 60)
print("✅ ТЕСТЫ ЗАВЕРШЕНЫ")
print("=" * 60)
