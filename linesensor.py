# Line Sensor Class

import pyb


class LineSensor:
    """Driver for a seven-element analog line sensor array."""

    def __init__(self, pins):
        """
        Initialize the line sensor with ADC pins and calibration values.

        Args:
            pins: Iterable of pin objects connected to the sensor outputs.
        """
        self.adc = [pyb.ADC(pin) for pin in pins]
        self.mins = [1449, 1111, 834, 430, 1193, 807, 1692]
        self.maxs = [3143, 3018, 2856, 2815, 2972, 2936, 3071]

        self.pos = [-24, -16, -8, 0, 8, 16, 24]  # mm

    def read_raw(self):
        """
        Read the raw ADC values from all sensor channels.

        Returns:
            list: Raw sensor readings for the seven channels.
        """
        return [a.read() for a in self.adc]

    def calibrate_step(self):
        """
        Update stored minimum and maximum calibration values using one reading.
        """
        raw = self.read_raw()
        for i in range(7):
            if raw[i] < self.mins[i]:
                self.mins[i] = raw[i]
            if raw[i] > self.maxs[i]:
                self.maxs[i] = raw[i]

    def read_norm(self):
        """
        Read normalized sensor values scaled between 0 and 1.

        Returns:
            list: Normalized sensor readings for the seven channels.
        """
        raw = self.read_raw()
        norm = [0] * 7
        for i in range(7):
            span = self.maxs[i] - self.mins[i]
            if span == 0:
                norm[i] = 0
            else:
                x = (raw[i] - self.mins[i]) / span
                norm[i] = max(0, min(1, x))
        return norm

    def centroid(self):
        """
        Compute the weighted line position from the normalized sensor readings.

        Returns:
            float | None: Estimated line position in millimeters, or None if
            no line is detected.
        """
        w = self.read_norm()
        total = sum(w)

        if total == 0:
            return None  # no line detected

        return sum(w[i] * self.pos[i] for i in range(7)) / total