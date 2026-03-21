# BUMP SENSOR TASK

import micropython
from time import ticks_us, ticks_diff

S0_INIT = micropython.const(0)
S1_RUN  = micropython.const(1)


class task_bumpsensor:
    """Task that monitors the bump sensor and publishes a debounced bump flag."""

    def __init__(self, bumpsensor, bumpFlag, lockout_us=30000):
        """
        Initialize the bump sensor task.

        Args:
            bumpsensor: BumpSensor driver object.
            bumpFlag: Shared flag used to notify other tasks of a bump event.
            lockout_us: Debounce lockout time in microseconds after a trigger.
        """
        self.state = S0_INIT
        self.bumpsensor = bumpsensor
        self.bumpFlag = bumpFlag

        self.lockout_us = lockout_us
        self._waiting = False
        self._tstart = 0

    def run(self):
        """
        Run one iteration of the bump sensor task.

        This generator watches for pending bump events from the interrupt-driven
        bump sensor, sets the shared bump flag, and applies a lockout period to
        prevent repeated triggers from switch bounce.

        Yields:
            int: The current state of the bump sensor task.
        """
        while True:

            if self.state == S0_INIT:
                self._waiting = False
                self.bumpsensor.pending = False
                self.bumpsensor.rearm()
                self.state = S1_RUN

            elif self.state == S1_RUN:
                # accept bump immediately on first edge
                if self.bumpsensor.pending and not self._waiting:
                    self.bumpFlag.put(1)        # mastermind clears it
                    self._waiting = True
                    self._tstart = self.bumpsensor.t0
                    self.bumpsensor.pending = False

                # lockout window prevents bounce/repeat triggers
                if self._waiting and ticks_diff(ticks_us(), self._tstart) >= self.lockout_us:
                    self._waiting = False
                    self.bumpsensor.rearm()

            yield self.state