import telebot
from telebot import types
from flask import Flask, request
import numpy as np
import math
import mysql.connector

database = mysql.connnector.connect(
    host = "localhost",
    user = "root",
    password = "root",
    database = "kursova"
)

cursor = database.cursor()

app = Flask(__name__)
bot = telebot.TeleBot('1724663886:AAGhkJY-sIz67hvpXAtX8gTjIbja8lBMEjQ', threaded=True)

places = {
    "Костел і монастир Бернардинів": {
        "location": "49.84003013944798+24.034351053972166",
        "category": "pab",
    },
    "Храм Успіння Пресвятої Богородиці": {
        "location": "49.84261977664883+24.0344346247853",
        "category": "cafe",
        "description": """
           My absolute favourite bar! 
           Mai Tie cocktail is one love - really one of the best cocktails 
           I’ve ever had! 
           The food also great!
    """
    },
    "Lviv National University Faculty of Economics": {
        "location": "49.8425275+24.0280427",
        "category": "science",
        "description": """
           My absolute favourite bar! 
           Mai Tie cocktail is one love - really one of the best cocktails 
           I’ve ever had! 
           The food also great!
    """
    },
    "Under Black Eagle": {
        "location": "49.84288373818804+24.032471357922237",
        "category": "science"
    },
    "Dobriy Druh": {
        "location": "49.843900092069404+24.030807576255405",
        "category": "pub",
        "description": """
The beer restaurant "Good Friend" will provide you with the opportunity to relax after work.
Here everyone will feel easy / completely free. Beer bars are exactly what all lovers of relaxation need.
You will love us!
"""
    },
    "Греко-католицький архикатедральний собор Святого Юра": {
        "location": "49.838838607607045+24.012932156072566",
        "category": "pub"
    },
    "Шевченківський гай": {
        "location": "49.84358198924415+24.064457826316634",
        "category": "pub",
        "description": """
The beer restaurant "Good Friend" will provide you with the opportunity to relax after work.
Here everyone will feel easy / completely free. Beer bars are exactly what all lovers of relaxation need.
You will love us!
"""
    },
    "Стрийський парк": {
        "location": "49.82363663136955+24.0250393468649",
        "category": "pub",
        "description": """
The beer restaurant "Good Friend" will provide you with the opportunity to relax after work.
Here everyone will feel easy / completely free. Beer bars are exactly what all lovers of relaxation need.
You will love us!
"""
    }
}

routes = {
    "Route_1": ["Костел і монастир Бернардинів", "Храм Успіння Пресвятої Богородиці",
                "Lviv National University Faculty of Economics"],
    "Route_2": ["Under Black Eagle", "Стрийський парк", "Шевченківський гай"],
    "Route_3": ["Греко-католицький архикатедральний собор Святого Юра", "Храм Успіння Пресвятої Богородиці",
                "Dobriy Druh"]
}

user_active_route = {

}

user_curr_location = {
    "current": " "
}

G_MAPS_URL = "https://www.google.com/maps/dir/"


# Метод для отримання відстані між точками у км
def get_distance_in_km(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = np.deg2rad(lat2 - lat1)
    dLon = np.deg2rad(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(deg_2_rad(lat1)) * math.cos(deg_2_rad(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d


# Метод для переведення градусів у радіани
def deg_2_rad(deg):
    return deg * (math.pi / 180)


# Метод для відображення списку категорій для коистувача
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    itembtn1 = types.InlineKeyboardButton('Маршрути', callback_data='route')
    itembtn2 = types.InlineKeyboardButton('Ресторани', callback_data='caffe')
    itembtn3 = types.InlineKeyboardButton('Готелі', callback_data='restaurant')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.reply_to(message, "", reply_markup=markup)


# Метод для встановлення початкової позиції користувача
@bot.message_handler(commands=["geo"])
def geo(message):
    button_geo = types.KeyboardButton(text="Надіслати локацію", request_location=True)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "", reply_markup=keyboard)


# Метод для повернення тепершіньої локації користувача
@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        start_location = f"/{message.location.latitude}" + "+" + f"{message.location.longitude}"
        user_curr_location["current"].replace(" ", f"{start_location}")
    return start_location

# Метод для відображення списку доступних марщрутів
@bot.callback_query_handler(lambda a: a.data == 'route')
def list_routes(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key in routes:
        markup.add(types.InlineKeyboardButton(f'{key}', callback_data=f"chosen_route_{key}"))
    bot.reply_to(message.message, "Choose one route:", reply_markup=markup)


CHOSEN_ROUTE = 'chosen_route_'


# Метод для надсилання деталей вибраного маршруту
@bot.callback_query_handler(lambda call: call.data.startswith(CHOSEN_ROUTE))
def sendroute(message):
    bot.send_message(message.message.chat.id, get_direction(routes[message.data.replace(CHOSEN_ROUTE, '')], message.message))


# Метод для встоновлення активного маршруту
@bot.callback_query_handler(lambda a: a.data.startswith(CHOSEN_ROUTE))
def set_active_route(message):
    user_active_route[message.message.chat.username] = list(map(
        lambda a: places[a]
        , routes[message.data.replace(CHOSEN_ROUTE, '')]
    ))
    print(message)


# Метод для отримання тепершіньої локації користувача
@bot.callback_query_handler(lambda a: a.data == 'geo')
def get_direction(routes, message):
    route_details = [(route, places[route]) for route in routes]
    start_location = location(message)
    lat_lon = '/'.join(map(lambda detail: f"{detail[1]['location']}", route_details))
    return G_MAPS_URL + start_location + lat_lon


# Метод для надсилання інформації про категорію кафе
@bot.callback_query_handler(lambda call: call.data == 'caffe')
def send_caffes(message):
    cursor.execute("SELECT photoOfCaffe, caffe FROM info")
    result = cursor.fetchall()
    for x in result:
        bot.send_message(message.message.chat.id, f"{x}")

# Метод для надсилання інформації про категорію готелі
@bot.callback_query_handler(lambda a: a.data == 'restaurant')
def send_hotels(message):
   cursor.execute("SELECT photoOfHotels, hotels FROM info")
   result = cursor.fetchall()
   for x in result:
       bot.send_message(message.message.chat.id, f"{x}")

# Метод для обробки http запитів від телеграм бота
@app.route("/", methods=['POST'])
def webhook():
    content_type = request.headers['content-type']
    if content_type == 'application/json':
        request_json = request.get_json(silent=True)
        print(request_json)
        update = telebot.types.Update.de_json(request_json)
        bot.process_new_updates([update])
    else:
        raise ValueError(f"Expected json, was {content_type}")
    return 'ok'


bot.polling()

if __name__ == "__main__":
    app.run(debug=True)
