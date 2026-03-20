# BUMP SENSOR TASK

import micropython
from time import ticks_us, ticks_diff

S0_INIT = micropython.const(0)
S1_RUN  = micropython.const(1)

class task_bumpsensor:
    def __init__(self, bumpsensor, bumpFlag, lockout_us=30000):
        self.state = S0_INIT
        self.bumpsensor = bumpsensor
        self.bumpFlag = bumpFlag

        self.lockout_us = lockout_us
        self._waiting = False
        self._tstart = 0

    def run(self):
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