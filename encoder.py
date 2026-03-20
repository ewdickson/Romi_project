# Encoder driver 

import pyb
from pyb import Timer, Pin
from time import ticks_us, ticks_diff 
from math import pi

 
class encoder: 

    '''A quadrature encoder decoding interface encapsulated in a Python class''' 

    def __init__(self, tim, chA_pin, chB_pin): 

        '''Initializes an Encoder object''' 

        self.timer = Timer(tim, prescaler=0, period=65535) 
        self.timer.channel(1, Timer.ENC_AB, pin=chA_pin) 
        self.timer.channel(2, Timer.ENC_AB, pin=chB_pin) 

        self.position   = 0 
        self.velocity   = 0
        self.prev_count = self.timer.counter() 
        self.delta      = 0 
        self.dt         = 0
        self.prev_time  = ticks_us() 

    def update(self): 

        '''Updates position and velocity, handling counter overflow''' 

        now = ticks_us() 
        self.dt = ticks_diff(now, self.prev_time) / 1000000 
        self.prev_time = now 

        # CLAUDE SUGGESTION: skip velocity on first call or if dt is suspiciously large
        if self.dt > 0.5:   # more than 500ms gap → stale, skip
            self.delta = 0
            self.prev_count = self.timer.counter()
            self.velocity = 0
            return

        count = self.timer.counter() 
        self.delta = count - self.prev_count 

        # Handle overflow 

        if self.delta > 32768: 
            self.delta -= 65536 
        elif self.delta < -32768: 
            self.delta += 65536 

        self.position += self.delta 
        self.prev_count = count 
        if self.dt > 0:
            self.velocity = self.delta / self.dt
        else:
            self.velocity = 0


    def get_position(self): 

        '''Returns the most recent encoder position''' 

        return self.position * 2 * pi * 0.035 / 1437.12

    def get_velocity(self): 

        '''Returns velocity in counts per microsecond''' 

        return self.velocity * 2 * pi * 0.035 / 1437.12

 

    def zero(self): 

        '''Resets encoder position to zero'''

        self.position = 0 
        self.prev_count = self.timer.counter() 