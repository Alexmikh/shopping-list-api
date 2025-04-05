import requests
import random
import time
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"

users = [
    {"username": "alice", "password": "alice"},
    {"username": "bob", "password": "bob"},
    {"username": "carol", "password": "carol"},
]

# 1. Регистрация пользователей
for user in users:
    r = requests.post(f"{BASE_URL}/register", auth=HTTPBasicAuth(user["username"], user["password"]))
    if r.status_code == 200:
        print(f"[OK] Registered {user['username']}")
    else:
        print(f"[WARN] Could not register {user['username']} ({r.status_code}): {r.text}")

# 2. Имитируем активность
item_names = ["milk", "bread", "eggs", "apples", "cheese", "water", "coffee", "chocolate"]
item_ids = []

for i in range(20):
    user = random.choice(users)
    auth = HTTPBasicAuth(user["username"], user["password"])

    # случайно добавляем товар
    item_name = random.choice(item_names) + f"-{random.randint(1, 100)}"
    r = requests.post(f"{BASE_URL}/items", params={"name": item_name}, auth=auth)
    if r.status_code == 200:
        print(f"[+] {user['username']} added item: {item_name}")
        # парсим id из запроса списка
        list_r = requests.get(f"{BASE_URL}/items", auth=auth)
        if list_r.ok:
            for item in list_r.json():
                if item["name"] == item_name:
                    item_ids.append((item["id"], user))
    else:
        print(f"[!] Failed to add item: {r.text}")

    # случайно удаляем или помечаем купленным
    if item_ids and random.random() < 0.7:
        item_id, item_user = random.choice(item_ids)
        action = random.choice(["delete", "buy"])
        auth_action = HTTPBasicAuth(item_user["username"], item_user["password"])

        if action == "delete":
            r = requests.delete(f"{BASE_URL}/items/{item_id}", auth=auth_action)
            print(f"[-] {item_user['username']} soft-deleted item {item_id}")
        elif action == "buy":
            r = requests.post(f"{BASE_URL}/items/{item_id}/buy", auth=auth_action)
            print(f"[✓] {item_user['username']} bought item {item_id}")

    # случайный просмотр
    if random.random() < 0.5:
        r = requests.get(f"{BASE_URL}/items", auth=auth)
        if r.ok:
            print(f"[👁️] {user['username']} sees {len(r.json())} visible items")

    time.sleep(0.2)  # чтобы не спамить слишком быстро
