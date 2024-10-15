import telebot, os, requests, sqlite3
from telebot import types
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv("container.env")

weather_key = os.getenv("WEATHER_API")
telegram_token = os.getenv("TELEGRAM_API")

bot = telebot.TeleBot(telegram_token)

con = sqlite3.connect("weather_bot.db", check_same_thread=False)
cur = con.cursor()
eWeather = ("thunderstorm", "shower rain", "heavy snow", "shower snow", "tornado", "volcanic ash", "clear")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    reply_message = """\
Hi there, I am Weather Bot.
I am here to report you the weather in your area and to alert if it is gonna ba dangerous. To start using the bot, you have to share your current location.
Please turn on GPS on your device, before doing so.
If you need help use the '/help' command!\
"""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    button = types.KeyboardButton('Share location', request_location=True)

    markup.add(button)

    bot.send_message(message.chat.id, reply_message, reply_markup=markup)


@bot.message_handler(commands=["help"])
def send_help(message):
    help_message = """
    Hello, I am a weather alert bot. My purpose is to inform you about the current and dangerous weathers in your area.
To start using me, you will need to share your location first. After this, you will be able to request for the weather info.
Besides that, every hour, I am going to automatically inform you about the current weather.
Every 25 minutes, I check if a dangerous weather conditions are expected in your area, if so, I am going to inform you.
Have a good day and be well!
    """
    bot.reply_to(message, help_message)


@bot.message_handler(content_types=['location'])
def save_info(message):
    user_id = message.chat.id
    location = message.location

    data = (user_id, message.from_user.first_name, location.latitude, location.longitude)

    check = cur.execute("SELECT * FROM users_data WHERE chat_id = ?", (user_id, ))
    check = check.fetchall()
    if check:
        cur.execute("UPDATE users_data SET username = ?, lat = ?, lon = ? WHERE chat_id = ?", (*data[1:], data[0]))
        con.commit()
    else:
        cur.execute("INSERT INTO users_data (chat_id, username, lat, lon) VALUES (?, ?, ?, ?)", data)
        con.commit()

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    update_button = types.KeyboardButton("Update location", request_location=True)
    info_button = types.KeyboardButton("Get the weather")

    markup.add(update_button)
    markup.add(info_button)

    bot.send_message(message.chat.id, "We recieved your location, to update it, press corresponding button\nTo get info about the weather press the corresponding button", reply_markup=markup)


def get_weather(lat, lon):
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_key}&units=metric'
    weather_report = requests.get(weather_url).json()

    return weather_report


@bot.message_handler(func=lambda m: m.text == "Get the weather")
def give_weather(message):
    data = cur.execute("SELECT * FROM users_data WHERE chat_id = ?", (message.chat.id, ))
    data = data.fetchall()
    con.commit()
    data = data[0]

    username = data[1]
    lat = data[2]
    lon = data[3]

    weather_report = get_weather(lat, lon)
    weather_type = weather_report['weather'][0]['description']
    temperature = weather_report['main']['temp']
    windspeed = weather_report['wind']['speed']

    bot.send_message(message.chat.id, f"Hello, {username}! Currently, it is {weather_type} in your area. Temperature is {temperature} by celcius. Wind speed is {windspeed}m/s. Have a nice day")


def send_alert():
    data = cur.execute("SELECT * FROM users_data")
    data = data.fetchall()
    con.commit()

    if data:
        for unit in data:
            user = unit
            chat_id = user[0]
            lat = user[2]
            lon = user[3]
            weather_report = get_weather(lat, lon)
            weather_type = weather_report['weather'][0]['main'].lower()
            weather_desc = weather_report['weather'][0]['description'].lower()
            
            if (weather_type in eWeather) or (weather_desc in eWeather):
                bot.send_message(chat_id, f"ALERT! You have {weather_type} in your area! Be cautious and stay safe!")
            else:
                continue


def send_info():
    data = cur.execute("SELECT * FROM users_data")
    data = data.fetchall()
    con.commit()

    if data:
        for unit in data:
            user = unit
            chat_id = user[0]
            username = user[1]
            lat = user[2]
            lon = user[3]

            weather_report = get_weather(lat, lon)
            weather_type = weather_report['weather'][0]['description']
            temperature = weather_report['main']['temp']
            windspeed = weather_report['wind']['speed']

            bot.send_message(chat_id, f"Hello, {username}! Currently, it is {weather_type} in your area. Temperature is {temperature} by celcius. Wind speed is {windspeed}m/s. Have a nice day")


def scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_alert, "interval", minutes = 25)
    scheduler.add_job(send_info, "interval", minutes = 60)
    scheduler.start()


scheduler()
bot.infinity_polling()