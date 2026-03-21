Program Structure
=================

The robot control software is structured as a cooperative multitasking system 
using a priority-based scheduler. Each major subsystem is implemented as an 
independent task, allowing sensing, control, and decision-making to occur 
concurrently. Tasks communicate using shared variables (Shares) and queues, 
which provide safe data exchange between tasks without data corruption.

The main program initializes all hardware drivers (motors, encoders, line sensor, 
IMU, and bump sensor), constructs the required tasks, and schedules them to run 
periodically using a cooperative scheduler. Each task runs as a generator function 
and yields control back to the scheduler, enabling deterministic execution timing.


Task Architecture
-----------------

The system is composed of several key tasks:

- **Motor Tasks**: Implement closed-loop PI control for each wheel, using encoder 
  feedback to regulate velocity.
- **Line Sensor Task**: Computes the line position and generates a correction signal 
  for steering.
- **FSM Task**: Acts as the high-level controller, determining robot behavior and 
  transitions between states.
- **Bump Sensor Task**: Detects collisions and triggers recovery behavior.
- **User Task**: Handles user input (start/stop) and provides debugging output.
- **Observer Task**: Handles IMU data and calibration (not used in final control).

Each task operates independently but shares data through a centralized set of 
Share objects, enabling modular and scalable system design.


Finite State Machine Navigation
-------------------------------

The overall behavior of the robot is governed by a finite state machine (FSM), 
which sequences the robot through the course. The FSM controls the robot by 
switching between different operating modes, including line following, open-loop 
motion, turning, and recovery.

The robot begins in an idle state and transitions into line-following mode when 
the course is started. It then progresses through a series of states corresponding 
to different segments of the track, including:

- Straight line following
- Curved line following
- In-place turns (90°, 45°, 180°)
- Open-loop straight segments
- Bump detection and recovery maneuvers

State transitions are primarily triggered by encoder-based distance thresholds, 
allowing the robot to move a precise distance before advancing to the next state. 
Additional transitions occur based on sensor events, such as detecting a bump. 

This structure enables deterministic navigation of the course while maintaining 
flexibility to handle disturbances such as collisions.


Control System
--------------

The control system consists of two main components: motor control and line-following control.

.. image:: _static/motorcontroller.jpg
   :width: 80%
   :align: center
   :alt: Control block diagram

**Motor Control (PI Controller)**

Each motor is controlled using a proportional-integral (PI) controller that 
regulates wheel velocity. The controller compares the desired velocity setpoint 
to the measured velocity from the encoder and computes a motor effort command. 
This effort is applied through PWM signals to the motor driver.

The PI controller improves tracking performance by reducing steady-state error 
and compensating for disturbances such as friction and load variations.

**Line-Following Control**

The line sensor task computes the position of the line relative to the robot 
using a centroid calculation. This position is multiplied by a steering gain 
to produce a correction term, which is applied to the motor setpoints:

- Left motor = base speed + correction  
- Right motor = base speed − correction  

This differential control allows the robot to steer smoothly toward the line 
and maintain alignment during motion.

Together, these control strategies enable stable and responsive motion throughout 
the course.


System Behavior in Final Implementation
--------------------------------------

In the final implementation, the robot relies on a combination of:

- Line sensor feedback for continuous path tracking  
- Encoder measurements for distance-based state transitions  
- Bump sensor input for event-driven recovery  

Although an observer task and IMU driver were implemented, state estimation was 
not used in the final control strategy. The simpler combination of line following 
and encoder-based navigation proved sufficiently robust for completing the course, 
while avoiding the additional complexity of tuning a model-based estimator.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   drivers
   main
   task_share
   task_fsm
   task_motor
   task_linesensor
   task_bumpsensor
   task_user
   task_observer