from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
import math
import os
import json

SAVE_FILE = "game_state.txt"

def CREATE_ORDER(client,symbol, side, leverage, amount_usdt,poside):
    try:
        # Set leverage (isolated mode)
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        print(f"Leverage set to {leverage}x for {symbol}.")

        # Get symbol price
        ticker = client.futures_symbol_ticker(symbol=symbol)
        entry_price = float(ticker['price'])
        print(f"Entry Price: {entry_price}")

        # Calculate position quantity
        quantity = math.floor((amount_usdt / entry_price) * 100) / 100
        quantity = round(quantity*50,0)
        print(f"Quantity: {quantity}")

        # Place market order to open position
        order = client.futures_create_order(
            symbol=symbol,
            side=side,  # Buy to open a long position
            type="MARKET",
            quantity=quantity,
            positionSide=poside,  # Position side for hedging
            leverage=leverage   # Set leverage in the same request
        )

        positions = client.futures_position_information()
        entry_price = float(positions[0]["entryPrice"])

        # Calculate SL and TP prices
        if side == SIDE_BUY:  # Long Trade
            sl_price = entry_price * (1 - (15/(100*50)))
            tp_price = entry_price * (1 + (15/(100*50)))
        else:  # Short Trade
            sl_price = entry_price * (1 + (15/(100*50)))
            tp_price = entry_price * (1 - (15/(100*50)))


        return round(tp_price,6), round(sl_price,6), order


    except Exception as e:
        print(f"An error occurred: {e}")

        return f"ERROR : {e}"
    
def LONG_TPSL(client,tp,sl):
    #STOP LOSS
    order = client.futures_create_order(
    symbol="1000PEPEUSDT",
    side="SELL",
    type="STOP_MARKET",
    closePosition=True,
    stopprice = sl,
    positionSide="LONG"
    )
    slid = order["orderId"]

    #TAKE PROFIT
    order = client.futures_create_order(
    symbol="1000PEPEUSDT",
    side="SELL",
    type="TAKE_PROFIT_MARKET",
    closePosition=True,
    stopprice = tp,
    positionSide="LONG"
    )
    tpid = order["orderId"]
    STATUS = True
    while STATUS:
        ticker = client.futures_symbol_ticker(symbol="1000PEPEUSDT")
        live_price = float(ticker['price'])

        if (live_price>= tp):
            Result = "PROFIT"
            STATUS = False
            tpslid = slid
            TRADEstatus = "P"
        elif (live_price<= sl):
            Result = "LOSS"
            STATUS = False
            tpslid = tpid
            TRADEstatus = "L"
    return Result,int(tpslid),TRADEstatus
    


def SHORT_TPSL(client,tp,sl):
    #STOP LOSS
    order = client.futures_create_order(
    symbol="1000PEPEUSDT",
    side="BUY",
    type="STOP_MARKET",
    closePosition=True,
    stopprice = sl,
    positionSide="SHORT"
    )
    slid = order["orderId"]
    #TAKE PROFIT
    order = client.futures_create_order(
    symbol="1000PEPEUSDT",
    side="BUY",
    type="TAKE_PROFIT_MARKET",
    closePosition=True,
    stopprice = tp,
    positionSide="SHORT"
    )
    tpid = order["orderId"]
    STATUS = True
    while STATUS:
        ticker = client.futures_symbol_ticker(symbol="1000PEPEUSDT")
        live_price = float(ticker['price'])
        if (live_price<= tp):
            Result = "PROFIT"
            tpslid = slid
            STATUS = False
            TRADEstatus = "P"
        elif (live_price>= sl):
            Result = "LOSS"
            tpslid = tpid
            STATUS = False
            TRADEstatus = "L"

    return Result,int(tpslid),TRADEstatus


def CLEAR_TRADES(client,tpslid):
            try:
                client.futures_cancel_order(symbol="1000PEPEUSDT", orderId=tpslid)
                final = (f"Cancelled TAKE PROFIT ORDER/STOP LOSS ORDER order for 1000PEPEUSDT with Order ID: {tpslid}")
            except Exception as e:
                final = (f"Failed to cancel order {tpslid} for 1000PEPEUSDT: {e}")
            return final


def save_state(state):
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f)

def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return None

class NumberGame:
    def __init__(self):
        # Initialize the lists
        self.list1 = [1, 2, 4, 7, 11, 16]
        self.list2 = [5, 7, 11, 16, 22, 29, 37]
        self.list3 = [16, 22, 29, 37, 47]
        self.TradeS = ['i', 'i', 'n', 'n']  # New list

        # Load saved state if available
        saved_state = load_state()
        if saved_state:
            self.current_list = saved_state["current_list"]
            self.current_index = saved_state["current_index"]
            self.cycle_number = saved_state["cycle_number"]
            self.p_press_count = saved_state["p_press_count"]
            self.moves_in_cycle = saved_state["moves_in_cycle"]
            self.trades_index = saved_state.get("trades_index", 0)
            self.trades_reset = saved_state.get("trades_reset", True)
        else:
            # Initial game state
            self.current_list = 1
            self.current_index = 0
            self.cycle_number = 1
            self.p_press_count = 0
            self.moves_in_cycle = 0
            self.trades_index = 0  # Current index for TradeS
            self.trades_reset = True  # Flag to indicate TradeS should reset

    def get_current_list(self):
        if self.current_list == 1:
            return self.list1
        elif self.current_list == 2:
            return self.list2
        else:
            return self.list3

    def get_start_index(self, list_num):
        return 0 if list_num == 1 else 1

    def get_current_value(self):
        return self.get_current_list()[self.current_index]

    def process_input(self, key):
        key = key.upper()

        # Handle TradeS behavior
        trades_value = None
        if key == 'L':
            if self.trades_reset:
                trades_value = self.TradeS[self.trades_index]
                self.trades_index = (self.trades_index + 1) % len(self.TradeS)  # Cycle through TradeS

        if key == 'P':
            if self.trades_reset:
                self.trades_index = 0  # Reset TradeS to the beginning
                trades_value = "n"

        # Handle original lists behavior
        if key == 'L':
            self.p_press_count = 0
            self.moves_in_cycle += 1

            # If at the end of the current list
            if self.current_index == len(self.get_current_list()) - 1:
                if self.current_list < 3:  # Move to the next list if possible
                    self.current_list += 1
                    self.current_index = self.get_start_index(self.current_list)
                    self.cycle_number = 1
                    self.moves_in_cycle = 0
            else:
                self.current_index += 1

        elif key == 'P':
            self.p_press_count += 1
            if self.p_press_count == 1:
                # Move back one index if possible
                if self.current_index > 0:
                    self.current_index -= 1
            elif self.p_press_count == 2:
                if self.cycle_number == 2 and self.current_list > 1:
                    # Switch to the previous list
                    self.current_list -= 1
                    self.current_index = self.get_start_index(self.current_list)
                    self.cycle_number = 1
                    self.moves_in_cycle = 0
                else:
                    # Reset to the start of the current list
                    self.current_index = self.get_start_index(self.current_list)
                    self.cycle_number = 2 if self.cycle_number == 1 else 1
                    self.moves_in_cycle = 0
                self.p_press_count = 0

        # Save the state
        save_state({
            "current_list": self.current_list,
            "current_index": self.current_index,
            "cycle_number": self.cycle_number,
            "p_press_count": self.p_press_count,
            "moves_in_cycle": self.moves_in_cycle,
            "trades_index": self.trades_index,
            "trades_reset": self.trades_reset,
        })

        # Return both values: from the original lists and TradeS
        return {
            "original_list_value": self.get_current_value(),
            "tradeS_value": trades_value or self.TradeS[self.trades_index - 1],
        }