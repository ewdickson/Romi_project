import pyb
from motor_driver import motor_driver
from encoder import encoder
from task_motor import task_motor
from task_user import task_user
from task_linesensor import task_linesensor
from linesensor import LineSensor
from task_share import Share, Queue, show_all
from cotask import Task, task_list
from gc import collect
from pyb import Timer, Pin, I2C, ExtInt
from imu_driver import BNO055
from task_observer import task_observer
from bumpsensor import BumpSensor
from task_bumpsensor import task_bumpsensor
from task_fsm import task_fsm


def button_cb(line):
    """Toggle the course start flag when the user button is pressed."""
    global courseGo
    courseGo.put(not courseGo.get())


def main():
    """
    Initialize hardware wiring, create shared variables and tasks, and run the scheduler.

    This function builds the full robot control system, including motors,
    encoders, line sensor, IMU, bump sensor, inter-task shares, and all
    cooperative tasks used during course operation.
    """
    global courseGo

    # --------------- MOTORS ---------------
    t = Timer(8, freq=10000)
    rightMotor = motor_driver(t, 1, 'PC6', 'PA5', 'PB6')
    leftMotor = motor_driver(t, 2, 'PC7', 'PB4', 'PB10')

    # --------------- ENCODERS ---------------
    rightEncoder = encoder(
        tim=3,
        chA_pin=Pin.cpu.A6,
        chB_pin=Pin.cpu.A7
    )

    leftEncoder = encoder(
        tim=2,
        chA_pin=Pin.cpu.A0,
        chB_pin=Pin.cpu.A1
    )

    # --------------- LINE SENSOR ---------------
    line_pins = [
        Pin.cpu.A4,
        Pin.cpu.B0,
        Pin.cpu.B1,
        Pin.cpu.C0,
        Pin.cpu.C1,
        Pin.cpu.C2,
        Pin.cpu.C3
    ]
    linesensor = LineSensor(line_pins)

    # --------------- IMU ---------------
    i2c = I2C(1, I2C.CONTROLLER)
    i2c.init(baudrate=400000)
    print("I2C scan:", i2c.scan())
    imu = BNO055(i2c)

    # --------------- BUMP SENSOR ---------------
    bumpSensor = BumpSensor(Pin.cpu.C12)

    # --------------- SHARES/QUEUES ---------------
    leftMotorGo = Share("B", name="Left Mot. Go Flag")
    rightMotorGo = Share("B", name="Right Mot. Go Flag")

    kpL = Share('f', name="KpL")
    kpL.put(125)
    kiL = Share('f', name="KiL")
    kiL.put(3.75)

    kpR = Share('f', name="KpR")
    kpR.put(125)
    kiR = Share('f', name="KiR")
    kiR.put(3.55)

    setpoint = Share('f', name="Setpoint")
    leftsetpoint = Share('f', name="Left Setpoint")
    rightsetpoint = Share('f', name="Right Setpoint")

    steerGain = Share("f", name="Steering Gain")
    lineCorr = Share("f", name="Line Correction Factor")

    sL_meas = Share('f', name="sL meas")
    sR_meas = Share('f', name="sR meas")
    uL_volts = Share('f', name="uL volts")
    uR_volts = Share('f', name="uR volts")

    psi_meas = Share('f', name="psi meas")
    psi_dot_meas = Share('f', name="psi_dot meas")

    bumpFlag = Share("B", name="Bump Flag")

    courseGo = Share("B", name="Course Start Flag")
    fsmState = Share("B")
    mode = Share("B", name="Mode")

    # --------------- BUTTON INTERRUPT SETUP ---------------
    button_int = ExtInt(
        Pin.cpu.C13,
        ExtInt.IRQ_FALLING,
        Pin.PULL_NONE,
        button_cb
    )

    # --------------- BUILD TASKS ---------------
    fsmTask = task_fsm(
        courseGo, sL_meas, sR_meas, lineCorr, steerGain,
        bumpFlag, fsmState, mode, leftsetpoint, rightsetpoint,
        leftMotorGo, rightMotorGo
    )

    leftMotorTask = task_motor(
        leftMotor, leftEncoder,
        leftMotorGo,
        kpL, kiL, leftsetpoint,
        sL_meas, uL_volts, bumpFlag,
        flip_encoder=-1, name="LEFT"
    )

    rightMotorTask = task_motor(
        rightMotor, rightEncoder,
        rightMotorGo,
        kpR, kiR, rightsetpoint,
        sR_meas, uR_volts, bumpFlag,
        flip_encoder=-1, name="RIGHT"
    )

    bumpSensorTask = task_bumpsensor(bumpSensor, bumpFlag)
    userTask = task_user(courseGo, fsmState)

    linesensorTask = task_linesensor(
        linesensor, leftMotorGo, rightMotorGo,
        steerGain, lineCorr
    )

    observerTask = task_observer(
        imu,
        uL_volts, uR_volts,
        sL_meas, sR_meas,
        psi_meas, psi_dot_meas,
        leftMotorGo, rightMotorGo
    )

    # --------------- SCHEDULE TASKS ---------------
    task_list.append(Task(
        leftMotorTask.run, name="Left Mot. Task",
        priority=1, period=20, profile=True
    ))
    task_list.append(Task(
        rightMotorTask.run, name="Right Mot. Task",
        priority=1, period=20, profile=True
    ))
    task_list.append(Task(
        bumpSensorTask.run, name="Bump Sensor Task",
        priority=2, period=20, profile=True
    ))
    task_list.append(Task(
        userTask.run, name="User Int. Task",
        priority=0, period=0, profile=True
    ))
    task_list.append(Task(
        linesensorTask.run, name="Line Sensor Task",
        priority=2, period=20, profile=True
    ))
    task_list.append(Task(
        observerTask.run, name="Observer Task",
        priority=2, period=20, profile=True
    ))
    task_list.append(Task(
        fsmTask.run, name="FSM Task",
        priority=3, period=20, profile=True
    ))

    collect()

    while True:
        try:
            task_list.pri_sched()

        except KeyboardInterrupt:
            print("Program Terminating")
            leftMotor.disable()
            rightMotor.disable()
            break

    print("\n")
    print(task_list)
    print(show_all())


if __name__ == "__main__":
    main()