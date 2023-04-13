""" Main programm for reading knx bus traffic"""
import serial
import logging
import binascii
import requests

import knx_monitor

DEVICE = "/dev/ttyAMA0"
BAUDRATE = 19200
CHARACTER_SIZE = serial.EIGHTBITS
PARITY = serial.PARITY_EVEN
STARTBYTE = b"\x68"
STOPBYTE = b"\x16"

logging.basicConfig(level=logging.DEBUG)

''' BAOS 777 monitor '''
BAOS_777 = True

import websocket
import _thread
import time
import rel

import json
import requests
import time

def get_token():
    # log in to BAOS 777
    # token is global for all http requests, not only websockets
    done = False
    while not done:
        try:
            r = requests.post('http://10.110.16.63/rest/login', json={"password": "admin", "username": "admin"})
        

            # if auth fails, we get 429 with e.g. {"login_blocked_for_s":24}'
            if r.status_code == 200:
                # token could be empty or too short 
                if len(r.text) > 10:
                    token = r.text  
                    done = True
                else:
                    logging.critical(f"token={r.text} invalid?")
            else:
                logging.critical(f"Unable to authenticate BAOS 777 websocket with admin user!")
                logging.critical(f"BAOS returned: {r.text}")
                time.sleep(2)
        except:
            logging.critical(f"Unable to connect to BAOS 777!")
            pass
    logging.info(f"New BAOS token: {token}")
    return token

class BAOSMonitor:
    def __init__(self):  
        websocket.enableTrace(True)
        while True:
            self.connect()
            # wait until next try
            logging.info(f"Connect BAOS Webservice again.")
            time.sleep(2)

    def connect(self):
        print('connect')

        self.token = get_token()
        WS_HOST = 'ws://10.110.16.63/websocket'
        URL = '{}?token={}'.format(WS_HOST, self.token)

        try:
            self.ws = websocket.WebSocketApp(URL,
                                            on_open=self.on_open,
                                            on_message=self.on_message,
                                            on_error=self.on_error,
                                            on_close=self.on_close
                                            )

            # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
            self.ws.run_forever(#dispatcher=rel, reconnect=5,
                                ping_interval=60, ping_timeout=2, ping_payload="keep alive")  
            #rel.signal(2, rel.abort)  # Keyboard Interrupt
            #rel.dispatch()
        except Exception:
            logging.critical(f"BAOS Webservice down, try reconnect")
            pass 
        print('done')
        
    def on_message(self, ws, message):
        print(F'Message:::{message}')
     
        # message should be a json message already.
        message = json.loads(message)
        knx_monitor.DBActions.monitor_status_save_777(message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        rel.abort()
        print("### re-connect ###")
        self.ws.close()
        self.ws.keep_running = False

        self.connect()

    def on_open(self, ws):
        print("Opened connection")
        time.sleep(2)
    
def main_777():
    baos_777_ws = BAOSMonitor()
    print('not blocked')
    
def main():
    with serial.Serial(DEVICE, BAUDRATE, CHARACTER_SIZE, PARITY) as connection:
        telegram_old = b"\xFF"
        while True:
            # read frame
            connection.read_until(STARTBYTE)
            telegram = bytearray(STARTBYTE)
            telegram.extend(connection.read_until(STOPBYTE))
            logging.info(f"Incoming ft1.2 telegram: {binascii.hexlify(telegram)}")

            if telegram[knx_monitor.OctectIndex.MESSAGE_CODE] == knx_monitor.MessageCode.L_DATA_CON:
                groupaddress = knx_monitor.get_groupaddress(telegram).get("formatted")
                logging.info(f"for groupaddress {groupaddress}")
                datapoint_type = knx_monitor.get_groupaddress_info(groupaddress).get("datapoint type")
                value = knx_monitor.get_value(telegram, datapoint_type).get("formatted")
                logging.info(f"with value {value}")

                if telegram_old != telegram:
                    knx_gateway = "localhost:8000"
                    logging.error("update led subscriptors")
                    requests.get(f"http://{knx_gateway}/knx/update_led_subscriptors/{groupaddress}/{value}")

                    #knx_monitor.DBActions.monitor_status_save(telegram)
                    knx_monitor.DBActions.status_save(telegram)
                    telegram_old = telegram


if __name__ == "__main__":
    if BAOS_777:
        main_777()
    else:
        main()
