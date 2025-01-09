import telethon, time
from telethon import TelegramClient, events,Button
import requests
from datetime import datetime
from binance.client import Client
from binance.enums import SIDE_BUY, ORDER_TYPE_MARKET, SIDE_SELL
from funtions import CREATE_ORDER, LONG_TPSL, SHORT_TPSL,CLEAR_TRADES, NumberGame


api_id = '8563251'
api_hash = '4e8e50edf90e644157df063be5032bdf'
bt='7683455009:AAEbd6Hn2dm24iw2qtqaw8N86h_P6WcUrIo'
 
API_KEY = "eKOvJyv4OarT9LZ4Rj6nVm1P1VUKBB3ZWl1hVqvPHJIQJ1GCpOBIA1SwUVjPdZec"
API_SECRET = "EqTKlMGVjp4j0ld2oa60QO5qF489u5ksREefrNgcQrWkwnGKCxZYaaRoePAiMPQf"

# Initialize the Binance Client and TG BOT CLIENT
client = Client(API_KEY, API_SECRET)
bot = TelegramClient('name', api_id, api_hash).start(bot_token=bt)

# Binance API Base URL
base_url = "https://fapi.binance.com"

# Endpoint for Klines
endpoint = "/fapi/v1/klines"

@bot.on(events.NewMessage(pattern='/coin'))
async def start(event):
    msg = event.message.text
    sender = await event.get_sender()
    uid = sender.id
    await event.reply("STARTED")
    try:
        sym = msg[6:].upper()
        symbol = sym+'USDT'
    except:
        symbol = 'NON'

    params = {
    "symbol": f"{symbol}",  # Trading pair
    "interval": "1m",          # 1-minute interval
    "limit": 3                 # Only the last candlestick
    }

    # Make the GET request
    livecandle = 0
    usdt = 1
    while True:
        response = requests.get(base_url + endpoint, params=params)
        data = response.json()

        newcandle = data[1][0]
        if newcandle == livecandle:
            newcandle = data[2][0]
            if data[0][1] < data[1][4]:
                try:
                    tp,sl,order = CREATE_ORDER(client,symbol, "BUY", 50, usdt,"LONG")
                    x=f'''OLD CANDLE OPENING : {data[0][1]}
NEW CANDLE CLOSING : {data[1][4]}
RESULT : LONG
TAKE PROFIT : {tp}
STOP LOSS : {sl}'''
                    await event.reply(str(x))
                    await event.reply(str(order))
                    Result,tpslid,TRADEstatus = LONG_TPSL(client,tp,sl)
                    await event.reply(str(Result))
                    final = CLEAR_TRADES(client,tpslid)
                    await event.reply(str(final))
                    game = NumberGame()
                    usdt = game.process_input(TRADEstatus)

                except Exception as e:
                    await event.reply(str(e))

            else:
                try:
                    tp,sl,order = CREATE_ORDER(client,symbol,"SELL", 50, usdt, "SHORT")

                    x=f'''OLD CANDLE OPENING : {data[0][1]}
NEW CANDLE CLOSING : {data[1][4]}
RESULT : SHORT
TAKE PROFIT : {tp}
STOP LOSS : {sl}'''
                    await event.reply(str(x))
                    await event.reply(str(order))
                    Result,tpslid,TRADEstatus = SHORT_TPSL(client,tp,sl)
                    await event.reply(str(Result))
                    final = CLEAR_TRADES(client,tpslid)
                    await event.reply(str(final))
                    game = NumberGame()
                    usdt = game.process_input(TRADEstatus)

                except Exception as e:
                    await event.reply(str(e))
        data = response.json()    
        livecandle = data[2][0]
        time.sleep(0.5)


print('BOT STARTED')
bot.run_until_disconnected()