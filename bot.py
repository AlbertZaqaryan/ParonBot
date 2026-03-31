# from telebot import TeleBot
# from dotenv import load_dotenv
# import os

# bot = TeleBot(os.getenv("TOKEN"))
# @bot.message_handler(commands=["start"])
# def start (message):
#     pass


import os
import requests
from telebot import TeleBot, types
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = TeleBot(TOKEN)

# API курсов
API_URL = "https://open.er-api.com/v6/latest/"

# Поддерживаемые валюты
CURRENCIES = ["AMD", "USD", "EUR", "RUB", "GBP", "CNY", "AED", "TRY"]

# Временное хранилище состояний пользователей
user_data = {}


# ====== Получение курсов ======
def get_rate(from_cur, to_cur):
    try:
        url = API_URL + from_cur
        response = requests.get(url)
        data = response.json()

        if data["result"] != "success":
            return None

        rate = data["rates"].get(to_cur)
        return rate
    except:
        return None


# ====== Логика "что можно купить" ======
def what_can_buy(amount, currency):
    amount = float(amount)

    if currency == "AMD":
        if amount < 500:
            return ["жвачка 🍬", "конфета 🍭"]
        elif amount < 1500:
            return ["кофе ☕", "булочка 🥐"]
        elif amount < 5000:
            return ["шаурма 🥙", "фастфуд 🍔"]
        else:
            return ["обед в кафе 🍽️", "пицца 🍕"]

    elif currency == "USD":
        if amount < 2:
            return ["жвачка 🍬"]
        elif amount < 5:
            return ["кофе ☕", "снек 🍫"]
        elif amount < 15:
            return ["фастфуд 🍔"]
        else:
            return ["обед 🍽️", "пицца 🍕"]

    elif currency == "EUR":
        return ["кофе ☕", "круассан 🥐"] if amount < 5 else ["обед 🍽️"]

    elif currency == "RUB":
        return ["чай ☕"] if amount < 200 else ["фастфуд 🍔"]

    elif currency == "GBP":
        return ["кофе ☕"] if amount < 5 else ["обед 🍽️"]

    elif currency == "CNY":
        return ["лапша 🍜"] if amount < 20 else ["обед 🍽️"]

    elif currency == "AED":
        return ["кофе ☕"] if amount < 10 else ["обед 🍽️"]

    elif currency == "TRY":
        return ["чай ☕"] if amount < 50 else ["донер 🥙"]

    return ["товары"]


# ====== Названия стран ======
def get_country(currency):
    return {
        "AMD": "🇦🇲 Армения",
        "USD": "🇺🇸 США",
        "EUR": "🇪🇺 Европа",
        "RUB": "🇷🇺 Россия",
        "GBP": "🇬🇧 Великобритания",
        "CNY": "🇨🇳 Китай",
        "AED": "🇦🇪 ОАЭ",
        "TRY": "🇹🇷 Турция",
    }.get(currency, "")


# ====== /start ======
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_photo(message.chat.id, open('Image.png', 'rb'))
    markup = types.InlineKeyboardMarkup(row_width=4)

    buttons = [types.InlineKeyboardButton(cur, callback_data=f"from_{cur}") for cur in CURRENCIES]
    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "👋 Выбери валюту ИЗ которой конвертировать:",
        reply_markup=markup
    )


# ====== Выбор первой валюты ======
@bot.callback_query_handler(func=lambda call: call.data.startswith("from_"))
def choose_from(call):
    from_currency = call.data.split("_")[1]

    user_data[call.from_user.id] = {"from": from_currency}

    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(cur, callback_data=f"to_{cur}") for cur in CURRENCIES]
    markup.add(*buttons)

    bot.send_message(call.message.chat.id, f"Выбрано: {from_currency}\n\nТеперь выбери валюту В которую:")
    bot.send_message(call.message.chat.id, "👇", reply_markup=markup)


# ====== Выбор второй валюты ======
@bot.callback_query_handler(func=lambda call: call.data.startswith("to_"))
def choose_to(call):
    to_currency = call.data.split("_")[1]

    user_data[call.from_user.id]["to"] = to_currency

    bot.send_message(
        call.message.chat.id,
        f"Отлично! Теперь введи сумму в {user_data[call.from_user.id]['from']}:"
    )


# ====== Ввод суммы ======
@bot.message_handler(func=lambda message: True)
def convert(message):
    user_id = message.from_user.id

    # Проверка, что пользователь выбрал валюты
    if user_id not in user_data or "to" not in user_data[user_id]:
        bot.send_message(message.chat.id, "⚠️ Сначала нажми /start и выбери валюты")
        return

    # Проверка числа
    try:
        amount = float(message.text.replace(",", "."))
    except:
        bot.send_message(message.chat.id, "❌ Введи корректное число")
        return

    from_cur = user_data[user_id]["from"]
    to_cur = user_data[user_id]["to"]

    rate = get_rate(from_cur, to_cur)

    if rate is None:
        bot.send_message(message.chat.id, "❌ Ошибка получения курса")
        return

    converted = round(amount * rate, 2)

    # Что можно купить
    buy_from = what_can_buy(amount, from_cur)
    buy_to = what_can_buy(converted, to_cur)

    country_from = get_country(from_cur)
    country_to = get_country(to_cur)

    text = f"""
💱 {amount} {from_cur} ≈ {converted} {to_cur}

🛒 {country_from} ({amount} {from_cur}):
- """ + "\n- ".join(buy_from) + f"""

🛒 {country_to} ({converted} {to_cur}):
- """ + "\n- ".join(buy_to)

    bot.send_message(message.chat.id, text)


# ====== Запуск ======
bot.polling()