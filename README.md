<h1>Description</h1>

This is a python script for a Telegram bot, that notifies its users every 60 minutes
about the current weather in the location that they have provided. Every 25 minutes, the script
automatically checks, if the weather in the users locations is currently in extreme conditions,
If so, it immedietly notifies user about it and alerts them to stay safe.
User also can request anytime they want by pressing coressponding button.
All the information about the user(their username, chat id and location) is stored in a SQL database

<h1>Usage</h1>

To start using the script, firtst you need to get API keys from OpenWeather and create a Telegram bot.
<bold>How to get Telegram API?</bold> To make a bot in telegram and get api key for it, you will need to use
BotFather. Just use the start command and follow the instructions.
<img src="/Media/Screenshot 2024-10-18 005412.png" />

<bold>How to get OpenWeahter API?</bold> To make an API key from OpenWeather, so you will be able to make calls
to the website to get weather information, you just need to go their website and register. After registration they
will give you an API key for free use.
<img src="/Media/Screenshot 2024-10-18 012102.png" />

After acquiring the API keys, you need to make an .env file and write down API keys there, name the file "container.env"
and API keys like in below
<img src="/Media/Screenshot 2024-10-18 012757.png" />

After this, run the "dbs.py" to initialize the database, where the data is going to be stored
<img src="/Media/Screenshot 2024-10-18 013336.png">

Finally, you ca run the main code, and it should work properly

<bold>Note:</bold>you might need to download some libraries

<h1>Technologies used<h1>
Technological technologies

Frame processing