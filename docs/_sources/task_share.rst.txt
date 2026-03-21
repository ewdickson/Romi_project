Share Task
==========
The task_share file provides the shared-variable and queue framework that allows the 
different cooperative tasks to exchange data safely. It defines the Share and Queue 
classes used throughout the project to pass sensor measurements, control commands, 
flags, and estimated states between tasks without requiring direct coupling between 
them. This communication layer is central to the project’s modular structure, since 
each task can publish and consume information through shared objects rather than 
depending on hard-coded links to other tasks.

.. automodule:: task_share
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance: