Finite State Machine Tasks
==========================
The finite state machine task is the high-level decision-making task that coordinates 
the robot’s overall behavior through the course. It advances through a sequence of 
motion states such as line following, straight driving, turns, bump handling, 
recovery, and final stopping, while updating the motor setpoints and operating modes 
needed for each phase. This task acts as the “mastermind” of the project by combining 
sensor-based transitions and distance-based logic into one organized control flow.

.. automodule:: task_fsm
   :members:
   :private-members:
   :special-members: __init__
   :show-inheritance: