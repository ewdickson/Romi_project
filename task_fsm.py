# FSM TASK
# task_fsm.py (updated for in-place turns)
import time
import math

# Defines state constants for the FSM.
S0_INIT = 0
'''Fortnite'''
S1_LF1 = 1
S2_LF2 = 2
S3_LILCURVE = 3
S4_STRAIGHT1 = 4
S5_RIGHT90 = 5
S6_BUMP = 6
S7_RECOVER = 7
S8_LEFT90 = 8
S9_STRAIGHT2 = 9
S10_LF3 = 10
S11_RIGHT45 = 11
S12_LFPP = 12
S13_TURN180 = 13
S14_STRAIGHTFIN = 14
S15_END = 15

# Defines 3 different modes that the FSM runs in.
MODE_STOP = 0
MODE_LINE_FOLLOW = 1
MODE_OPEN_LOOP = 2

# Speed settings for each state in m/s (adjusted in configuration)
WHEEL_BASE = 0.141
V_LF = 0.3
V_LFCURVE = 0.05
V_STRAIGHT = 0.35
V_STRAIGHT1 = 0.15
V_TURN = 0.3          
V_CURVE = 0.05
V_LF3 = 0.05

# Distance thresholds for state transitions (adjusted in configuration)
D_LF1_STRAIGHT = 1.375
D_LF1_CURVE = 0.26
D_STRAIGHT1 = 0.16
D_RECOVER = 0.05
D_STRAIGHT2 = 0.07
D_LF_CURVE = 1.8
D_CURVE = 0.3
D_LILCURVE = 0.022
D_RIGHT90= 0.14
D_LEFT90 = 0.12
D_LFOUTG = 0.2
D_STRAIGHTFIN = 0.38

# The task_fsm class encapsulates the finite state machine logic for controlling the robot's behavior.
class task_fsm:
    '''Finite-state-machine task that coordinates robot behavior live.'''

    def __init__(self,
                 courseGo,
                 sL_meas,
                 sR_meas,
                 lineCorr,
                 steerGain,
                 bumpFlag,
                 fsmState,
                 mode,
                 leftSetpoint,
                 rightSetpoint,
                 leftMotorGo,
                 rightMotorGo): 
        
        self.courseGo = courseGo    
        ''' Indicates whether the FSM should be active (go) or not (stop).'''
        self.sL_meas = sL_meas      
        ''' Left wheel encoder measurement, used to track distance traveled by the left wheel.'''
        self.sR_meas = sR_meas      
        ''' Right wheel encoder measurement, used to track distance traveled by the right wheel.'''
        self.lineCorr = lineCorr    
        ''' Line correction signal, which is used in line-following states to adjust the wheel speeds based on the robot's position relative to the line.'''
        self.steerGain = steerGain  
        ''' Steering gain, which can be adjusted to change how aggressively the robot steers in response to the line correction signal.'''
        self.bumpFlag = bumpFlag    
        ''' Indicates whether the bump sensor has been triggered, used in the bump and recovery states.'''
        self.fsmState = fsmState    
        ''' Current state of the FSM for monitoring or debugging purposes.'''
        self.mode = mode            
        ''' Current mode of operation (stop, line follow, open loop) for use by other tasks that control the motors.'''
        self.leftSetpoint = leftSetpoint    
        ''' Desired speed setpoint for the left motor, which is updated in each state based on the behavior required (e.g., line following, straight, turn).'''
        self.rightSetpoint = rightSetpoint   
        ''' Desired speed setpoint for the right motor, similar to leftSetpoint.'''
        self.leftMotorGo = leftMotorGo       
        ''' Flag to enable or disable the left motor, which is set to True when the FSM wants the left motor to run and False when it should stop.'''
        self.rightMotorGo = rightMotorGo    
        ''' Flag to enable or disable the right motor, similar to leftMotorGo.'''

        self.state = S0_INIT
        self.state_entry = True 
        '''Flag to indicate first loop in a state (for init actions)'''
        self.start_sL = 0.0 
        '''Initial wheel encoder readings (for distance tracking)'''
        self.start_sR = 0.0
        self.start_time = 0.0

    def _turn_wheel_arc_inplace(self, angle_deg):     
        '''Arc length each wheel must travel for a given in-place rotation (about midpoint)'''
        angle_rad = math.radians(abs(angle_deg))      
        radius = WHEEL_BASE / 2.0
        return radius * angle_rad

    def _capture_refs(self):    
        '''Capture current encoder readings and time to use as reference for distance-based transitions in the current state'''
        try:
            self.start_sL = float(self.sL_meas.get())
        except:
            self.start_sL = 0.0
        try:
            self.start_sR = float(self.sR_meas.get())
        except:
            self.start_sR = 0.0
        self.start_time = time.ticks_ms() / 1000.0

    def _dist_since_left(self): 
        '''Distance traveled by left wheel since _capture_refs() was called (positive forward, negative reverse)'''
        return float(self.sL_meas.get()) - self.start_sL

    def _dist_since_right(self):
        '''Distance traveled by right wheel since _capture_refs() was called (positive forward, negative reverse)'''
        return float(self.sR_meas.get()) - self.start_sR

    def run(self): 
        '''The main loop of the FSM task, which should be called repeatedly by the scheduler. It checks the current state, performs actions, and transitions between states based on sensor inputs and timing.'''
        while True:
            # publish state
            self.fsmState.put(self.state)

            go = bool(self.courseGo.get())  #Check if the courseGo flag is set to determine whether to start or stop the FSM. If not set, reset to initial state and wait for go signal.'''

            if not go:  # If go is False, the FSM should be inactive. In this case, we set the mode to STOP, disable both motors, reset setpoints to 0, capture the current encoder readings as reference for when we start again, reset the line correction signal, and transition back to the initial state (S0_INIT) while setting the state_entry flag to True for initialization.
                self.mode.put(MODE_STOP)
                self.leftMotorGo.put(False)
                self.rightMotorGo.put(False)
                self.leftSetpoint.put(0.0)
                self.rightSetpoint.put(0.0)
                self.start_sL = float(self.sL_meas.get())
                self.start_sR = float(self.sR_meas.get())
                self.lineCorr.put(0.0)
                self.state = S0_INIT
                self.state_entry = True
                yield self.state
                continue            

            # ---- S0 INIT ----
            if self.state == S0_INIT:   
                '''In the initial state, the robot is stopped and waiting for the go signal. Once go is received, it transitions to the first line-following state.'''
                self.mode.put(MODE_STOP)
                self.leftMotorGo.put(False)
                self.rightMotorGo.put(False)
                self.leftSetpoint.put(0.0)
                self.rightSetpoint.put(0.0)
                if go:
                    self.bumpFlag.put(False)
                    self.state = S1_LF1
                    self.steerGain.put(0.01)
                    self.state_entry = True

            # ---- S1 LF1 ----
            elif self.state == S1_LF1:  
                '''In the first line-following state, the robot uses the line correction signal to adjust its wheel speeds while moving forward. It transitions to the next state after traveling a certain distance along the line.'''
                if self.state_entry:
                    self._capture_refs() 
                    self.state_entry = False
                self.mode.put(MODE_LINE_FOLLOW) 
                '''Set mode to line following, which will cause the line correction signal to be updated by the line sensor task.'''
                self.leftMotorGo.put(True) 
                self.rightMotorGo.put(True)
                corr = float(self.lineCorr.get())   
                '''Get the current line correction signal, which indicates how much the robot should steer to stay on the line. A positive value means the line is to the right, so the robot should steer right (increase left wheel speed, decrease right wheel speed).'''
                base = V_LF # Base speed for line following.
                self.leftSetpoint.put(base + corr)  
                '''Adjust wheel speed based on correction.'''
                self.rightSetpoint.put(base - corr) # Adjust right wheel speed based on correction (opposite of left).

                left_dist = float(self.sL_meas.get())   
                right_dist = float(self.sR_meas.get())
                avg_dist = 0.5*(left_dist + right_dist) # Average distance traveled by wheels since the start of this state.
                start_avg = 0.5*(self.start_sL + self.start_sR) 
                dist_ok = (avg_dist - start_avg) >= D_LF1_STRAIGHT  
                '''Check if the robot has traveled the required distance along the line to transition to the next state.'''
                if dist_ok: 
                    '''If the distance condition is met, transition to the next state (S2_LF2) and set the state_entry flag to True to perform any initialization actions for the new state.'''
                    self.state = S2_LF2
                    self.state_entry = True
            
            # ---- S2 LF2 ----

            elif self.state == S2_LF2: 
                '''In the second line-following state, the robot continues to follow the line but at a slower speed (V_LFCURVE) to prepare for an upcoming curve. It transitions to the next state after traveling a shorter distance along the line.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_LINE_FOLLOW)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                corr = float(self.lineCorr.get())
                base = V_LFCURVE
                self.leftSetpoint.put(base + corr)
                self.rightSetpoint.put(base - corr)

                avg_dist = 0.5*(float(self.sL_meas.get()) + float(self.sR_meas.get()))
                start_avg = 0.5*(self.start_sL + self.start_sR)
                dist_ok = (avg_dist - start_avg) >= D_LF1_CURVE
                if dist_ok:
                    self.state = S3_LILCURVE
                    self.state_entry = True
            
            # ---- S3 LILCURVE (in-place) ----
            elif self.state == S3_LILCURVE: 
                '''In the "little curve" state, the robot performs a small in-place turn to adjust its heading. This is done by setting one wheel to move forward and the other to move in reverse at the same speed (V_TURN). The transition to the next state occurs after either wheel has traveled a certain distance, which corresponds to the arc length needed for the desired turn angle.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(V_TURN)   
                self.rightSetpoint.put(-V_TURN) 
                L_dist = float(self.sL_meas.get())
                start_L_dist = (self.start_sL)
                dist_ok = (L_dist - start_L_dist) >= D_LILCURVE
                if dist_ok:
                    self.state = S4_STRAIGHT1
                    self.state_entry = True
            
            # ---- S4 STRAIGHT1 ----
            elif self.state == S4_STRAIGHT1: 
                '''In the first straight segment state, the robot moves forward at a slower speed (V_STRAIGHT1) for a short distance. This is likely to ensure that the robot is properly aligned and has cleared any obstacles before performing the next turn. The transition to the next state occurs after traveling the specified distance.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_OPEN_LOOP)   
                '''Open loop control for straight movement, no line following.'''
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(V_STRAIGHT1)  # Both motors set to the same speed for straight movement.
                self.rightSetpoint.put(V_STRAIGHT1)
                avg_dist = 0.5*(float(self.sL_meas.get()) + float(self.sR_meas.get()))
                start_avg = 0.5*(self.start_sL + self.start_sR)
                if (avg_dist - start_avg) >= D_STRAIGHT1:
                    self.state = S5_RIGHT90
                    self.state_entry = True

            # ---- S5 RIGHT 90 (in-place) ----
            elif self.state == S5_RIGHT90:  
                '''In the right 90-degree turn state, the robot performs an in-place turn to the right by setting the left wheel to move forward and the right wheel to move in reverse at the same speed (V_TURN). The transition to the next state occurs after either wheel has traveled a distance corresponding to a 90-degree turn arc length.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(V_TURN)   
                self.rightSetpoint.put(-V_TURN) 
                L_dist = float(self.sL_meas.get())
                start_L_dist = (self.start_sL)
                dist_ok = (L_dist - start_L_dist) >= D_RIGHT90
                if dist_ok:
                    self.leftSetpoint.put(0.0)
                    self.rightSetpoint.put(0.0)
                    self.bumpFlag.put(False)
                    self.state = S6_BUMP
                    self.state_entry = True

            # ---- S6 BUMP ----
            elif self.state == S6_BUMP: 
                '''In the bump state, the robot moves forward at a moderate speed (V_STRAIGHT) while monitoring the bump sensor. If the bump sensor is triggered (bumpFlag becomes True), it immediately stops and transitions to the recovery state (S7_RECOVER) to back up and try to get around the obstacle.'''
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(V_STRAIGHT)
                self.rightSetpoint.put(V_STRAIGHT)
                if bool(self.bumpFlag.get()):
                    self.leftSetpoint.put(0.0)
                    self.rightSetpoint.put(0.0)
                    self.bumpFlag.put(False)
                    self.state = S7_RECOVER
                    self.state_entry = True

            # ---- S7 RECOVER ----
            elif self.state == S7_RECOVER:  
                '''In the recovery state, the robot attempts to back up and get around the obstacle that caused the bump. It does this by reversing both wheels at a moderate speed (V_STRAIGHT) for a short distance (D_RECOVER).'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(-V_STRAIGHT)
                self.rightSetpoint.put(-V_STRAIGHT)
                avg_dist = 0.5*(float(self.sL_meas.get()) + float(self.sR_meas.get()))
                start_avg = 0.5*(self.start_sL + self.start_sR)
                if abs(avg_dist - start_avg) >= D_RECOVER:
                    self.state = S8_LEFT90
                    self.state_entry = True

            # ---- S8 LEFT 90 ----
            elif self.state == S8_LEFT90: 
                '''In the left 90-degree turn state, the robot performs an in-place turn to the left by setting the left wheel to move in reverse and the right wheel to move forward at the same speed (V_TURN). The transition to the next state occurs after either wheel has traveled a distance corresponding to a 90-degree turn arc length. This turn is intended to help the robot navigate around the obstacle it encountered in the bump state.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(-V_TURN)   
                self.rightSetpoint.put(V_TURN) 
                R_dist = float(self.sR_meas.get())
                start_R_dist = (self.start_sR)
                dist_ok = (R_dist - start_R_dist) >= D_LEFT90
                if dist_ok:
                    self.leftSetpoint.put(0.0)
                    self.rightSetpoint.put(0.0)
                    self.state = S9_STRAIGHT2
                    self.state_entry = True

            # ---- S9 STRAIGHT2 ----
            elif self.state == S9_STRAIGHT2:  
                '''In the second straight state, the robot moves forward at a moderate speed (V_STRAIGHT) for a short distance. This is intended to provide a brief period of stable movement before the line can be detected and line following resumes.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(V_STRAIGHT)
                self.rightSetpoint.put(V_STRAIGHT)
                avg_dist = 0.5*(float(self.sL_meas.get()) + float(self.sR_meas.get()))
                start_avg = 0.5*(self.start_sL + self.start_sR)
                if (avg_dist - start_avg) >= D_STRAIGHT2:
                    self.state = S10_LF3
                    self.state_entry = True

            # ---- S10 LF3 ----
            elif self.state == S10_LF3: 
                '''In the third line-following state, the robot follows the line at a slower speed (V_LF3) for a short distance. This is intended to focus the robot on the line to prepare for the upcoming turn.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_LINE_FOLLOW)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                corr = float(self.lineCorr.get())
                base = V_LF3
                self.leftSetpoint.put(base + corr)
                self.rightSetpoint.put(base - corr)
                avg_dist = 0.5*(float(self.sL_meas.get()) + float(self.sR_meas.get()))
                start_avg = 0.5*(self.start_sL + self.start_sR)
                dist_ok = (avg_dist - start_avg) >= D_LFOUTG
                if dist_ok:
                    self.state = S11_RIGHT45
                    self.state_entry = True 

            # ---- S11 RIGHT 45 (in-place) ----
            elif self.state == S11_RIGHT45: 
                '''In the right 45-degree turn state, the robot performs a 45-degree heading adjustment to cut off the upcoming 90-degree turn. This is done because line following through a 90-degreee turn is unreliable, so the 45-degree adjustment allows the robot to find the path at an acute angle, which will ensure reliable detection and course correction.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(V_TURN)   
                self.rightSetpoint.put(-V_TURN) 
                L_dist = float(self.sL_meas.get())  # Distance traveled by left wheel since the start of this state.
                start_L_dist = (self.start_sL)  
                dist_ok = (L_dist - start_L_dist) >= 0.5*D_RIGHT90  # Check if the left wheel has traveled the distance corresponding to a 45-degree turn (half of the 90-degree turn arc length).
                if dist_ok:
                    self.leftSetpoint.put(0.0)
                    self.rightSetpoint.put(0.0)
                    self.state = S12_LFPP
                    self.state_entry = True 

            # ---- S12 LFPP ----
            elif self.state == S12_LFPP:    
                '''In the final line-following state, the robot follows the line at a slower speed (V_LFCURVE) to navigate the slolum, the portion of the track with tight windy turns. The transition to the next state (S13_TURN180) occurs after traveling the specified distance along the line.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_LINE_FOLLOW)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                corr = float(self.lineCorr.get())
                base = V_LFCURVE
                self.leftSetpoint.put(base + corr)
                self.rightSetpoint.put(base - corr)
                avg_dist = 0.5*(float(self.sL_meas.get()) + float(self.sR_meas.get()))
                start_avg = 0.5*(self.start_sL + self.start_sR)
                dist_ok = (avg_dist - start_avg) >= D_LF_CURVE
                if dist_ok:
                    self.state = S13_TURN180
                    self.state_entry = True                                            

            # ---- S13 TURN 180 (in-place) ----
            elif self.state == S13_TURN180: 
                '''In the "180-degree" turn state, the robot performs an in-place turn to reverse its heading. The final section of the course has a curving 90-degree turn into finish location. This state's turn is adjusted to less than 180-degrees so that the robot can shortcut to the finish location by driving a straight secant line of the final curve.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                    self._turn_arc_target = self._turn_wheel_arc_inplace(170.0) 
                    '''Calculate the arc length that each wheel must travel for a 170-degree in-place turn, which will be used as the distance threshold for transitioning to the next state. The angle is set to 170 degrees instead of 180 to allow the robot to cut the corner and drive straight to the finish line, which is more faster than following the curve using line following.'''
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(-V_TURN)
                self.rightSetpoint.put(V_TURN)

                if (abs(self._dist_since_left()) >= self._turn_arc_target or
                        abs(self._dist_since_right()) >= self._turn_arc_target):    # Check if either wheel has traveled the required arc length for the turn. Since it's an in-place turn, both wheels should ideally travel the same distance, but we check both to ensure we don't miss the transition due to any discrepancies in wheel speeds or encoder readings.
                    self.leftSetpoint.put(0.0)
                    self.rightSetpoint.put(0.0)
                    self.state = S14_STRAIGHTFIN
                    self.state_entry = True

            # ---- S14 STRAIGHT FIN ----
            elif self.state == S14_STRAIGHTFIN: 
                '''In the final straight segment state, the robot drives straight towards the finish line at a moderate speed (V_STRAIGHT). The transition to the end state (S15_END) occurs after traveling the specified distance.'''
                if self.state_entry:
                    self._capture_refs()
                    self.state_entry = False
                self.mode.put(MODE_OPEN_LOOP)
                self.leftMotorGo.put(True)
                self.rightMotorGo.put(True)
                self.leftSetpoint.put(V_STRAIGHT)
                self.rightSetpoint.put(V_STRAIGHT)
                avg_dist = 0.5*(float(self.sL_meas.get()) + float(self.sR_meas.get()))
                start_avg = 0.5*(self.start_sL + self.start_sR)
                if (avg_dist - start_avg) >= D_STRAIGHTFIN:
                    self.state = S15_END
                    self.state_entry = True

            # ---- S15 END ----
            elif self.state == S15_END: 
                '''In the end state, the robot has completed the course and will stop within the finish position, covering the dot to qualify for a perfect run. The mode is set to STOP, both motors are disabled, and the setpoints are reset to 0. The FSM remains in this state until it receives a new go signal, at which point it will transition back to the initial state (S0_INIT) to start the course again.'''
                self.mode.put(MODE_STOP)
                self.leftSetpoint.put(0.0)
                self.rightSetpoint.put(0.0)
                self.leftMotorGo.put(False)
                self.rightMotorGo.put(False)
                self.courseGo.put(False)
                self.state = S0_INIT
            yield self.state
