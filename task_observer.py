# task_observer.py

import micropython
import utime
from ulab import numpy as np
from imu_driver import BNO055
import os
import math  # ADDED

# try to import embedded calibration blob (optional)
try:
    from bno055_cal import CAL_BLOB
except Exception:
    CAL_BLOB = None

S0_INIT = micropython.const(0)
S1_RUN  = micropython.const(1)

class task_observer:
    """
    Observer task:
      - Handles IMU init + calibration load/save
      - Each period: reads u and y, runs xhat update: xhat[k+1] = Ad*xhat[k] + Bd*z[k]
    """

    def __init__(self, imu,
                 # inputs
                 uL, uR,
                 # measurements
                 sL, sR, psi, psi_dot, 
                 leftMotorGo, rightMotorGo,
                 cal_filename="bno055_cal.bin"):

        self.state = S0_INIT

        self.leftGo = leftMotorGo
        self.rightGo = rightMotorGo

        self._was_running = False
        #self.posTime = posTime

        self.imu = imu
        self.uL = uL
        self.uR = uR

        self.sL = sL
        self.sR = sR
        self.psi = psi
        self.psi_dot = psi_dot

        #self.xhat0 = xhat0
        #self.xhat1 = xhat1
        #self.xhat2 = xhat2
        #self.xhat3 = xhat3

        # ADDED: pose outputs
        #self.x = x
        #self.y = y

        # ADDED: internal pose state
        #self.x_pos = 0.0
        #self.y_pos = 0.0
        self._t_us = utime.ticks_us()

        self.prev_s = None
        self._pos_t0_ms = None

        '''
        # Ad: (4x4), Bd: (4x(2+4)) if z=[uL,uR,sL,sR,psi,psi_dot]
        self.Ad = np.array([
            [0.7427,  0,       0.2494,  0.2494],
            [0,       0.0061,  0,       0],
            [-0.1212, 0,       0.3192,  0.3095],
            [-0.1212, 0,       0.3095,  0.3192]
        ], dtype=np.float)
        self.Bd = np.array([
            [0.1962, 0.1962, 0.1287, 0.1287, 0,       0],
            [0,      0,      -0.0071, 0.0071, 0.0001, 0.0039],
            [0.7137, 0.4156, 0.0606,  0.0606, 0,      -1.8098],
            [0.4156, 0.7137, 0.0606,  0.0606, 0,       1.8098]
        ], dtype=np.float)
        '''
        

        self.cal_filename = cal_filename

        # internal state estimate vector
        #self.xhat = np.zeros((4, 1), dtype=np.float)


    def _try_load_cal(self):
        # Try to load the binary file on the board first
        try:
            with open(self.cal_filename, "rb") as f:
                blob = f.read()
            if blob is None or len(blob) != 22:
                raise OSError
            self.imu.write_calibration_coeffs(blob)
            return True
        except OSError:
            # If no file on disk, fall back to embedded CAL_BLOB (if present)
            if CAL_BLOB is not None and len(CAL_BLOB) == 22:
                # save to disk so future runs also have the .bin
                try:
                    with open(self.cal_filename, "wb") as f:
                        f.write(CAL_BLOB)
                    os.sync()   # ensure filesystem commit
                except Exception:
                    # ignore write errors but still attempt to write into IMU
                    pass
                # write into IMU (do not rely on file being present)
                self.imu.write_calibration_coeffs(CAL_BLOB)
                return True
            return False

    def _save_cal(self):
        blob = self.imu.read_calibration_coeffs()
        with open(self.cal_filename, "wb") as f:
            f.write(blob)
        os.sync()
        print("Saved", self.cal_filename, "len", len(blob))

    def run(self):
        while True:
            if self.state == S0_INIT:

                # Force IMU into IMU_MODE
                if self.imu.mode() != BNO055.IMU_MODE:
                    self.imu.set_mode(BNO055.IMU_MODE)
                    utime.sleep_ms(50)

                # Try to load calibration once at boot
                loaded = self._try_load_cal()

                if loaded:
                    self.imu.set_mode(BNO055.IMU_MODE)
                    utime.sleep_ms(50)
                    print("IMU cal loaded from file.")
                    self.state = S1_RUN
                    yield self.state
                    continue

                # Otherwise, wait until calibrated
                sys, gyro, accel, mag = self.imu.calibration_status()
                calibrated = (gyro == 3 and accel == 3)

                if calibrated:
                    print("IMU calibrated. Saving + starting observer.")
                    self._save_cal()
                    self.state = S1_RUN
                else:
                    # Optional: print status occasionally
                    print("Cal status:", sys, gyro, accel, mag)
                    utime.sleep_ms(200)

                yield self.state
                continue


            elif self.state == S1_RUN:
                # --- Read IMU measurements ---
                psi = self.imu.heading()
                psi = (psi + math.pi) % (2*math.pi) - math.pi
                psi_dot = self.imu.yaw_rate()

                # Publish IMU measurements
                self.psi.put(psi)
                self.psi_dot.put(psi_dot)

                # --- Read inputs and other measurements ---
                uL = self.uL.get()
                uR = self.uR.get()

                sL = self.sL.get() * 1000
                sR = self.sR.get() * 1000

                '''
                # z = [uL, uR, sL, sR, psi, psi_dot]^T
                z = np.array([[uL],
                              [uR],
                              [sL],
                              [sR],
                              [psi],
                              [psi_dot]], dtype=np.float)

                # xhat_next = Ad*xhat + Bd*z
                #self.xhat = np.dot(self.Ad, self.xhat) + np.dot(self.Bd, z)
                

                #s_est = self.xhat[0,0]
                #psi_est = self.xhat[1,0]

                # ---------------- CALC POSITION ---------------
                
                # init
                if self.prev_s is None:
                    self.prev_s = s_est

                ds = s_est - self.prev_s
                self.prev_s = s_est

                self.x_pos += ds * math.cos(psi_est)
                self.y_pos += ds * math.sin(psi_est)
                '''

                running = (self.leftGo.get() or self.rightGo.get())

                # detect start of run
                if running and not self._was_running:
                    self._pos_t0_ms = utime.ticks_ms()

                self._was_running = running

                if running:
                    
                    '''
                    if not self.x.full():
                        self.x.put(self.x_pos)

                    if not self.y.full():
                        self.y.put(self.y_pos)

                    if (self._pos_t0_ms is not None) and (not self.posTime.full()):
                        t = utime.ticks_diff(utime.ticks_ms(), self._pos_t0_ms) / 1000.0
                        self.posTime.put(t)
                    '''
                    
                    psi_meas = self.imu.heading()
                    psi_meas = (psi_meas + math.pi) % (2*math.pi) - math.pi

                    '''
                    # Publish estimated states
                    if not self.xhat0.full():
                        self.xhat0.put(float(self.xhat[0, 0]))
                    if not self.xhat1.full():
                        self.xhat1.put(float(self.xhat[1, 0]))
                        #self.xhat1.put(psi_meas)
                    if not self.xhat2.full():
                        self.xhat2.put(float(self.xhat[2, 0]))
                    if not self.xhat3.full():
                        self.xhat3.put(float(self.xhat[3, 0]))
                    '''

                    

            yield self.state