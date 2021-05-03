'''Handles frame payload depending on datapointtype'''
DPTS = {
    'DPT1': {
        'pattern': '^DPS?T-1-',
    },
    'DPT3': {
        'pattern': '^DPS?T-3-',
        'values': {
            'stop': 0x80,
            'decrease': range(0x81, 0x88),
            'increase': range(0x88, 0x8F+0x01)
        },
    },
    'DPT5': {
        'pattern': '^DPS?T-5-',
        'values': {
            'byte0': 0x80,
            'byte1': range(0x01, 0xFF)
        },
    },
}


class DptHandlers:
    def __init__(self, raw_value, dpt):
        self.raw_value = raw_value
        self.HANDLERS = {
            'DPT1': self.handle_DPT1(),
            'DPT3': self.handle_DPT3(),
        }
        self.value = self.HANDLERS.get(dpt)

    def handle_DPT1(self):
        VALUES = {'on': 0x81, 'off': 0x80}

        if self.raw_value == VALUES.get('on'):
            return 'on'

        elif self.raw_value == VALUES.get('off'):
            return 'off'

        else:
            return 'wrong value'

    def handle_DPT3(self):
        VALUES = {
            'stop': 0x80,
            'decrease': range(0x81, 0x88),
            'increase': range(0x88, 0x8F+0x01)
        }
        print(self.raw_value)

        step = self.raw_value & 0x07

        if self.raw_value in VALUES.get('increase'):
            return f'increase { step }'

        elif self.raw_value in VALUES.get('decrease'):
            return f'decrease { step }'

        elif self.raw_value == VALUES.get('stop'):
            return 'stop'

        else:
            return 'wrong value'
