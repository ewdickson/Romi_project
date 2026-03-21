Motor Task
==========
The motor task performs closed-loop control of an individual drive motor using 
encoder feedback. It reads the current wheel motion, compares it to the commanded 
setpoint, and applies a PI controller to compute the motor effort required to 
track the desired speed. By separating this wheel-level control from the 
higher-level FSM logic, the project is able to command motion in terms of target 
wheel behavior while leaving the detailed regulation to dedicated motor tasks.

.. automodule:: task_motor
   :members:
   :special-members: __init__
   :show-inheritance: