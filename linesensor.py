# Line Sensor Class

import pyb

class LineSensor:
    def __init__(self, pins):
        self.adc = [pyb.ADC(pin) for pin in pins]

        # OPTION A: PLACEHOLDERS FOR CALIBRATION
        #self.mins = [4095]*7
        #self.maxs = [0]*7

        # OPTION B: HARDCODED CALIBRATION VALUES OG TRACK
        #self.mins =  [1567, 1018, 682, 425, 1069, 683, 1571]
        #self.maxs =  [3183, 3134, 2961, 2947, 3133, 2999, 3247]

        # OPTION C: BAD TRACK
        self.mins = [1449, 1111, 834, 430, 1193, 807, 1692]
        self.maxs = [3143, 3018, 2856, 2815, 2972, 2936, 3071]

        self.pos = [-24, -16, -8, 0, 8, 16, 24]  # mm

    def read_raw(self):
        return [a.read() for a in self.adc]

    def calibrate_step(self):
        raw = self.read_raw()
        for i in range(7):
            if raw[i] < self.mins[i]:
                self.mins[i] = raw[i]
            if raw[i] > self.maxs[i]:
                self.maxs[i] = raw[i]

    def read_norm(self):

        raw = self.read_raw()
        norm = [0]*7
        for i in range(7):
            span = self.maxs[i] - self.mins[i]
            if span == 0:
                norm[i] = 0
            else:
                x = (raw[i] - self.mins[i]) / span
                norm[i] = max(0, min(1, x))
        return norm

    def centroid(self):
        w = self.read_norm()
        total = sum(w)

        if total == 0:
            return None  # no line detected

        return sum(w[i]*self.pos[i] for i in range(7)) / total