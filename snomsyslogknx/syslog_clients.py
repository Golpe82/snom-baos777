# TODO: this should be managed in django ui (save this in the portal db)

# SYSLOG_CLIENTS = {
#     "10.110.16.50": {
#         "label": "Simóns desk",
#         "min brightness": 30,
#         "max brightness": 45,
#         "switch groupaddress": "2/1/10",
#         "relative dim groupaddress": "2/1/20",
#         "send celsius groupaddress": "5/1/10",
#     },
#     "10.110.16.79": {
#         "label": "Simóns window",
#         "min brightness": 30,
#         "max brightness": 45,
#         "switch groupaddress": "2/1/10",
#         "relative dim groupaddress": "2/1/20",
#         "send celsius groupaddress": "5/1/10",
#     },
#     "10.110.16.65": {
#         "label": "Localhost",
#         "min brightness": 100,
#         "max brightness": 110,
#         "switch groupaddress": "2/1/10",
#         "relative dim groupaddress": "2/1/20",
#         "send celsius groupaddress": "5/1/10",
#     }
# }

SYSLOG_CLIENTS = {
    "192.168.178.20": {
        "is D735": True,
        "label": "Simóns desk",
        "min brightness": 100,
        "max brightness": 150,
        "switch groupaddress": "1/2/20",
        "relative dim groupaddress": "1/2/21",
        "send lux groupaddress": "4/2/10",
        "max lux delta": 10.,
        "send celsius groupaddress": "4/1/10",
        "max celsius delta": 1.0,
    },
    "192.168.178.26": {
        "is D735": False,
        "label": "Simóns desk",
        "min brightness": 30,
        "max brightness": 45,
        "switch groupaddress": "2/1/10",
        "relative dim groupaddress": "2/1/20",
        "send celsius groupaddress": "4/1/20",
        "max celsius delta": 1.0,
    },
    "192.168.178.37": {
        "is D735": False,
        "label": "Simóns desk",
        "min brightness": 100,
        "max brightness": 110,
        "switch groupaddress": "2/1/10",
        "relative dim groupaddress": "2/1/20",
        "send celsius groupaddress": "4/1/30",
        "max celsius delta": 1.0,
    },
}
