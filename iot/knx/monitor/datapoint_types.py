'''Handles frame payload depending on datapointtype'''
DPTS = {
    'DPT1': '^DPS?T-1-',
    'DPT3': '^DPS?T-3-',
    'DPT5': '^DPS?T-5-',
}


class DptHandlers:
    def __init__(self, raw_value, dpt):
        self.raw_value = raw_value
        self.HANDLERS = {
            'DPT1': self.handle_DPT1(),
            'DPT3': self.handle_DPT3(),
            'DPT5': self.handle_DPT3(),
        }
        self.value = self.HANDLERS.get(dpt)

    def handle_DPT1(self):
        VALUES = {'on': 0x81, 'off': 0x80}

        for key, value in VALUES.items():
            if self.raw_value == value:
                return key

        return 'wrong value'

    def handle_DPT3(self):
        VALUES = {
            'stop': range(0x81),
            'decrease': range(0x81, 0x88),
            'increase': range(0x88, 0x8F+0x01)
        }

        step = self.raw_value & 0x07

        for key, value in VALUES.items():
            if self.raw_value in value:
                return f'{ key } { step }'

        return 'wrong value'

    def handle_DPT5(self):
        VALUES = {
            'byte0': 0x80,
            'byte1': range(0x01, 0xFF)
        }

        return 'not implemented'
