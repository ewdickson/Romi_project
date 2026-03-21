Line Sensor Task
================
The line sensor task reads the processed line centroid from the line sensor driver 
and converts it into a steering correction signal. When the robot is actively 
running, it scales the detected line offset by a steering gain and publishes the 
resulting correction so that the finite state machine or motor control logic can 
adjust wheel speeds appropriately. This task is what turns the raw line position 
measurement into a usable guidance signal for line following.

.. automodule:: task_linesensor
   :members:
   :special-members: __init__
   :show-inheritance: