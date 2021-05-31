#--------------------------------------------------
#   Тема: створення додатка-помічника у подорожах -
#   Хомин Віктор Андрійович СА-12                 -
#   Павлишин Тетяна Андріївна СА-13               -
#   Дата створення: 05.03.2021                    -
#--------------------------------------------------
import telebot
from telebot import types
from flask import Flask, request
import numpy as np
import math
import mysql.connector

# Підключення бази даних
database = mysql.connnector.connect(
    host = "localhost",
    user = "root",
    password = "root",
    database = "kursova"
)

cursor = database.cursor()

app = Flask(__name__)
bot = telebot.TeleBot('1724663886:AAGhkJY-sIz67hvpXAtX8gTjIbja8lBMEjQ', threaded=True)

user_active_route = {

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


# Метод для відображення списку категорій для користувача

#--------------------------------------------------------------------------
# markup - При створенні пуста користувацька клавіатура                   -
# itembtn1 - Кнопка, після натискання якої надсилається перелік маршрутів -
# itembtn2 - Кнопка, після натискання якої надсилається перелік ресторанів-
# itembtn3 - Кнопка, після натискання якої надсилається перелік готелів   -
#--------------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    itembtn1 = types.InlineKeyboardButton('Маршрути', callback_data='route')
    itembtn2 = types.InlineKeyboardButton('Ресторани', callback_data='caffe')
    itembtn3 = types.InlineKeyboardButton('Готелі', callback_data='restaurant')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.reply_to(message, "", reply_markup=markup)


# Метод для встановлення початкової позиції користувача

#--------------------------------------------------------------------------
# button_geo - Кнопка, після натискання якої надсилається поточна локація -
# keyboard - При створенні пуста користувацька клавіатура                 -
#--------------------------------------------------------------------------
@bot.message_handler(commands=["geo"])
def geo(message):
    button_geo = types.KeyboardButton(text="Надіслати локацію", request_location=True)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "", reply_markup=keyboard)


# Метод для повернення тепершіньої локації користувача

#--------------------------------------------------------------------------
# start_location - Змінна у яку записується ваша локація відформатована   -
#--------------------------------------------------------------------------
@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        start_location = f"/{message.location.latitude}" + "+" + f"{message.location.longitude}"
    return start_location


# Метод для відображення списку доступних марщрутів

#--------------------------------------------------------------------------
# markup - При створенні пуста користувацька клавіатура                   -
#--------------------------------------------------------------------------
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

#--------------------------------------------------------------------------------
# user_active_route - Словник в який додається ідентифікатор вибраного маршруту -
#--------------------------------------------------------------------------------
@bot.callback_query_handler(lambda a: a.data.startswith(CHOSEN_ROUTE))
def set_active_route(message):
    user_active_route[message.message.chat.username] = list(map(
        lambda a: places[a]
        , routes[message.data.replace(CHOSEN_ROUTE, '')]
    ))
    print(message)


# Метод для отримання тепершіньої локації користувача

#-------------------------------------------------------------------------------
# start_location - Викликає функцію location, та отримує останню відому локацію-
# lat_lon - Додає координати точок у маршруті, у форматування для гугл карт    -
# return... - Повертає посилання на готовий маршрут                            -
#-------------------------------------------------------------------------------
@bot.callback_query_handler(lambda a: a.data == 'geo')
def get_direction(routes, message):
    route_details = [(route, places[route]) for route in routes]
    start_location = location(message)
    lat_lon = '/'.join(map(lambda detail: f"{detail[1]['location']}", route_details))
    return G_MAPS_URL + start_location + lat_lon


# Метод для надсилання інформації про категорію кафе

#-----------------------------------------
# cursor.execute - отримує дані із БД    -
# result - поверта дані в вигляді масиву -
#-----------------------------------------
@bot.callback_query_handler(lambda call: call.data == 'caffe')
def send_caffes(message):
    cursor.execute("SELECT photoOfCaffe, caffe FROM info")
    result = cursor.fetchall()
    for x in result:
        bot.send_message(message.message.chat.id, f"{x}")


# Метод для надсилання інформації про категорію готелі

#-----------------------------------------
# cursor.execute - отримує дані із БД    -
# result - поверта дані в вигляді масиву -
#-----------------------------------------
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
