''' This file demonstrates an example motor task using a custom class with a
    run method implemented as a generator
'''

from motor_driver import motor_driver
from encoder      import encoder
from task_share   import Share, Queue
from utime        import ticks_us, ticks_diff
import micropython

S0_INIT = micropython.const(0) # State 0 - initialiation
S1_WAIT = micropython.const(1) # State 1 - wait for go command
S2_RUN  = micropython.const(2) # State 2 - run closed loop control

class task_motor:

    def __init__(self,
                 mot: motor_driver, enc: encoder,
                 goFlag: Share,
                 kp, ki, setpoint,
                 s_meas: Share, u_volts: Share,
                 bumpFlag: Share,
                 flip_encoder, name):
        
        self._bumpFlag: Share = bumpFlag

        self._state: int        = S0_INIT       
        
        # Hardware
        self._mot: motor_driver = mot        
        self._enc: encoder      = enc        
        
        # Scheduler shares
        self._goFlag: Share     = goFlag     
        #self._dataValues: Queue = dataValues 
        #self._timeValues: Queue = timeValues  
        self._startTime: int    = 0          
        
        # Initialize controller

        self._kp = kp
        self._ki = ki
        self._setpoint = setpoint

        self._e_int = 0.0

        self._s_meas  = s_meas
        self._u_volts = u_volts

        self.flip_encoder = flip_encoder
        self.name = name
        
        print("Motor Task object instantiated")
        
    def run(self):
        '''
        Runs one iteration of the task
        '''
        
        while True:
            
            if self._state == S0_INIT: # Init state (can be removed if unneeded)
                # print("Initializing motor task")
                
                self._state = S1_WAIT

                # MOTORS GO ON STARTUP
                '''
                self._kp.put(150)
                self._ki.put(3)
                self._setpoint.put(0.1)
                self._goFlag.put(True)
                '''
                
            elif self._state == S1_WAIT: # Wait for "go command" state
                if self._goFlag.get():
                    self._startTime = ticks_us()

                    self._mot.enable()
                    self._e_int = 0.0

                    # HARDCODING GAINS EVERY TIME THE MOTOR STARTS AGAIN
                    # self._kp.put(150)
                    # self._ki.put(3)

                    self._state = S2_RUN
                
            elif self._state == S2_RUN: # Closed-loop control state

                if self._goFlag.get() == True:                
                    # Update encoder
                    self._enc.update() 
                    #print(self.name, "dt", self._enc.dt, "vel", self._enc.get_velocity())
                    
                    '''
                    print(self.name, 
                          "delta", self._enc.delta, 
                          "pos", self._enc.position, 
                          "dist", self.flip_encoder * self._enc.get_position())
                    '''                   

                    vel = self.flip_encoder * self._enc.get_velocity()                 # MADE NEGATIVE 2/24
                    dt = self._enc.dt

                    self._s_meas.put(self.flip_encoder * self._enc.get_position())      # FOR OBSERVER

                    if dt <= 0:
                        yield self._state
                        continue

                    # Controller
                    
                    Kp = self._kp.get()
                    Ki = self._ki.get()
                    SP = self._setpoint.get()

                    e = SP - vel

                    e_int_test = self._e_int + e * dt
                    effort = (Kp * e) + (Ki * e_int_test)

                    if -100 < effort < 100:
                        self._e_int = e_int_test

                    effort = (Kp * e) + (Ki * self._e_int)
                    effort = max(min(effort, 100), -100)
                    
                    self._mot.set_effort(effort)     

                    Vbatt = 9.0                                     # FOR OBSERVER, A GUESS
                    self._u_volts.put((effort / 100.0) * Vbatt)    

                else:
                    self._e_int = 0
                    self._mot.set_effort(0)
                    self._mot.disable()
                    self._state = S1_WAIT      
                
                '''
                # STOP IF BUMP SENSOR TRIPPED
                if self._bumpFlag.get():
                    self._mot.set_effort(0)
                    self._mot.disable()
                    self._goFlag.put(False)
                    self._state = S1_WAIT
                    yield self._state
                    continue
                '''

                '''
                # Stop cleanly BEFORE any put() can block
                if self._dataValues.full() or self._timeValues.full():
                    self._mot.set_effort(0)
                    self._mot.disable()
                    self._goFlag.put(False)
                    self._state = S1_WAIT
                    yield self._state
                    continue

                # Log data (safe because there is space)
                t = ticks_us()
                self._dataValues.put(vel)
                self._timeValues.put(ticks_diff(t, self._startTime) / 1_000_000)
                '''
            
            yield self._state