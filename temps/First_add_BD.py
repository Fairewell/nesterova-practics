import requests
import json
import os
import random
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Загрузка переменных окружения
dotenv_path = os.path.join(os.getcwd(), ".env")
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

# Функция для генерации случайного имени с фамилией
def generate_random_name():

    # Списки имен и фамилий
    male_first_names = [
        "Иван", "Дамир", "Даниил", "Мерген", "Виктор", 
        "Дугар", "Сергей", "Дмитрий", "Александр", "Максим",
        "Анатолий", "Николай", "Роман", "Антон", "Павел",
        "Григорий", "Игорь", "Владимир", "Станислав", "Юрий"
    ]

    female_first_names = [
        "Анна", "Елена", "Ксения", "Мария", "Татьяна", 
        "Ольга", "Анастасия", "Светлана", "Дарья", "Виктория",
        "Наталья", "Юлия", "Кристина", "Екатерина", "Алёна",
        "Людмила", "Валентина", "Зинаида", "София", "Ирина"
    ]

    last_names = [
        "Смирнов", "Иванов", "Кузнецов", "Петров", "Сидоров", 
        "Попов", "Лебедев", "Ковалев", "Морозов", "Федоров",
        "Соловьев", "Григорьев", "Васильев", "Беляев", "Королев",
        "Михайлов", "Тарасов", "Борисов", "Зиновьев", "Степанов",
        "Алексеев", "Киселев", "Сергеев", "Дмитриев", "Андреев",
        "Ковалев", "Савельев", "Кириллов", "Лавров", "Семёнов",
        "Климов", "Фролов", "Сорокин", "Коваленко", "Громов",
        "Лукьянов", "Денисов", "Панфилов", "Шевченко", "Дорофеев"
    ]

    gender = random.choice(['male', 'female'])  # Случайный выбор пола
    if gender == 'male':
        first_name = random.choice(male_first_names)
    else:
        first_name = random.choice(female_first_names)
    
    last_name = random.choice(last_names)
    return f"{first_name} {last_name}"

# Функция для генерации случайных дат
def generate_random_dates():
    check_in_date = datetime.now() + timedelta(days=random.randint(1, 30))
    check_out_date = check_in_date + timedelta(days=random.randint(1, 7))
    return check_in_date.strftime("%Y-%m-%d"), check_out_date.strftime("%Y-%m-%d")

# Функция для добавления нового бронирования
def add_booking(house_id,room_id, customer_name, check_in_date, check_out_date, total_price):
    booking_id = f'booking:{customer_name.replace(" ", "_")}_{check_in_date}'
    booking_data = {
        "_id": booking_id,
        "type": "booking",
        "house_id": house_id,
        "room_number": room_id,
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

# Данные о домах
houses = [
    {"name": "Домик 1", "rooms": 12, "price_per_night": 500},
    {"name": "Домик 2", "rooms": 4, "price_per_night": 3000},
    {"name": "Домик 3", "rooms": 4, "price_per_night": 3000},
    {"name": "Домик 4", "rooms": 4, "price_per_night": 3000},
    {"name": "Домик 5", "rooms": 7, "price_per_night": 500},
    {"name": "Комната 6.1", "rooms": 6, "price_per_night": 500},
    {"name": "Комната 6.2", "rooms": 6, "price_per_night": 500},
    {"name": "Комната 6.3", "rooms": 7, "price_per_night": 500},
    {"name": "Комната 6.4", "rooms": 7, "price_per_night": 500},
    {"name": "Комната 6.5", "rooms": 6, "price_per_night": 500},
    {"name": "Комната 6.0", "rooms": 5, "price_per_night": 500},
    {"name": "Домик 7", "rooms": 8, "price_per_night": 500},
    {"name": "Домик 8", "rooms": 6, "price_per_night": 500},
    {"name": "Комната 9.1", "rooms": 3, "price_per_night": 500},
    {"name": "Комната 9.2", "rooms": 6, "price_per_night": 500},
    {"name": "Комната 10.1", "rooms": 4, "price_per_night": 500},
    {"name": "Комната 10.2", "rooms": 6, "price_per_night": 500},
    {"name": "Домик 12", "rooms": 3, "price_per_night": 2600},
    {"name": "Домик 13", "rooms": 3, "price_per_night": 2600},
    {"name": "Домик 14", "rooms": 4, "price_per_night": 3000},
]

# Добавление домов в базу данных и генерация бронирований
idx = 0  # Инициализируем idx перед циклом
total_bookings = 0  # Счетчик для общего количества бронирований

# Начало общего времени выполнения
start_time = time.time()

for house in houses:
    # Начало времени добавления дома
    house_start_time = time.time()
    
    house_id = add_house(house["name"], house["rooms"], house["price_per_night"])
    print(f"[{idx + 1}]   Дом добавлен с ID: {house_id}")
    
    jdx = random.randint(1, house["rooms"])  # Генерация от 1 до количества мест
    print(f'Для {house_id} будет сгенерировано {jdx} броней')
    
    # Начало времени добавления бронирований для текущего дома
    bookings_start_time = time.time()
    
    # Генерация jdx бронирований для каждого дома
    for booking_idx in range(jdx):
        customer_name = generate_random_name()
        check_in_date, check_out_date = generate_random_dates()
        total_price = house["price_per_night"] * (datetime.strptime(check_out_date, "%Y-%m-%d") - datetime.strptime(check_in_date, "%Y-%m-%d")).days
        booking_id = add_booking(house_id, jdx + 1, customer_name, check_in_date, check_out_date, total_price)
        
        # Время добавления бронирования
        booking_time = time.time() - bookings_start_time
        print(f"[{idx + 1}][{booking_idx + 1}]   Бронирование добавлено с ID: {booking_id} за {booking_time:.4f} секунд")
    
    # Общее время добавления всех бронирований для текущего дома
    total_bookings += jdx  # Увеличиваем общий счетчик бронирований
    bookings_total_time = time.time() - bookings_start_time
    print(f"Все бронирования для {house_id} добавлены за {bookings_total_time:.4f} секунд")
    
    # Время добавления дома
    house_total_time = time.time() - house_start_time
    print(f"Дом {house_id} добавлен за {house_total_time:.4f} секунд")
    
    idx += 1  # Увеличиваем idx для следующего дома

# Общее время выполнения кода
total_time = time.time() - start_time

# Вывод итогов
print(f"\nОбщее количество добавленных домов: {idx}")
print(f"Общее количество добавленных бронирований: {total_bookings}")
print(f"Общее время выполнения кода: {total_time:.4f} секунд")