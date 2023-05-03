# TODO: this should be managed in django ui (save this in the portal db)

SYSLOG_CLIENTS = {
    "10.110.16.50": {
        "label": "Simóns desk",
        "min brightness": 30,
        "max brightness": 45,
        "switch groupaddress": "2/1/10",
        "relative dim groupaddress": "2/1/20",
        "send celsius groupaddress": "5/1/10",
    },
    "10.110.16.110": {
        "label": "Visitor's desk",
        "min brightness": 30,
        "max brightness": 45,
        "switch groupaddress": "2/1/10",
        "relative dim groupaddress": "2/1/20",
        "send celsius groupaddress": "5/1/10",
    },
    "127.0.0.1": {
        "label": "Localhost",
        "min brightness": 100,
        "max brightness": 110,
        "switch groupaddress": "2/1/10",
        "relative dim groupaddress": "2/1/20",
        "send celsius groupaddress": "5/1/10",
    }
}
