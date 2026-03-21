# task_observer.py

import micropython
import utime
from ulab import numpy as np
from imu_driver import BNO055
import os
import math

# try to import embedded calibration blob (optional)
try:
    from bno055_cal import CAL_BLOB
except Exception:
    CAL_BLOB = None

S0_INIT = micropython.const(0)
S1_RUN  = micropython.const(1)


class task_observer:
    """
    Observer task that manages IMU calibration and publishes orientation data.
    """

    def __init__(self, imu,
                 uL, uR,
                 sL, sR, psi, psi_dot,
                 leftMotorGo, rightMotorGo,
                 cal_filename="bno055_cal.bin"):
        """
        Initialize the observer task.

        Args:
            imu: BNO055 IMU driver object.
            uL: Share containing left motor input voltage estimate.
            uR: Share containing right motor input voltage estimate.
            sL: Share containing left wheel position measurement.
            sR: Share containing right wheel position measurement.
            psi: Share used to publish heading angle.
            psi_dot: Share used to publish yaw rate.
            leftMotorGo: Shared flag indicating left motor activity.
            rightMotorGo: Shared flag indicating right motor activity.
            cal_filename: Filename used to store IMU calibration data.
        """
        self.state = S0_INIT

        self.leftGo = leftMotorGo
        self.rightGo = rightMotorGo

        self._was_running = False

        self.imu = imu
        self.uL = uL
        self.uR = uR

        self.sL = sL
        self.sR = sR
        self.psi = psi
        self.psi_dot = psi_dot

        self._t_us = utime.ticks_us()

        self.prev_s = None
        self._pos_t0_ms = None

        self.cal_filename = cal_filename

    def _try_load_cal(self):
        """
        Try to load IMU calibration data from file or embedded fallback data.

        Returns:
            bool: True if calibration data was successfully loaded.
        """
        try:
            with open(self.cal_filename, "rb") as f:
                blob = f.read()
            if blob is None or len(blob) != 22:
                raise OSError
            self.imu.write_calibration_coeffs(blob)
            return True
        except OSError:
            if CAL_BLOB is not None and len(CAL_BLOB) == 22:
                try:
                    with open(self.cal_filename, "wb") as f:
                        f.write(CAL_BLOB)
                    os.sync()
                except Exception:
                    pass
                self.imu.write_calibration_coeffs(CAL_BLOB)
                return True
            return False

    def _save_cal(self):
        """
        Save the current IMU calibration coefficients to a file.
        """
        blob = self.imu.read_calibration_coeffs()
        with open(self.cal_filename, "wb") as f:
            f.write(blob)
        os.sync()
        print("Saved", self.cal_filename, "len", len(blob))

    def run(self):
        """
        Run one iteration of the observer task.

        This generator handles IMU startup and calibration during initialization,
        then reads heading and yaw-rate measurements during execution and publishes
        them to shared variables.

        Yields:
            int: The current state of the observer task.
        """
        while True:
            if self.state == S0_INIT:

                if self.imu.mode() != BNO055.IMU_MODE:
                    self.imu.set_mode(BNO055.IMU_MODE)
                    utime.sleep_ms(50)

                loaded = self._try_load_cal()

                if loaded:
                    self.imu.set_mode(BNO055.IMU_MODE)
                    utime.sleep_ms(50)
                    print("IMU cal loaded from file.")
                    self.state = S1_RUN
                    yield self.state
                    continue

                sys, gyro, accel, mag = self.imu.calibration_status()
                calibrated = (gyro == 3 and accel == 3)

                if calibrated:
                    print("IMU calibrated. Saving + starting observer.")
                    self._save_cal()
                    self.state = S1_RUN
                else:
                    print("Cal status:", sys, gyro, accel, mag)
                    utime.sleep_ms(200)

                yield self.state
                continue

            elif self.state == S1_RUN:
                psi = self.imu.heading()
                psi = (psi + math.pi) % (2 * math.pi) - math.pi
                psi_dot = self.imu.yaw_rate()

                self.psi.put(psi)
                self.psi_dot.put(psi_dot)

                uL = self.uL.get()
                uR = self.uR.get()

                sL = self.sL.get() * 1000
                sR = self.sR.get() * 1000

                running = (self.leftGo.get() or self.rightGo.get())

                if running and not self._was_running:
                    self._pos_t0_ms = utime.ticks_ms()

                self._was_running = running

                if running:
                    psi_meas = self.imu.heading()
                    psi_meas = (psi_meas + math.pi) % (2 * math.pi) - math.pi

            yield self.state