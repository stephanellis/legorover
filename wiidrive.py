#! /usr/bin/env python

import cwiid
from rrb3 import *
import time
import sys

class Bullrover(object):
    """
    Bullrover is a raspberry pi 3 with a Raspirobot board v4 controlled by
    a wiimote.  Yeah!
    """
    def __init__(self, wm, batt_voltage=9, motor_voltage=9, poll_interval=.2):
        self.BATT_VOLTAGE = batt_voltage
        self.MOTOR_VOLTAGE = motor_voltage
        self.r = RRB3(self.BATT_VOLTAGE, self.MOTOR_VOLTAGE)
        self.r.set_led1(False)
        self.POLL_INTERVAL = poll_interval
        self.MOTOR_MAX = 1.0
        self.MOTOR_MIN = -1.0
        self.STICK_ENABLED = False
        self.X_MAX = 224
        self.X_CNT = 132
        self.X_MIN = 32
        self.X_RNG = self.X_MAX - self.X_MIN
        self.Y_MAX = 230
        self.Y_CNT = 130
        self.Y_MIN = 32
        self.Y_RNG = self.Y_MAX - self.Y_MIN
        self.wm = wm

    def set_motors_bystick(self):
        x, y = self.wm.state["nunchuk"]["stick"]
        print("Stick raw values: %i, %i" % (x,y))
        nx = x - self.X_CNT
        ny = y - self.Y_CNT
        print("Stick norm values: %i, %i" % (nx, ny))
        s = float(abs(ny)) / (float(self.Y_RNG) / 2)
        m = float(abs(nx)) / (float(self.X_RNG) / 2)
        sl = s
        sr = s
        d = 0
        if ny < 0:
            d = 1
        if nx > 0:
            sl = sl - m
        else:
            sr = sr - m
        if sl > 1.0:
            sl = 1.0
        if sr > 1.0:
            sr = 1.0
        sl = abs(round(sl, 1))
        sr = abs(round(sr, 1))
        print("%f, %i, %f, %i" % (sl, d, sr ,d))
        self.r.set_motors(sl, d, sr, d)
        

    def stop_motors(self):
        self.r.set_motors(0,0,0,0)

    def skid_left(self):
        self.r.set_motors(1,1,1,0)

    def skid_right(self):
        self.r.set_motors(1,0,1,1)

    def full_forward(self):
        self.r.set_motors(1,0,1,0)

    def full_reverse(self):
        self.r.set_motors(1,1,1,1)

    def toggle_stick(self):
        if not self.STICK_ENABLED:
            self.STICK_ENABLED = True
            self.r.set_led1(True)
        else:
            self.STICK_ENABLED = False
            self.r.set_led1(False)
            self.stop_motors()
        
    def main(self):
        while True:
            print(self.wm.state)
            print ("Stick enabled: %s" % self.STICK_ENABLED)
            if wm.state["buttons"] & cwiid.BTN_HOME:
                break
            if wm.state["buttons"] & cwiid.BTN_A:
                self.stop_motors()
            if wm.state["buttons"] & cwiid.BTN_UP:
                self.full_forward()
            if wm.state["buttons"] & cwiid.BTN_DOWN:
                self.full_reverse()
            if wm.state["buttons"] & cwiid.BTN_LEFT:
                self.skid_left()
            if wm.state["buttons"] & cwiid.BTN_RIGHT:
                self.skid_right()
            if wm.state["nunchuk"]["buttons"] & cwiid.NUNCHUK_BTN_Z:
                self.stop_motors()
            if wm.state["nunchuk"]["buttons"] & cwiid.NUNCHUK_BTN_C:
                self.toggle_stick()
            if self.STICK_ENABLED:
                self.set_motors_bystick()
            time.sleep(self.POLL_INTERVAL)
        self.stop_motors()
        self.set_led1(False)
        sys.exit(1)

if __name__ == "__main__":
    print("Trying to connect to wiimote...")
    wm = None
    while True:
        try:
            wm = cwiid.Wiimote()
            wm.rumble = True
            time.sleep(1)
            wm.rumble = False
            wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK
            print("Wiimote connected. Running mainloop...")
            break
        except RuntimeError:
            print("failed to connect to wiimote, trying to connect again...")

    b = Bullrover(wm)
    b.main()

                
                
