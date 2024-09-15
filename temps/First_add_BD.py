import requests
import json
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
dotenv_path = os.path.join(os.getcwd(), ".env")
print(f".env path: {dotenv_path}")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

LOGIN = os.getenv("DB_LOGIN")
PASSWORD = os.getenv("DB_PASSWORD")
NAME = os.getenv("DB_NAME")
# Настройки подключения к CouchDB
COUCHDB_URL = f"http://{LOGIN}:{PASSWORD}@localhost:5984"
DB_NAME = NAME


# Создание базы данных, если она не существует
def create_database():
    response = requests.put(f"{COUCHDB_URL}/{DB_NAME}")
    if response.status_code == 201:
        print("База данных создана.")
    elif response.status_code == 412:
        print("База данных уже существует.")
    else:
        print("Ошибка при создании базы данных:", response.json())


# Функция для добавления нового дома
def add_house(name, rooms, price_per_night):
    house_id = f'house:{name.replace(" ", "_")}'
    house_data = {
        "_id": house_id,
        "type": "house",
        "name": name,
        "rooms": rooms,
        "price_per_night": price_per_night,
        "bookings": [],
    }
    response = requests.put(f"{COUCHDB_URL}/{DB_NAME}/{house_id}", json=house_data)
    return house_id if response.status_code in (201, 202) else None


# Функция для добавления нового бронирования
def add_booking(house_id, customer_name, check_in_date, check_out_date, total_price):
    booking_id = f'booking:{customer_name.replace(" ", "_")}_{check_in_date}'
    booking_data = {
        "_id": booking_id,
        "type": "booking",
        "house_id": house_id,
        "customer_name": customer_name,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "total_price": total_price,
    }
    response = requests.put(f"{COUCHDB_URL}/{DB_NAME}/{booking_id}", json=booking_data)

    if response.status_code in (201, 202):
        # Обновление дома с добавлением нового бронирования
        house_response = requests.get(f"{COUCHDB_URL}/{DB_NAME}/{house_id}")
        if house_response.status_code == 200:
            house_doc = house_response.json()
            house_doc["bookings"].append(booking_id)
            requests.put(f"{COUCHDB_URL}/{DB_NAME}/{house_id}", json=house_doc)

    return booking_id if response.status_code in (201, 202) else None


# Пример использования функций
create_database()
house_id = add_house("Дом у озера", 3, 150)
booking_id = add_booking(house_id, "Иван Иванов", "2023-12-01", "2023-12-07", 900)

print(f"Дом добавлен с ID: {house_id}")
print(f"Бронирование добавлено с ID: {booking_id}")
