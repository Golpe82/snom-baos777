import requests
import logging
import time

DECT_ULE_GATEWAY = "10.110.16.101:8881"
KNX_GATEWAY = "localhost:1234"
BLIND_GROUPADDRESS = "6/1/10"
SWITCH_SOCKET_LEFT_GROUPADDRESS = "3/1/10"

class DECTULEActions:
    def control_blind(self, status):
        if status == "on":
            self._control_blind_up()
            time.sleep(2)
            self._switch_groupaddress_on(SWITCH_SOCKET_LEFT_GROUPADDRESS)
            
        elif status == "off":
            self._control_blind_down()
            time.sleep(2)
            self._switch_groupaddress_off(SWITCH_SOCKET_LEFT_GROUPADDRESS)
        else:
            raise ValueError(f"unknown status {status}")

    def _control_blind_down(self):
        down = f"http://{DECT_ULE_GATEWAY}/snom_ule_cmd/snom_send_cmd%2013%201%20516%201%202%2022"
        logging.info("sending down")
        requests.get(down)

    def _control_blind_up(self):
        up = f"http://{DECT_ULE_GATEWAY}/snom_ule_cmd/snom_send_cmd%2013%201%20516%201%201%2022"
        logging.info("sending up")
        requests.get(up)

    def _switch_groupaddress_on(self, groupaddress):
        on = f"http://{KNX_GATEWAY}/{groupaddress}-an"
        logging.info("switching on")
        requests.get(on)

    def _switch_groupaddress_off(self, groupaddress):
        off = f"http://{KNX_GATEWAY}/{groupaddress}-aus"
        logging.info("switching off")
        requests.get(off)
