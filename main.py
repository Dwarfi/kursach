import telebot
from telebot import types
from flask import Flask, request
import numpy as np
import math

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
def start(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    itembtn1 = types.InlineKeyboardButton('Routes', callback_data='route')
    itembtn2 = types.InlineKeyboardButton('Best Caffe', callback_data='caffe')
    itembtn3 = types.InlineKeyboardButton('Best Hotels', callback_data='restaurant')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.reply_to(m, "Choose one option:", reply_markup=markup)


# Метод для встановлення початкової позиції користувача
@bot.message_handler(commands=["geo"])
def geo(message):
    button_geo = types.KeyboardButton(text="Send location", request_location=True)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Hey! Press this button and send me your location", reply_markup=keyboard)


# Метод для повернення тепершіньої локації користувача
@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        start_location = f"/{message.location.latitude}" + "+" + f"{message.location.longitude}"
    return start_location


# Метод для відображення списку доступних марщрутів
@bot.callback_query_handler(lambda a: a.data == 'route')
def list_routes(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key in routes:
        markup.add(types.InlineKeyboardButton(f'{key}', callback_data=f"chosen_route_{key}"))
    bot.reply_to(m.message, "Choose one route:", reply_markup=markup)


CHOSEN_ROUTE = 'chosen_route_'


# Метод для надсилання деталей вибраного маршруту
@bot.callback_query_handler(lambda call: call.data.startswith(CHOSEN_ROUTE))
def sendroute(call):
    bot.send_message(call.message.chat.id, get_direction(routes[call.data.replace(CHOSEN_ROUTE, '')], call.message))


# Метод для встоновлення активного маршруту
@bot.callback_query_handler(lambda a: a.data.startswith(CHOSEN_ROUTE))
def set_active_route(m):
    user_active_route[m.message.chat.username] = list(map(
        lambda a: places[a]
        , routes[m.data.replace(CHOSEN_ROUTE, '')]
    ))
    print(m)


# Метод для отримання тепершіньої локації користувача
@bot.callback_query_handler(lambda a: a.data == 'geo')
def get_direction(routes, a):
    route_details = [(route, places[route]) for route in routes]
    lat_lon = '/'.join(map(lambda detail: f"{detail[1]['location']}", route_details))
    curr_location = location(a.message)
    return G_MAPS_URL + curr_location + lat_lon


# Метод для надсилання інформації про категорію кафе
@bot.callback_query_handler(lambda call: call.data == 'caffe')
def send_caffes(a):
    bot.send_photo(a.message.chat.id, 'https://img.the-village.com.ua/the-village.com.ua/post_image-image'
                                      '/lRgqr0BOtX7q5b9LwrcNgQ-article.jpg')
    bot.send_message(a.message.chat.id, f""" Ліпша львівська настоянка – невід'ємна частина старого Львова. П'яну вишню здавна 
    у Львові настоювали у кожній хаті. Кожна львівська господиня робила ту настоянку, і кожна панєнка знала той смак. 
    Настоянка була така смачна, що жодна кобіта, незалежно від віку, не могла встояти перед тим смаком. І колєжанки, 
    як здибалися попліткувати про хлопів, завше смакували настоянку. Львівські хлопи швидко дізналися той рецепт і на 
    всі здибанки чи шпацер брали з собою фляжчину П'яної вишні. І жодна не могла відмовити. Напій смачний, 
    забирає швидко. Зроблений за традиційним рецептом на ліпшому коньячному спирті з відбірних вишень. Добре 
    надається до здибанок або інших пригод з кобітами. Допомагає хлопам знайти кохання з XVII століття. """)
    bot.send_photo(a.message.chat.id, 'https://i.pinimg.com/originals/2c/bb/b6/2cbbb6a4cb98b4c82651b76edf789333.jpg')
    bot.send_message(a.message.chat.id, f""" «Park. Art of Rest» — це ресторанний комплекс біля центральної частини Львова, 
    оточений зеленим оазисом Парку культури. На території є парковка на 50 місць, тому в нас майже завжди є де 
    припаркуватися. Наш комплекс складається з двох залів: Rest Hall (перший поверх), Art Hall (другий), 2 VIP-зали 
    для 20 людей у кожній. Два поверхи із залами для реалізації будь-яких святкових і буденних фантазій. Весілля 
    вашої мрії, корпоратив із найкращими колегами, бенкет на честь 50-річчя вашого батька, вечірка тільки для своїх 
    або ділова зустріч у VIP-кімнаті. Лаунж-ресторан Rest Hall працює з 12:00 - 21:00 понеділок - четвер та з 12:00 - 
    23:00 п'ятниця - неділя . Тут ви можете спробувати страви від шефа з меню A la carte і авторські коктейлі від 
    талановитого бар-менеджера Сергія Федеки. Також у цьому залі є вихід на терасу, де можна замовити кальян і побути 
    серед природи За вино відповідає професійний сомельє Павлюх Богдан, який неодноразово відзначений українськими та 
    міжнародними нагородами. """)
    bot.send_photo(a.message.chat.id,
                   'https://mesta.com.ua/wp-content/uploads/2019/10/42044322_547067759082358_2470509216368951296_o-1024x809.jpg')
    bot.send_message(a.message.chat.id, f""" Ресторан «36По» розмістився в самому серці Львова, на площі Ринок. 
    П'ятиповерховий заклад складається з пивного залу, який займає два рівні, рибного залу, залу нової української 
    кухні, винної й сигарної кімнат. Дизайнерський інтер'єр ресторану виконаний у стилі тропіків з безліччю живих 
    рослин, які звисають зі стелі, зі справжнім акваріумом, який займає два поверхи й в якому плаває акула, 
    а також з прозорим фортепіано. В основі меню представлена сучасна українська кухня в авторській інтерпретації 
    шеф-кухаря. Гості можуть замовити холодні закуски, традиційні українські страви, страви до пива, салати, 
    перші страви, основні страви з риби, м'яса, птиці, вареники, гарніри, десерти, морозиво, сорбети """)
    bot.send_message(a.message.chat.id, f""" Театр пива «Правда» знаходиться в самому серці Львова – на площі Ринок. У цьому 
    ресторані ви і справді, як в театрі, зможете спостерігати за роботою майстрів-пивоварів, кухарів відкритої кухні, 
    і все це під акомпанемент оркестру. А заодно тут можна смачно повечеряти і провести годинку-другу за кухлем 
    свіжого пива. В меню ресторану страви галицької та європейської кухні і, звичайно ж, великий вибір оригінальних 
    пивних закусок. Та й самого авторського пива тут чимало, а назви сортів порадують навіть самого сумного 
    відвідувача: де ще ви спробуєте пиво «Весільна свиня-сороконіжка», «Гребуча корова» або «Надія Обами»? """)


# Метод для надсилання інформації про категорію готелі
@bot.callback_query_handler(lambda a: a.data == 'restaurant')
def send_hotels(a):
    bot.send_photo(a.message.chat.id, 'https://cf.bstatic.com/images/hotel/max1024x768/259/259260775.jpg')
    bot.send_message(a.message.chat.id, """Історія Grand Hotel Lviv починається у 1893 р. На місці готелю раніше була будівля, у якій працював батько Леопольда фон Захер-Мазоха, відомого австрійського письменника-новеліста. У готелі дбайливо збережені унікальні поручні, двері та меблі, які відтворюють атмосферу ХХ ст. Ми пишаємось нашою історією і прагнемо стати частиною Вашої.
Grand Hotel Lviv завжди слідкує за сучасними трендами. Готель одним із першим провів електричне освітлення у Львові. Ще у ті далекі часи готель слідкував за модними тенденціями, проводив реконструкції у 1910 р., 1992 р. У 2016 р. закінчилася ще одна реконструкція, метою якої було оснащити готель сучасною технікою. А яким феєричним було відкриття, зіркою якого була сама Періс Хілтон!
Місце релаксу – центр Oasis Infinity Pool & SPA. Найкраща косметика, досвідчені майстри, широкий спектр послуг та неймовірна атмосфера – саме те, що треба, щоб відновити сили після насиченого дня.
Перебування у Grand Hotel Lviv Luxury & SPA буде сповненим grandіозними емоціями та турботою, перевершуючи Ваші сподівання!""")
    bot.send_photo(a.message.chat.id, 'https://encrypted-tbn0.gstatic.com/images?q=tbn'
                                      ':ANd9GcTfHKO2vzscD5WTvGJ17I00b7MUpFNQsilrJQ&usqp=CAU')
    bot.send_message(a.message.chat.id, """Основна ідея, що лягла в проектування готелю, максимальне збереження 
    історичного вигляду будівлі, як архітектурної пам’ятки. До елементів інтер’єру, що не підлягали кардинальним 
    змінам, можна віднести: вестибюль з мармуровими сходами та вітражі; підлога з кераміки, що знаходиться на першому 
    поверсі в вестибюлі та в холі на другому; декоративне оздоблення стін з автентичними карнізами.Для ділових 
    зустрічей в BANKHOTEL є 8 конференц-залів загальною місткістю 270 осіб, що забезпечать будь-які вимоги з 
    організації переговорів, семінарів, презентацій. Учасникам ділових заходів також пропонується лаунж зона та 
    відкрита тераса. На території готелю на постійній основі діє виставка двох арт-проектів Кудіна В.П. «Банкноти і 
    шаги» та «Монети». Головна ідея першого проекту – ознайомлення з банкнотами, що були в перебігу в Українській 
    Народній Республіці. Гості готелю та відвідувачі виставки зможуть дізнатись про особливість кожної банкноти, 
    хто був її автором, де вона друкувалась. Особливість проекту «Монети» полягає в знайомстві з ювілейними монетами, 
    що випускає Національний банк України.""")
    bot.send_photo(a.message.chat.id, 'https://citadel-inn.com.ua/fileadmin/_processed_/csm_IMG-6781_42411846df.jpg')
    bot.send_message(a.message.chat.id, """Курортний готель Citadel Inn розміщений у старій фортеці в центрі Львова, 
    де гостям пропонуються розкішні номери з безкоштовним Wi-Fi. Інфраструктура закладу налічує вартий найвищих 
    відзнак ресторан, а також цілодобовий тренажерний зал і сауну. На території готелю облаштована безкоштовна 
    автостоянка. Усі номери та люкси курортного готелю Citadel Inn оснащені телевізором з плоским екраном і 
    кабельними каналами, міні-баром та зоною відпочинку. Приватні ванні кімнати укомплектовані туалетно-косметичними 
    засобами, банними халатами й капцями. У ресторані "Гармата" подаються вишукані страви європейської та української 
    кухні. У винному льосі пропонується великий вибір міжнародних вин. 


    """)


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
