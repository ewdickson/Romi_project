from motor_driver import motor_driver
from encoder      import encoder
from task_share   import Share, Queue
from utime        import ticks_us, ticks_diff
import micropython

S0_INIT = micropython.const(0)  # State 0 - initialization
S1_WAIT = micropython.const(1)  # State 1 - wait for go command
S2_RUN  = micropython.const(2)  # State 2 - run closed loop control


class task_motor:
    """Closed-loop motor control task for one drive motor."""

    def __init__(self,
                 mot: motor_driver, enc: encoder,
                 goFlag: Share,
                 kp, ki, setpoint,
                 s_meas: Share, u_volts: Share,
                 bumpFlag: Share,
                 flip_encoder, name):
        """
        Initialize the motor task with hardware objects, controller gains, and shares.

        Args:
            mot: Motor driver object for this wheel.
            enc: Encoder object used for feedback.
            goFlag: Shared flag that enables or disables motor operation.
            kp: Shared proportional gain.
            ki: Shared integral gain.
            setpoint: Shared wheel velocity setpoint.
            s_meas: Share used to publish measured wheel position.
            u_volts: Share used to publish estimated motor input voltage.
            bumpFlag: Shared bump flag from the bump sensor task.
            flip_encoder: Sign correction for encoder direction.
            name: Short name for this motor task.
        """
        self._bumpFlag: Share = bumpFlag
        self._state: int = S0_INIT

        # Hardware
        self._mot: motor_driver = mot
        self._enc: encoder = enc

        # Scheduler shares
        self._goFlag: Share = goFlag
        self._startTime: int = 0

        # Controller parameters
        self._kp = kp
        self._ki = ki
        self._setpoint = setpoint
        self._e_int = 0.0

        self._s_meas = s_meas
        self._u_volts = u_volts

        self.flip_encoder = flip_encoder
        self.name = name

        print("Motor Task object instantiated")

    def run(self):
        """
        Run one iteration of the motor control task.

        This generator implements a finite state machine with initialization,
        waiting, and closed-loop control states. During the run state, the task
        reads encoder feedback, computes PI control effort, and commands the motor.

        Yields:
            int: The current state of the motor task.
        """
        while True:

            if self._state == S0_INIT:
                self._state = S1_WAIT

            elif self._state == S1_WAIT:
                if self._goFlag.get():
                    self._startTime = ticks_us()

                    self._mot.enable()
                    self._e_int = 0.0
                    self._state = S2_RUN

            elif self._state == S2_RUN:

                if self._goFlag.get() is True:
                    self._enc.update()

                    vel = self.flip_encoder * self._enc.get_velocity()
                    dt = self._enc.dt

                    self._s_meas.put(self.flip_encoder * self._enc.get_position())

                    if dt <= 0:
                        yield self._state
                        continue

                    Kp = self._kp.get()
                    Ki = self._ki.get()
                    SP = self._setpoint.get()

                    e = SP - vel

                    e_int_test = self._e_int + e * dt
                    effort = (Kp * e) + (Ki * e_int_test)

                    if -100 < effort < 100:
                        self._e_int = e_int_test

                    effort = (Kp * e) + (Ki * self._e_int)
                    effort = max(min(effort, 100), -100)

                    self._mot.set_effort(effort)

                    Vbatt = 9.0
                    self._u_volts.put((effort / 100.0) * Vbatt)

                else:
                    self._e_int = 0
                    self._mot.set_effort(0)
                    self._mot.disable()
                    self._state = S1_WAIT

            yield self._state