import kite as kite
import os

import pytz
from dateutil.rrule import rrule, WEEKLY, TH
from flask import *
import datetime
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from tradingview_ta import TA_Handler, Interval

# from kiteconnect import KiteConnect

import acctkn
from kite_trade import KiteApp

att = acctkn.att()
ap = acctkn.atp()
app = Flask(__name__)
# kite = KiteConnect(api_key=ap)
# apiToken = os.getenv("APITOKEN")
apiToken = "9LBRla7cQGh74Mt5imAVALeSdarTy7+vxAjS7np8tgkn+zW8AiLgIvLvKncbr0nP8TbAxi5SK01AsDi52UExhNzXWQctk0yI7lZxBNx/bZ+VGrVnkz9rrA=="
# kite.set_access_token(att)
kite = KiteApp(enctoken=apiToken)

isTradeAllowed = True
option_data = {}
current_expiry = ""
index_global = "NIFTY"
is_monthly_expiry = False
tradingsymbol = 'NSE:NIFTY 50'
#lots = os.getenv("LOTS")
lots=3
qty = 50 * int(lots)
#targetPoints = os.getenv("TARGET")
targetPoints=10
currentPremiumPlaced = ""
currentOrderID = ""
print("lots")
print(lots)
print(targetPoints)
print("++++++++")


# Basic calls
# print(kite.margins())
# print(kite.orders())
# print(kite.positions())
# print(kite.instruments("NFO"))
# kite.orders()

def getnsedata():
    try:
        global option_data
        df = pd.DataFrame(kite.instruments())
        df = df[(df.name == index_global)]
        df = sorted(df.expiry.unique())
        option_data[0] = str(datetime.datetime.strptime(str(df[0]), '%Y-%m-%d').strftime('%d-%b-%Y'))
        option_data[1] = str(datetime.datetime.strptime(str(df[1]), '%Y-%m-%d').strftime('%d-%b-%Y'))
        print(option_data)
    except BaseException as e:
        print("exception in getNseData Kite instruments  -----  " + str(e))


def getExpiryList():
    try:
        if option_data != "":
            global current_expiry
            current_expiry = option_data[0]
            print("Current Expiry = " + str(current_expiry))
            next_expiry = option_data[1]

            if (str(current_expiry).split("-")[1] != (str(next_expiry).split("-")[1])):
                global is_monthly_expiry
                is_monthly_expiry = True
            return current_expiry
    except BaseException as e:
        print("exception in getExpiryList  -----  " + str(e))


def getExistingOrders():
    try:
        print("Existing Orders")
        print(kite.orders())
        return kite.orders()
    except BaseException as e:
        print("exception in getExistingOrders  -----  " + str(e))


def placeCallOption(message):
    try:
        if isTradeAllowed:
            exitOrder(message)
            # rsiValue = round(getCurrentRSI())
            # if rsiValue > 50:
            optionToBuy = getTradingSymbol() + str(getCurrentAtm() - 200) + "CE"
            global currentPremiumPlaced
            currentPremiumPlaced = optionToBuy
            print("Current premium  = " + str(currentPremiumPlaced))
            order_id = kite.place_order(tradingsymbol=optionToBuy, variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=qty,
                                        order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
            if order_id["status"] == "success":
                if order_id["data"]["order_id"] != "":
                    optionLtp = getLTPForOption("Option For LimitOrder")
                    target = int(optionLtp) + int(targetPoints)
                    sell_order = kite.place_order(tradingsymbol=optionToBuy, variety=kite.VARIETY_REGULAR,
                                                  exchange=kite.EXCHANGE_NFO,
                                                  transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=qty,
                                                  price=target,
                                                  order_type=kite.ORDER_TYPE_LIMIT, product=kite.PRODUCT_MIS)
                    print("*** Buy Order Details ***")
                    print(order_id)
                    print(currentPremiumPlaced + " call Option")
                    getLTPForOption("Buy  -- " + message)
                    print("*** Sell Order Details ***")
                    print(sell_order)
                    global currentOrderID
                    currentOrderID = sell_order["data"]["order_id"]
                    print("Sell order placed with target || Order ID = " + str(currentOrderID))
                    print("target price === " + str(target))
            else:
                print(order_id)
        # else:
        #    print("RSI value is not greater tha 50|| Current RSI = "+ str(rsiValue))
        else:
            print('Trading is blocked in server')
    except BaseException as e:
        print("exception in placeCallOption ---- " + str(e))


def placePutOption(message):
    try:
        if isTradeAllowed:
            exitOrder(message)
            # rsiValue = round(getCurrentRSI())
            # if rsiValue < 50:
            optionToBuy = getTradingSymbol() + str(getCurrentAtm() + 200) + "PE"
            global currentPremiumPlaced
            currentPremiumPlaced = optionToBuy
            order_id = kite.place_order(tradingsymbol=optionToBuy, variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=qty,
                                        order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
            if order_id["status"] == "success":
                if order_id["data"]["order_id"] != "":
                    currentPremiumPlaced = optionToBuy
                    optionLtp = getLTPForOption("Option For LimitOrder")
                    target = int(optionLtp) + int(targetPoints)
                    sell_order = kite.place_order(tradingsymbol=optionToBuy, variety=kite.VARIETY_REGULAR,
                                                  exchange=kite.EXCHANGE_NFO,
                                                  transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=qty,
                                                  price=target,
                                                  order_type=kite.ORDER_TYPE_LIMIT, product=kite.PRODUCT_MIS)
                    print("*** Buy Order Details ***")
                    print(order_id)
                    print(currentPremiumPlaced + " Put Option")
                    getLTPForOption("Buy  -- " + message)
                    print("*** Sell Order Details ***")
                    print(sell_order)
                    global currentOrderID
                    currentOrderID = sell_order["data"]["order_id"]
                    print("Sell order placed with target || Order ID = " + str(currentOrderID))
                    print("target price === " + str(target))
            else:
                print(order_id)
        # else:
        #    print("Rsi is not less than 50 || Current RSI = " + str(rsiValue))
        else:
            print("Trading is blocked in server")
    except BaseException as e:
        print("exception in placePutOption ----- " + str(e))


def exitOrder(message):
    try:
        global currentPremiumPlaced
        print(currentPremiumPlaced)
        if currentPremiumPlaced != "":
            if currentOrderID != "":
                print(currentPremiumPlaced)
                order_id = kite.modify_order(order_id=currentOrderID, variety=kite.VARIETY_REGULAR,
                                             quantity=qty,
                                             order_type=kite.ORDER_TYPE_MARKET)
                print(order_id)
                print(currentPremiumPlaced + "exit order")
                getLTPForOption("exit -- " + message)
                currentPremiumPlaced = "No Current Orders"
        print(currentPremiumPlaced)

    except BaseException as e:
        print("exception in exitOrder ---- " + str(e))


def getCurrentAtm():
    try:
        niftyLTP = (kite.ltp(tradingsymbol)).get(tradingsymbol).get('last_price')
        print("Nifty current value = " + str(niftyLTP))
        niftySpot = 50 * round(niftyLTP / 50)
        print("Nifty spot value = " + str(niftySpot))
        return niftySpot
    except BaseException as e:
        print("exception in getCurrentAtm  -----  " + str(e))


def getTradingSymbol():
    try:
        getExpiryList()
        global symbol
        today = datetime.date.today()
        year = str(today.year)[2:4]

        if is_monthly_expiry:
            month = str(current_expiry.split("-")[1]).upper()
            symbol = index_global + year + month
            print(symbol)
        else:
            # month = str(current_expiry.split("-")[1]).upper()[0]
            # currentMonth = datetime.datetime.now().month

            monthList = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6, Jul=7, Aug=8, Sep=9, Oct=10, Nov=11, Dec=12)
            month = str(current_expiry.split("-")[1])
            next_thursday = rrule(freq=WEEKLY, dtstart=today, byweekday=TH, count=1)[0]
            date = str(next_thursday)[8:10]
            symbol = "" + index_global + year + str(monthList[month]) + date
            print(symbol)
        return symbol
    except BaseException as e:
        print("exception in getTradingSymbol  -----  " + str(e))


def getLTPForOption(action):
    try:
        print("__________")
        ltp_str = json.dumps(kite.quote("NFO:" + currentPremiumPlaced))
        ltp = json.loads(ltp_str)["NFO:" + currentPremiumPlaced]["last_price"]
        print("tradebooklogs = " + currentPremiumPlaced + " \t " + action + " \t" + str(ltp) + "\t" + str(
            datetime.datetime.now()) + "\n")
        print("__________")
        return ltp
    except BaseException as e:
        print("exception in getLTPForOption  -----  " + str(e))


def checkIfOrderExists():
    try:
        position_string = json.dumps(getExistingOrders())
        position_json = json.loads(position_string)
        allDayPositions = position_json['day']
        print(allDayPositions)
        if allDayPositions != []:
            for position in allDayPositions:
                print(position['tradingsymbol'])
                if position['tradingsymbol'] == currentPremiumPlaced:
                    if position['quantity'] >= 0:
                        print(position['last_price'])
                        exitOrder("exit order")
        else:
            print("No day positions")
        print()
    except BaseException as e:
        print("exception in checkIfOrderExists  -----  " + str(e))


def getCurrentRSI():
    try:
        index = TA_Handler(
            symbol="NIFTY",
            screener="cfd",
            exchange="NSE",
            interval=Interval.INTERVAL_5_MINUTES,
        )
        currentRsi = index.get_analysis().indicators["RSI"]
        print(currentRsi)
        return currentRsi
    except BaseException as e:
        print("exception in getCurrentRSI  -----  " + str(e))


@app.route('/')
def index():
    return render_template('html/algoscalping.html')


@app.route('/exit', methods=["GET", "POST"])
def exitCurrentOrder():
    print("Exit Order")
    exitOrder("exit")
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + "Order Exited")


#######################
@app.route('/buy', methods=["GET", "POST"])
def buyCE():
    print("Entry CE")
    placeCallOption("CE")
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + "Order placed")


@app.route('/sell', methods=["GET", "POST"])
def buyPE():
    print("Entry PE")
    placePutOption("PE")
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + " Order placed")


# @app.route('/exit', methods=["GET", "POST"])
# def exit():
#     exitOrder("exit")
#     return render_template('html/algoscalping.html', option=currentPremiumPlaced + " Order placed")
@app.route('/settoggle/<message>', methods=["GET", "POST"])
def setToggle(message):
    print("Set toggle")
    global isTradeAllowed
    if message == "false":
        isTradeAllowed = False
    elif message == "true":
        isTradeAllowed = True
    print(isTradeAllowed)
    return render_template('html/algoscalping.html', option=isTradeAllowed)


@app.route('/getvalues', methods=["GET", "POST"])
def getvalues():
    allValues = {"currentPremiumPlaced": currentPremiumPlaced, "lots": lots, "targetPoints": targetPoints}
    return allValues


######################
scheduler = BackgroundScheduler(daemon=True, timezone=pytz.timezone('Asia/Calcutta'))
scheduler.add_job(getnsedata, 'cron', day_of_week='fri', hour=9, minute=3)
scheduler.start()
getnsedata()
getCurrentRSI()
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
