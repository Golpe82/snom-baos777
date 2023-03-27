"""Constants for KNX Django app"""
from dataclasses import dataclass

class PhoneModel:
    D335 = "D335"
    D385 = "D385"
    D713 = "D713"
    D717 = "D717"
    D735 = "D735"
    D785 = "D785"
    D862 = "D862"
    D865 = "D865"

@dataclass
class FkeyLEDNo:
    D335: range = range(2, 10)
    D385: range = range(2, 8)
    D713: range = range(1, 5)
    D717: range = range(5, 8)
    D735: range = range(5, 13)
    D785: range = range(5, 29)
    D862: range = range(5, 37)
    D865: range = range(5, 15)
