# LAB 0x05 MAIN

from pyb import Pin, millis, delay, elapsed_millis
from linesensor import LineSensor
# task_linesensor.py
import micropython

S0_INIT = micropython.const(0)
S1_RUN  = micropython.const(1)

class task_linesensor:
    def __init__(self, linesensor, leftGo, rightGo, steerGain, lineCorr):
        self.state = S0_INIT
        self.linesensor = linesensor

        self.leftGo = leftGo
        self.rightGo = rightGo

        self._cent_t0 = None
        self._was_running = False

        #self.centroid              = centroid
        #self.centroidTime           = centroidTime
        
        self._steerGain = steerGain
        self._lineCorr = lineCorr

    def run(self):
        while True:

            if self.state == S0_INIT:
                self.state = S1_RUN

            elif self.state == S1_RUN:
                
                running = (self.leftGo.get() or self.rightGo.get())

                # detect start of run
                if running and not self._was_running:
                    self._cent_t0_ms = millis()

                self._was_running = running

                if running:
                    c = self.linesensor.centroid()
                    g = self._steerGain.get()

                    '''
                    if not self.centroid.full():
                        self.centroid.put(0.0 if c is None else c)

                    if (self._cent_t0_ms is not None) and (not self.centroidTime.full()):
                        t = (millis() - self._cent_t0_ms) / 1000.0
                        self.centroidTime.put(t)
                    '''

                #self.centroid.put(c)
                    if c is None:
                        d = 0.0
                    else:
                        d = g * c   # <-- only “tuning” number
                    
                    self._lineCorr.put(d)
                else:
                    self._lineCorr.put(0)

                '''
                    self.leftSetpoint.put(b + d)
                    self.rightSetpoint.put(b - d)

                else:
                    # not running -> keep both equal
                    self.leftSetpoint.put(b)
                    self.rightSetpoint.put(b)
                '''

            yield self.state

'''
pins = [
    Pin.cpu.A4,
    Pin.cpu.B0,
    Pin.cpu.B1,
    Pin.cpu.C0,
    Pin.cpu.C1,
    Pin.cpu.C2,
    Pin.cpu.C3
]

line_sensor = LineSensor(pins)


# -------------------- CALIBRATION CODE --------------------

print("Starting calibration...")

start = millis()
last_print = start

while elapsed_millis(start) < 10000:
    raw = line_sensor.read_raw()
    line_sensor.calibrate_step()
    if elapsed_millis(last_print) > 100:
        print(raw)
        last_print = millis()
    delay(5)

print("Calibration complete!")
print("Mins:", line_sensor.mins)
print("Maxs:", line_sensor.maxs)
'''
'''
# -------------------- TESTING CENTROID --------------------
print("Streaming centroid in mm (Ctrl+C to stop)...")

last_print = millis()

while True:
    c = line_sensor.centroid()

    # Print every 100 ms
    if elapsed_millis(last_print) >= 100:
        if c is None:
            print("centroid: None")
        else:
            print("centroid (mm):", round(c, 2))
        last_print = millis()

    delay(5)
'''