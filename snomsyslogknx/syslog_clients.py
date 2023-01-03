# TODO: this should be managed in django ui (save this in the portal db)

SYSLOG_CLIENTS = {
    "10.110.16.59": {
        "label": "Simóns desk",
        "min brightness": 30,
        "max brightness": 45,
        "switch groupaddress": "1/1/20",
        "relative dim groupaddress": "1/1/21",
        "send celsius groupaddress": "1/6/1",
    },
    "10.110.16.110": {
        "label": "Visitor's desk",
        "min brightness": 30,
        "max brightness": 45,
        "switch groupaddress": "1/1/20",
        "relative dim groupaddress": "1/1/21",
        "send celsius groupaddress": "1/6/1",
    },
    "127.0.0.1": {
        "label": "Localhost",
        "min brightness": 100,
        "max brightness": 110,
        "switch groupaddress": "1/1/20",
        "relative dim groupaddress": "1/1/21",
        "send celsius groupaddress": "1/6/1",
    }
}
