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
        
        # Load saved state if available
        saved_state = load_state()
        if saved_state:
            self.current_list = saved_state["current_list"]
            self.current_index = saved_state["current_index"]
            self.cycle_number = saved_state["cycle_number"]
            self.p_press_count = saved_state["p_press_count"]
            self.moves_in_cycle = saved_state["moves_in_cycle"]
        else:
            # Initial game state
            self.current_list = 1
            self.current_index = 0
            self.cycle_number = 1
            self.p_press_count = 0
            self.moves_in_cycle = 0

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
        
        if key == 'L':
            self.p_press_count = 0
            self.moves_in_cycle += 1
            
            # If we're at the end of the current list
            if self.current_index == len(self.get_current_list()) - 1:
                if self.current_list < 3:
                    self.current_list += 1
                    self.current_index = self.get_start_index(self.current_list)
                    self.cycle_number = 1  # Reset to first cycle in new list
                    self.moves_in_cycle = 0
            else:
                self.current_index += 1
                
        elif key == 'P':
            self.p_press_count += 1
            
            if self.p_press_count == 1:
                # First P press - move back one index if possible
                if self.current_index > 0:
                    self.current_index -= 1
                    
            elif self.p_press_count == 2:
                if self.cycle_number == 2 and self.current_list > 1:
                    # In cycle 2 and not in first list - go to previous list
                    self.current_list -= 1
                    self.current_index = self.get_start_index(self.current_list)
                    self.cycle_number = 1
                    self.moves_in_cycle = 0
                else:
                    # Go to current list's start position
                    self.current_index = self.get_start_index(self.current_list)
                    self.cycle_number = 2 if self.cycle_number == 1 else 1
                    self.moves_in_cycle = 0
                self.p_press_count = 0

        # Save the state after processing input
        save_state({
            "current_list": self.current_list,
            "current_index": self.current_index,
            "cycle_number": self.cycle_number,
            "p_press_count": self.p_press_count,
            "moves_in_cycle": self.moves_in_cycle,
        })
        return self.get_current_value()