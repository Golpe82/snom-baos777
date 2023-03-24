"""Constants for KNX Django app"""
from enum import Enum

class PhoneModel:
    D335 = "D335"
    D385 = "D385"
    D713 = "D713"
    D717 = "D717"
    D735 = "D735"
    D785 = "D785"
    D862 = "D862"
    D865 = "D865"

class FkeyLEDNo(Enum):
    D335 = range(2, 10)
    D385 = range(2, 8)
    D713 = range(1, 5)
    D717 = range(5, 8)
    D735 = range(5, 13)
    D785 = range(5, 29)
    D862 = range(5, 13)
    D865 = range(5, 15)
