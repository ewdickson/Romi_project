Main
====
The main file serves as the top-level integration point for the entire robot control 
system. It initializes all hardware drivers, creates the shared variables used for 
communication between tasks, instantiates each cooperative task, and adds them to 
the scheduler. Once setup is complete, it enters the main scheduling loop, allowing 
the motor control, line sensing, bump detection, observer, user interface, and finite 
state machine tasks to work together as one coordinated program.

.. automodule:: main
   :members:
   :undoc-members: