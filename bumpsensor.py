# BUMP SENSOR DRIVER

from pyb import Pin, ExtInt
from time import ticks_us

class BumpSensor:
    """Active-low bump input: ISR latches pending + disables IRQ."""
    def __init__(self, pin_name):
        self.pin = Pin(pin_name, Pin.IN, Pin.PULL_UP)
        self.pending = False
        self.t0 = 0
        self.ext = ExtInt(self.pin, ExtInt.IRQ_FALLING, Pin.PULL_UP, self._isr)

    def _isr(self, line):
        self.pending = True
        self.t0 = ticks_us()
        self.ext.disable()      # prevent ISR spam

    def rearm(self):
        self.ext.enable()

    