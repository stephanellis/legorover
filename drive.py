#! /usr/bin/env python

DEBUG=False

if not DEBUG:
    from rrb3 import *
import sys


class Vehicle(object):

    def __init__(self, batt_voltage=5, motor_voltage=9):
        self.K_FORWARD = "w"
        self.K_REVERSE = "s"
        self.K_LEFT = "a"
        self.K_RIGHT = "d"
        self.K_STOP = " "
        self.SPEED_MAX = 1.0
        self.SPEED_MIN = -1.0
        self.SPEED_STEP = 0.2
        self.batt_voltage = batt_voltage
        self.motor_voltage = motor_voltage
        self.speed = dict(left=0.0, right=0.0)
        self.r = None
        if not DEBUG:
            self.r = RRB3(self.batt_voltage, self.motor_voltage)

    # this function was ripped from here:
    # https://stackoverflow.com/a/6599441
    def read_single_keypress(self):
        """Waits for a single keypress on stdin.

        This is a silly function to call if you need to do it a lot because it has
        to store stdin's current setup, setup stdin for reading single keystrokes
        then read the single keystroke then revert stdin back after reading the
        keystroke.

        Returns the character of the key that was pressed (zero on
        KeyboardInterrupt which can happen when a signal gets handled)

        """
        import termios, fcntl, sys, os
        fd = sys.stdin.fileno()
        # save old state
        flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
        attrs_save = termios.tcgetattr(fd)
        # make raw - the way to do this comes from the termios(3) man page.
        attrs = list(attrs_save) # copy the stored version to update
        # iflag
        attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                      | termios.ISTRIP | termios.INLCR | termios. IGNCR
                      | termios.ICRNL | termios.IXON )
        # oflag
        attrs[1] &= ~termios.OPOST
        # cflag
        attrs[2] &= ~(termios.CSIZE | termios. PARENB)
        attrs[2] |= termios.CS8
        # lflag
        attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                      | termios.ISIG | termios.IEXTEN)
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        # turn off non-blocking
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
        # read a single keystroke
        try:
            ret = sys.stdin.read(1) # returns a single character
        except KeyboardInterrupt:
            ret = 0
        finally:
            # restore old state
            termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
        return ret

    def display_state(self):
        print("Left Speed: %f / Right Speed: %f\n" %
            (
            self.speed["left"],
            self.speed["right"]
            )
        )

    def set_motors(self):
        ld = 0
        rd = 0
        if self.speed["left"] < 0:
            ld = 1
        if self.speed["right"] < 0:
            rd = 1
        motor_args = [abs(self.speed["left"]), ld, abs(self.speed["right"]), rd]
        print("setting motors %f %i %f %i" % tuple(motor_args))
        if not DEBUG:
            self.r.set_motors(*motor_args)

    def incr_speed(self, motor="both"):
        if motor == "both" or motor == "left":
            if self.speed["left"] < self.SPEED_MAX:
                self.speed["left"] += self.SPEED_STEP
        if motor == "both" or motor == "right":
            if self.speed["right"] < self.SPEED_MAX:
                self.speed["right"] += self.SPEED_STEP

    def decr_speed(self, motor="both"):
        if motor == "both" or motor == "left":
            if self.speed["left"] > self.SPEED_MIN:
                self.speed["left"] -= self.SPEED_STEP
        if motor == "both" or motor == "right":
            if self.speed["right"] > self.SPEED_MIN:
                self.speed["right"] -= self.SPEED_STEP

    def dispatch(self, ch):
        if ch == self.K_FORWARD:
            self.incr_speed()
        if ch == self.K_STOP:
            self.speed["left"] = 0.0
            self.speed["right"] = 0.0
        if ch == self.K_REVERSE:
            self.decr_speed()
        if ch == self.K_RIGHT:
            self.incr_speed(motor="left")
            self.decr_speed(motor="right")
        if ch == self.K_LEFT:
            self.incr_speed(motor="right")
            self.decr_speed(motor="left")
        self.set_motors()

    def main(self):
        """
        loop forever waiting for keypresses, pass key presses except for x or q
        to the dispatcher
        """
        while True:
            self.display_state()
            ch = self.read_single_keypress()
            print("User Pressed key: %s" % ch)
            if ch == "x" or ch == "q":
                break
            self.dispatch(ch)
        sys.exit(0)

if __name__ == "__main__":
    v = Vehicle()
    v.main()
