Observer Task
=============
The observer task manages IMU startup and calibration while also publishing 
orientation-related measurements to the rest of the system. It loads or saves 
BNO055 calibration data, ensures the IMU is in the correct mode, and 
continuously updates shared heading and yaw-rate values during operation. 
This task supports state estimation by turning the raw IMU into a ready-to-use 
sensing component that the robot can rely on during motion.

.. automodule:: task_observer
   :members:
   :special-members: __init__
   :show-inheritance: