"""Module for BAOS 777 constants"""

class BAOS777Commands:
    NO_COMMAND = 0
    SET_VALUE = 1
    SEND_VALUE_ON_BUS = 2
    SET_VALUE_AND_SEND_ON_BUS = 3
    READ_VALUE_VIA_BUS = 4
    CLEAR_DATAPOINT_TRANSMISSION_STATE = 5

class DatapointValues:
    DPT1 = {"on": True,"off": False}
