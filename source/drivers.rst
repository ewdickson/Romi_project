Drivers
=======
The driver files provide the low-level hardware interface layer for the project. 
Together, they handle communication with the Romi’s physical sensors and actuators, 
converting raw electrical signals and register-level device behavior into usable 
Python objects for the higher-level task code. This keeps the control tasks cleaner 
and more modular, since each task can work with meaningful quantities such as motor 
effort, wheel position, line position, heading, or bump events without needing to 
manage hardware details directly.

Motor Driver
------------
The motor driver file defines the interface used to command each drive motor on the 
Romi. It configures the PWM, direction, and sleep-control pins needed by the motor 
driver hardware, and provides methods to enable or disable the driver and to apply 
a signed effort command. This allows the rest of the control system to command wheel 
motion in a simple and consistent way without dealing directly with timer or pin-level 
behavior.

.. automodule:: motor_driver
   :members:
   :special-members: __init__
   :show-inheritance:

Encoder Driver
--------------
The encoder driver file measures wheel motion using quadrature encoder feedback. It 
tracks encoder counts over time, converts them into position and velocity information, 
and provides the feedback needed for closed-loop motor control. By encapsulating the 
timer and count-update logic, it gives the motor task a clean source of motion data 
for estimating wheel speed and distance traveled.

.. automodule:: encoder
   :members:
   :special-members: __init__
   :show-inheritance:

Line Sensor Driver
------------------
The line sensor driver file reads the seven-element reflectance sensor array used 
for line following. It collects raw ADC values from each sensor, applies stored 
calibration limits, and computes normalized readings and a centroid value 
representing the detected line position. This makes it possible for the line-following 
task to turn sensor readings into a steering correction that keeps the robot aligned 
with the course.

.. automodule:: linesensor
   :members:
   :special-members: __init__
   :show-inheritance:

IMU Driver
----------
The IMU driver file manages communication with the BNO055 inertial measurement unit 
over I2C. It handles sensor reset, operating mode changes, calibration data storage, 
and the reading of orientation and angular velocity values. In this project, it is 
used primarily to provide heading and yaw-rate measurements that support state 
estimation and observer-based tracking of the robot’s motion.

.. automodule:: imu_driver
   :members:
   :special-members: __init__
   :show-inheritance:

Bump Sensor Driver
------------------
The bump sensor driver file provides a simple interrupt-based interface for the front 
bump switch. It configures the input pin and external interrupt so that a contact 
event is latched immediately when the bumper is triggered, then temporarily disables 
the interrupt to avoid repeated triggers from switch bounce. This gives the 
higher-level bump task a reliable event signal that can be used for obstacle handling 
and recovery behavior.

.. automodule:: bumpsensor
   :members:
   :special-members: __init__
   :show-inheritance: