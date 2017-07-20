



#This code will not run without valid public and private keys entered on line 81





import websocket 
import thread
import time
import hmac
import hashlib
import datetime
import json
import csv

#Functions for generating the keys to the CEX  Websocket API
def create_signature(key, secret):  # (string key, string secret) 
        timestamp = int(time.time())  # UNIX timestamp in seconds
        string = "{}{}".format(timestamp, key)
        return timestamp, hmac.new(secret.encode(), string.encode(), hashlib.sha256).hexdigest()

def auth_request(key, secret):
        timestamp, signature = create_signature(key, secret)
        return json.dumps({'e': 'auth',
              'auth': {'key': key, 'signature': signature, 'timestamp': timestamp,}, 'oid': 'auth', })

#Functions for interacting with the Websocket API

def on_message(ws, message):

    '''Performs different actions based on the server responses'''

    try:
        message = json.loads(message)
    except:
        pass 

    if message['e'] == 'md_update':

        data = message['data']

        f = ''
        if data['pair'] == 'ETH:USD':
            f = 'data/eth-usd-orderbook.txt'
        elif data['pair'] == 'BTC:USD':
            f = 'data/btc-usd-orderbook.txt'
        elif data['pair'] == 'ETH:BTC':
            f = 'data/eth-btc-orderbook.txt'

        with open(f, 'a') as outfile:
            writer = csv.writer(outfile)
            writer.writerow([data[u'time'],data['id'],data['bids'],data['asks']])

    elif message['e'] == 'ping':
        ws.send('{"e":"pong"}')

    elif message['e'] == 'tick':
        with open('data/transaction-ticker.txt', 'a') as outfile:
            writer = csv.writer(outfile)
            writer.writerow([int(time.time()),message["data"][u'symbol2'],message["data"][ u'symbol1'],message["data"][u'price']])

    print(message)

sub_request = '{"e":"subscribe","rooms":["tickers"]}'
order_book_request_btc_usd = '{"e":"order-book-subscribe","data":{"pair":["BTC","USD"],"subscribe":true,"depth":100},"oid":"148400_order_book_btc_usd"}'
order_book_request_eth_usd = '{"e":"order-book-subscribe","data":{"pair":["ETH","USD"],"subscribe":true,"depth":100},"oid":"148400_order_book_eth_usd"}'
order_book_request_eth_btc = '{"e":"order-book-subscribe","data":{"pair":["ETH","BTC"],"subscribe":true,"depth":100},"oid":"148400_order_book_eth_btc"}'

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    
    ws.send(auth_request("PUT PRIVATE KEY HERE","PUT PUBLIC KEY HERE"))
    time.sleep(5)
    ws.send(sub_request) 
    ws.send(order_book_request_eth_usd) 
    ws.send(order_book_request_btc_usd) 
    ws.send(order_book_request_eth_btc) 


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.cex.io/ws/",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
