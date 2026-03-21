"""User interface task for starting the course and reporting FSM state."""

from pyb import USB_VCP, UART
from task_share import Share, BaseShare, Queue
import micropython

S0_INIT = micropython.const(0)  # State 0 - initialization
S1_WAIT = micropython.const(1)  # State 1 - wait
S2_GO   = micropython.const(2)  # State 2 - go

UI_prompt = ">: "


class task_user:
    """Task that provides a simple serial user interface for course control."""

    def __init__(self, courseGo, fsmState):
        """
        Initialize the user task.

        Args:
            courseGo: Shared flag used to start or stop the course.
            fsmState: Share containing the current FSM state.
        """
        self._state: int = S0_INIT
        self._ser = USB_VCP()

        self._courseGo: Share = courseGo
        self._fsmState: Share = fsmState
        self._prevState = 0

        self._ser.write("User Task object instantiated\r\n")

    def run(self):
        """
        Run one iteration of the user interface task.

        This generator prints startup messages, reports when the course begins
        or stops, and displays FSM state changes over the serial connection.

        Yields:
            int: The current state of the user task.
        """
        while True:

            if self._state == S0_INIT:
                self._ser.write("Use blue button to start/stop\r\n")
                self._ser.write(UI_prompt)
                self._state = S1_WAIT

            elif self._state == S1_WAIT:
                if self._courseGo.get():
                    self._ser.write("GOING\r\n")
                    self._state = S2_GO

            elif self._state == S2_GO:
                fsmState = self._fsmState.get()
                if self._prevState != fsmState:
                    self._ser.write(f"CURRENT STATE: {fsmState}\r\n")
                    self._prevState = fsmState

                if not self._courseGo.get():
                    self._ser.write("STOPPING\r\n")
                    self._ser.write(UI_prompt)
                    self._state = S1_WAIT

            yield self._state