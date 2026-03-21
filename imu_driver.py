# IMU Driver

import utime
from pyb import Pin, I2C


class BNO055:
    """Driver for the BNO055 IMU using I2C communication."""

    ADDR = 0x28

    # Registers (page 0)
    _CHIP_ID      = 0x00
    _PAGE_ID      = 0x07

    _OPR_MODE     = 0x3D
    _CALIB_STAT   = 0x35

    _EUL_H_LSB    = 0x1A  # EUL_DATA_X = heading
    _EUL_R_LSB    = 0x1C  # EUL_DATA_Y = roll
    _EUL_P_LSB    = 0x1E  # EUL_DATA_Z = pitch

    _GYR_X_LSB    = 0x14
    _GYR_Y_LSB    = 0x16
    _GYR_Z_LSB    = 0x18

    _CALIB_START  = 0x55
    _CALIB_LEN    = 22  # standard profile blob length (0x55..0x6A)

    # Operating modes (fusion + config)
    CONFIG_MODE   = 0x00
    IMU_MODE      = 0x08
    NDOF_MODE     = 0x0C

    def __init__(self, i2c, addr=ADDR):
        """
        Initialize the BNO055 sensor and place it in configuration mode.

        Args:
            i2c: I2C bus object used to communicate with the sensor.
            addr: I2C address of the BNO055.
        """
        self.i2c = i2c
        self.addr = addr

        # Hardware reset: RST wired to PA15 (active LOW)
        self.rst = Pin('PA15', Pin.OUT_PP)
        self.rst.low()
        utime.sleep_ms(20)
        self.rst.high()
        utime.sleep_ms(700)   # allow BNO055 to boot

        chip = self._read_u8(self._CHIP_ID)
        if chip != 0xA0:
            utime.sleep_ms(650)
            chip = self._read_u8(self._CHIP_ID)
            if chip != 0xA0:
                raise OSError("BNO055 not found")

        # Ensure page 0
        self._write_u8(self._PAGE_ID, 0x00)

        # Start in config mode
        self.set_mode(self.CONFIG_MODE)

    def set_mode(self, mode):
        """
        Set the current BNO055 operating mode.

        Args:
            mode: One of the BNO055 operating mode constants.
        """
        self._write_u8(self._OPR_MODE, mode & 0x0F)
        utime.sleep_ms(30)

    def mode(self):
        """
        Read the current operating mode.

        Returns:
            int: Current BNO055 operating mode value.
        """
        return self._read_u8(self._OPR_MODE) & 0x0F

    def calibration_status(self):
        """
        Read the current system and sensor calibration status.

        Returns:
            tuple: Calibration levels for system, gyro, accel, and mag.
        """
        c = self._read_u8(self._CALIB_STAT)
        sys  = (c >> 6) & 0x03
        gyro = (c >> 4) & 0x03
        accel = (c >> 2) & 0x03
        mag  = c & 0x03
        return (sys, gyro, accel, mag)

    def read_calibration_coeffs(self):
        """
        Read the stored calibration coefficient block from the sensor.

        Returns:
            bytes: Calibration data blob.
        """
        old = self._read_u8(self._OPR_MODE)
        self.set_mode(self.CONFIG_MODE)
        utime.sleep_ms(25)

        blob = self._read_len(self._CALIB_START, self._CALIB_LEN)

        self.set_mode(old)
        utime.sleep_ms(25)
        return blob

    def write_calibration_coeffs(self, blob):
        """
        Write a calibration coefficient block to the sensor.

        Args:
            blob: 22-byte calibration data blob.

        Raises:
            ValueError: If the calibration blob is not 22 bytes long.
        """
        if blob is None or len(blob) != self._CALIB_LEN:
            raise ValueError("Calibration data must be 22 bytes")

        old = self._read_u8(self._OPR_MODE)
        self.set_mode(self.CONFIG_MODE)
        utime.sleep_ms(25)

        self._write_len(self._CALIB_START, blob)

        self.set_mode(old)
        utime.sleep_ms(25)

    def read_euler(self):
        """
        Read Euler orientation angles from the IMU.

        Returns:
            tuple: Heading, roll, and pitch in radians.
        """
        h = self._read_s16(self._EUL_H_LSB) / 16.0 * (3.141592653589793 / 180.0)
        r = self._read_s16(self._EUL_R_LSB) / 16.0 * (3.141592653589793 / 180.0)
        p = self._read_s16(self._EUL_P_LSB) / 16.0 * (3.141592653589793 / 180.0)
        return (h, r, p)

    def heading(self):
        """
        Read the current heading angle.

        Returns:
            float: Heading in radians.
        """
        return self._read_s16(self._EUL_H_LSB) / 16.0 * (3.141592653589793 / 180.0)

    def read_angular_velocity(self):
        """
        Read angular velocity from the gyroscope.

        Returns:
            tuple: Angular velocity about x, y, and z axes in radians per second.
        """
        gx = self._read_s16(self._GYR_X_LSB) / 16.0 * (3.141592653589793 / 180.0)
        gy = self._read_s16(self._GYR_Y_LSB) / 16.0 * (3.141592653589793 / 180.0)
        gz = self._read_s16(self._GYR_Z_LSB) / 16.0 * (3.141592653589793 / 180.0)
        return (gx, gy, gz)

    def yaw_rate(self):
        """
        Read the angular velocity about the z-axis.

        Returns:
            float: Yaw rate in radians per second.
        """
        return self._read_s16(self._GYR_Z_LSB) / 16.0 * (3.141592653589793 / 180.0)

    def _write_u8(self, reg, val):
        """Write one byte to a sensor register."""
        self.i2c.mem_write(bytes([val & 0xFF]), self.addr, reg)

    def _read_u8(self, reg):
        """Read one byte from a sensor register."""
        return self.i2c.mem_read(1, self.addr, reg)[0]

    def _read_len(self, reg, n):
        """Read multiple bytes starting at a given register."""
        return self.i2c.mem_read(n, self.addr, reg)

    def _write_len(self, reg, data):
        """Write multiple bytes starting at a given register."""
        self.i2c.mem_write(data, self.addr, reg)

    def _read_s16(self, reg):
        """
        Read a signed 16-bit value starting at the given register.

        Args:
            reg: Starting register address.

        Returns:
            int: Signed 16-bit register value.
        """
        b = self.i2c.mem_read(2, self.addr, reg)
        v = b[0] | (b[1] << 8)
        if v & 0x8000:
            v -= 0x10000
        return v