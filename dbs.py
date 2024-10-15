import sqlite3

con = sqlite3.connect("weather_bot.db", check_same_thread=False)
cur = con.cursor()
cur.execute("CREATE TABLE users_data(chat_id INTEGER PRIMARY KEY, username TEXT, lat REAL, lon REAL)")
con.commit()