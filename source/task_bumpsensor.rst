Bump Sensor Task
================
The bump sensor task monitors the interrupt-driven bump sensor driver and converts 
bump events into a debounced shared flag for the rest of the system. When a collision 
is detected, it latches the event, starts a lockout timer to prevent repeated 
triggers from switch bounce, and rearms the sensor after the lockout period ends. 
This allows the FSM to respond reliably to obstacle contact without being 
overwhelmed by repeated bump interrupts.

.. automodule:: task_bumpsensor
   :members:
   :special-members: __init__
   :show-inheritance: