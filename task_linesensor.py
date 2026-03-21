# LAB 0x05 MAIN

from pyb import Pin, millis, delay, elapsed_millis
from linesensor import LineSensor
import micropython

S0_INIT = micropython.const(0)
S1_RUN  = micropython.const(1)


class task_linesensor:
    """Task that reads the line sensor and publishes a steering correction."""

    def __init__(self, linesensor, leftGo, rightGo, steerGain, lineCorr):
        """
        Initialize the line sensor task.

        Args:
            linesensor: LineSensor object used to compute the centroid.
            leftGo: Shared flag indicating whether the left motor is active.
            rightGo: Shared flag indicating whether the right motor is active.
            steerGain: Shared steering gain used to scale centroid error.
            lineCorr: Shared output correction value for line following.
        """
        self.state = S0_INIT
        self.linesensor = linesensor

        self.leftGo = leftGo
        self.rightGo = rightGo

        self._cent_t0 = None
        self._was_running = False

        self._steerGain = steerGain
        self._lineCorr = lineCorr

    def run(self):
        """
        Run one iteration of the line sensor task.

        This generator monitors whether the robot is actively driving, reads
        the line centroid when running, and publishes a steering correction
        based on the centroid and steering gain.

        Yields:
            int: The current state of the line sensor task.
        """
        while True:

            if self.state == S0_INIT:
                self.state = S1_RUN

            elif self.state == S1_RUN:

                running = (self.leftGo.get() or self.rightGo.get())

                if running and not self._was_running:
                    self._cent_t0_ms = millis()

                self._was_running = running

                if running:
                    c = self.linesensor.centroid()
                    g = self._steerGain.get()

                    if c is None:
                        d = 0.0
                    else:
                        d = g * c

                    self._lineCorr.put(d)
                else:
                    self._lineCorr.put(0)

            yield self.state