''' This file demonstrates an example UI task using a custom class with a
    run method implemented as a generator
'''
from pyb import USB_VCP, UART
from task_share import Share, BaseShare, Queue
import micropython

S0_INIT = micropython.const(0) # State 0 - initialiation
S1_WAIT = micropython.const(1) # State 1 - wait
S2_GO   = micropython.const(2) # State 2 - go

UI_prompt = ">: "

class task_user:

    def __init__(self, courseGo, fsmState):
        
        self._state: int          = S0_INIT     

        self._ser: stream         = USB_VCP()

        self._courseGo: Share     = courseGo     # to command the course to start
        self._fsmState: Share     = fsmState     # current state of the FSM
        self._prevState = 0
        self._ser.write("User Task object instantiated\r\n")

    def run(self):
        
        while True:
            
            if self._state == S0_INIT: # Init state: Print menu
                self._ser.write("Use blue button to start/stop\r\n")
                self._ser.write(UI_prompt)
                self._state = S1_WAIT

            elif self._state == S1_WAIT: # Wait for UI commands
                '''
                # Wait for at least one character in serial buffer
                if self._ser.any():
                    # Read the character and decode it into a string
                    inChar = self._ser.read(1).decode()
                    if inChar in {"g", "G"}:
                        self._ser.write("GOING\r\n"
                                        "Press 'S' to stop.\r\n")
                        self._ser.write(UI_prompt)
                        self._courseGo.put(True)
                        self._state = S2_GO
                '''
                if self._courseGo.get():
                    self._ser.write("GOING\r\n")
                    self._state = S2_GO

            elif self._state == S2_GO:
                fsmState = self._fsmState.get()
                if self._prevState != fsmState:
                    self._ser.write(f"CURRENT STATE: {fsmState}\r\n")
                    self._prevState = fsmState
                '''
                if self._ser.any():
                    # Read the character and decode it into a string
                    inChar = self._ser.read(1).decode()
                    if inChar in {"s", "S"}:
                        self._courseGo.put(False)
                        self._ser.write("STOPPING\r\n"
                                        "Press 'G' to go!\r\n")
                        self._ser.write(UI_prompt)
                        self._state = S1_WAIT
                '''
                if not self._courseGo.get():
                    self._ser.write("STOPPING\r\n")
                    self._ser.write(UI_prompt)
                    self._state = S1_WAIT

            yield self._state