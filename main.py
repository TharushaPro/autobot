import telethon, time, requests
from telethon import TelegramClient, events,Button
from datetime import datetime
from binance.client import Client
from binance.enums import SIDE_BUY, ORDER_TYPE_MARKET, SIDE_SELL
from funtions import CREATE_ORDER, LONG_TPSL, SHORT_TPSL,CLEAR_TRADES, NumberGame


#Telegram API Settings

api_id = '8563251'
api_hash = '4e8e50edf90e644157df063be5032bdf'
bt='7699871487:AAEGo7GZYdf4HmmKGLtCtlBaFky7jYlmHWs'
LOG_GROUP = -4756531806

#Binance API Settings

API_KEY = "eKOvJyv4OarT9LZ4Rj6nVm1P1VUKBB3ZWl1hVqvPHJIQJ1GCpOBIA1SwUVjPdZec"
API_SECRET = "EqTKlMGVjp4j0ld2oa60QO5qF489u5ksREefrNgcQrWkwnGKCxZYaaRoePAiMPQf"
symbol = "1000PEPEUSDT"

# Initialize the Binance Client and TG BOT CLIENT
client = Client(API_KEY, API_SECRET)
bot = TelegramClient('name', api_id, api_hash).start(bot_token=bt)

# Binance API Base URL
base_url = "https://fapi.binance.com"

# Endpoint for Klines
endpoint = "/fapi/v1/klines"

params = {
    "symbol": f"{symbol}",  # Trading pair
    "interval": "1m",          # 1-minute interval
    "limit": 3                 # Only the last candlestick
    }



@bot.on(events.NewMessage(pattern='/run'))
async def start(event):
    msg = event.message.text
    id =  event.chat_id
    if id != LOG_GROUP:
        await bot.send_message(id,"YOU ARE NOT AUTHORIZED")
        pass
    else:
        await bot.send_message(LOG_GROUP,"BOT STARTED")
        livecandle = 0
        usdt = 1
        tradeS_value = "n"
        while True:
            response = requests.get(base_url + endpoint, params=params)
            data = response.json()

            newcandle = data[1][0]
            if newcandle == livecandle:
                newcandle = data[2][0]

                if data[0][1] < data[1][4]:
                    try:
                        if tradeS_value == "n":
                            side = "BUY"
                            poside = "LONG"
                        else:
                            side = "SELL"
                            poside = "SHORT"

                        tp,sl,order = CREATE_ORDER(client,symbol, side, 50, usdt,poside)
                        x=f'''OLD CANDLE OPENING : {data[0][1]}
NEW CANDLE CLOSING : {data[1][4]}
RESULT : LONG / {tradeS_value}
TAKE PROFIT : {tp}
STOP LOSS : {sl}
AMOUNT : {usdt}'''
                        await bot.send_message(LOG_GROUP,x)
                        await bot.send_message(LOG_GROUP,str(order))
                        if tradeS_value == "n":
                            Result,tpslid,TRADEstatus = LONG_TPSL(client,tp,sl)
                        else:
                            Result,tpslid,TRADEstatus = SHORT_TPSL(client,tp,sl)
                        await bot.send_message(LOG_GROUP,str(Result))
                        final = CLEAR_TRADES(client,tpslid)
                        await bot.send_message(LOG_GROUP,str(final))
                        game = NumberGame()
                        usdt = game.process_input(TRADEstatus)["original_list_value"]
                        tradeS_value = game.process_input(TRADEstatus)["tradeS_value"]
                        response = requests.get(base_url + endpoint, params=params)

                    except Exception as e:
                        await bot.send_message(LOG_GROUP,str(e))
                        response = requests.get(base_url + endpoint, params=params)

                else:
                    try:
                        if tradeS_value == "n":
                            side = "SELL"
                            poside = "SHORT"
                        else:
                            side = "BUY"
                            poside = "LONG"
                        
                        tp,sl,order = CREATE_ORDER(client,symbol,side, 50, usdt, poside)

                        x=f'''OLD CANDLE OPENING : {data[0][1]}
NEW CANDLE CLOSING : {data[1][4]}
RESULT : SHORT / {tradeS_value}
TAKE PROFIT : {tp}
STOP LOSS : {sl}
AMOUNT : {usdt}'''
                        await bot.send_message(LOG_GROUP,x)
                        await bot.send_message(LOG_GROUP,str(order))
                        if tradeS_value == "n":
                            Result,tpslid,TRADEstatus = SHORT_TPSL(client,tp,sl)
                        else:
                            Result,tpslid,TRADEstatus = LONG_TPSL(client,tp,sl)
                        await bot.send_message(LOG_GROUP,str(Result))
                        final = CLEAR_TRADES(client,tpslid)
                        await bot.send_message(LOG_GROUP,str(final))
                        game = NumberGame()
                        usdt = game.process_input(TRADEstatus)["original_list_value"]
                        tradeS_value = game.process_input(TRADEstatus)["tradeS_value"]
                        response = requests.get(base_url + endpoint, params=params)

                    except Exception as e:
                        await bot.send_message(LOG_GROUP,str(e))
                        response = requests.get(base_url + endpoint, params=params)

            data = response.json()    
            livecandle = data[2][0]
            time.sleep(0.5)

print('BOT STARTED')
bot.run_until_disconnected()
