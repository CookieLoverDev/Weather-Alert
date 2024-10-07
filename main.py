import telebot, os, requests
from telebot import types
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv("container.env")

weather_key = os.getenv("WEATHER_API")
telegram_token = os.getenv("TELEGRAM_API")

bot = telebot.TeleBot(telegram_token)

user_data = {}
eWeather = ("thunderstorm", "shower rain", "heavy snow", "shower snow", "tornado", "volcanic ash", "clear")

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am Weather Bot.
I am here to report you the weather in your area and to alert if it is gonna ba dangerous. To start using the bot, you got to share your location\
""")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    button = types.KeyboardButton('Share location', request_location=True)

    markup.add(button)

    bot.send_message(message.chat.id, "Please share your location", reply_markup=markup)


@bot.message_handler(content_types=['location'])
def save_info(message):
    user_id = message.chat.id
    location = message.location

    user_data[user_id] = {
        'chat': message.chat.id,
        'lat' : location.latitude,
        'lon' : location.longitude,
    }

    bot.send_message(message.chat.id, "We recieved your location, to update it, send it one more time")
    print(user_data.items())

def get_weather(lat, lon):
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_key}&units=metric'
    weather_report = requests.get(weather_url).json()

    return weather_report

def send_alert():
    if user_data:
        for user_id, data in user_data.items():
            chat_id = data["chat"]
            lat = data["lat"]
            lon = data["lon"]

            weather_report = get_weather(lat, lon)
            weather_type = weather_report['weather'][0]['main'].lower()
            weather_desc = weather_report['weather'][0]['description'].lower()
            
            if (weather_type in eWeather) or (weather_desc in eWeather):
                bot.send_message(chat_id, f"ALERT! You have {weather_type} in your area! Be cautious and stay safe!")
            else:
                continue

def send_info():
    print("Going to send info")
    if user_data:
        for user_id, data in user_data.items():
            chat_id = data["chat"]
            lat = data["lat"]
            lon = data["lon"]

            weather_report = get_weather(lat, lon)
            print(weather_report)
            weather_type = weather_report['weather'][0]['description']
            temperature = weather_report['main']['temp']
            windspeed = weather_report['wind']['speed']

            bot.send_message(chat_id, f"Hello! Currently, it is {weather_type} in your area. Temperature is {temperature} by celcius. Wind speed is {windspeed}m/s. Have a nice day")

def scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_alert, "interval", minutes = 25)
    scheduler.add_job(send_info, "interval", minutes = 60)
    scheduler.start()

scheduler()
bot.infinity_polling()