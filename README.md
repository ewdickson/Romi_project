# ME405 Term Project: Autonomous Line-Following Robot

## Project Overview
This project implements an autonomous line-following robot using the Pololu Romi platform. The robot is designed to navigate a printed course as quickly and reliably as possible while handling obstacles and executing predefined maneuvers.

Depending on track position, the robot follows printed lines, performs distance-based movements, and recovers from collisions. Performance is evaluated based on completion time, with penalties and bonuses applied depending on interactions with course elements (e.g., moving cups or hitting obstacles).

---

## System Summary
The robot uses a combination of:
- Line sensors for continuous path tracking  
- Wheel encoders for distance-based navigation  
- Bump sensor for collision detection and recovery  
- PI motor controllers for velocity regulation  

Although an IMU and state estimation framework were developed, they were not used in the final implementation.

---

## General Strategy
The robot progresses through the course using a finite state machine (FSM). Each state corresponds to a segment of the track and defines how the robot should behave.

Key behaviors include:
- Straight and curved line following  
- Open-loop motion segments  
- In-place turns (90°, 45°, 180°)  
- Bump detection and recovery  

State transitions are primarily triggered by encoder-based distance thresholds, with additional transitions based on sensor events such as detecting a bump.

---

## Program Structure
The software is organized as a cooperative multitasking system using a priority-based scheduler. Each subsystem runs as an independent task and communicates through shared variables.

The main program initializes all hardware drivers (motors, encoders, line sensor, IMU, and bump sensor), constructs the required tasks, and schedules them to run periodically. Each task is implemented as a generator function and yields control back to the scheduler, enabling deterministic execution timing.

---

## Task Architecture
The system is composed of several key tasks:

- **Motor Tasks** – Implement closed-loop PI control for each wheel using encoder feedback  
- **Line Sensor Task** – Computes line position and generates a steering correction  
- **FSM Task** – High-level controller that governs behavior and transitions  
- **Bump Sensor Task** – Detects collisions and triggers recovery behavior  
- **User Task** – Handles start/stop input and prints debugging information  
- **Observer Task** – Handles IMU data and calibration (not used in final control)

Each task operates independently but shares data through a centralized set of shared variables, enabling modular and scalable system design.

---

## Control System

### Motor Control (PI)
Each motor is controlled using a proportional-integral (PI) controller that regulates wheel velocity. The controller compares the desired velocity setpoint to the measured velocity from the encoder and computes a motor effort command, which is applied via PWM.

This improves tracking accuracy, reduces steady-state error, and compensates for disturbances such as friction and load variations.

---

### Line Following
The robot uses a centroid-based line detection algorithm to determine its position relative to the line.

Control is implemented as:

Left Motor  = Base Speed + Correction  
Right Motor = Base Speed − Correction  

The correction term is proportional to the line position, allowing smooth steering and stable tracking of the path.

---

## Hardware Overview
- **Platform:** Pololu Romi chassis  
- **Motor Driver:** Pololu DRV8838 Motor Driver & Power Distribution Board  
- **Line Sensor:** Pololu QTRX-MD-07A (7-channel analog reflectance sensor)  
- **Encoders:** Integrated quadrature encoders  
- **IMU:** BNO055 (not used in final control)  
- **Bump Sensor:** Pololu bumper switch  

---

## System Behavior
In the final implementation, the robot relies on:
- Line sensor feedback for continuous navigation  
- Encoder measurements for distance-based transitions  
- Bump sensor input for event-driven recovery  

Although an observer and IMU driver were implemented, state estimation was not used. The simpler approach proved more robust and easier to tune for this application.

---

## Repository Structure

`main.py` — System initialization and scheduler<br>
`task_fsm.py` — Finite state machine logic<br>
`task_motor.py` — Motor control tasks (PI controllers)<br>
`task_linesensor.py` — Line detection and correction<br>
`task_bumpsensor.py` — Bump detection task<br>
`task_user.py` — User interface and debugging<br>
`task_observer.py` — IMU + observer (not used)<br>
`motor_driver.py` — Motor driver interface<br>
`encoder.py` — Encoder interface<br>
`imu_driver.py` — IMU driver<br>
`task_share.py` — Inter-task communication

---

## How to Run
1. Upload all files to the Nucleo board  
2. Power the robot  
3. Press the blue user button to start/stop the run  
4. Optionally monitor output via serial terminal  

---

## Acknowledgments
Special thanks to previous ME405 teams for shared components and resources and Charlie Refvem for general advising.
