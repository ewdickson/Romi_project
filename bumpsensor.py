# BUMP SENSOR DRIVER

from pyb import Pin, ExtInt
from time import ticks_us


class BumpSensor:
    """Driver for an active-low bump sensor using an external interrupt."""

    def __init__(self, pin_name):
        """
        Initialize the bump sensor input and attach its interrupt handler.

        Args:
            pin_name: Pin connected to the bump sensor signal.
        """
        self.pin = Pin(pin_name, Pin.IN, Pin.PULL_UP)
        self.pending = False
        self.t0 = 0
        self.ext = ExtInt(self.pin, ExtInt.IRQ_FALLING, Pin.PULL_UP, self._isr)

    def _isr(self, line):
        """
        Interrupt callback that latches a bump event and disables the IRQ.

        Args:
            line: Interrupt line identifier passed by the callback.
        """
        self.pending = True
        self.t0 = ticks_us()
        self.ext.disable()      # prevent ISR spam

    def rearm(self):
        """Re-enable the interrupt after a bump event has been handled."""
        self.ext.enable()

    