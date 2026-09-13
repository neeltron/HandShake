# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 01:55:06 2026

@author: neeltron
"""

from pymycobot.mycobot import MyCobot
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = "1000000"

mc = MyCobot(PORT, BAUDRATE)

home = [0, 0, 0, 0, 0, 45]
left_air = [-90, 0, 0, 0, 0, 45]
left_pos = [-90, -36, -120, 74, 0, -45]
mid_air = [0, -36, -30, 74, 0, -45]
right_air = [135, -36, -30, 74, 0, -45]
right_pos = [90, -40, -120, 74, 0, 0]

left_grab = [-90, -28, -60, 95, 0, 135]

left_take = [-90, 0, -60, 135, 0, 135]

speed = 50
mc.set_gripper_state(0, 70)
time.sleep(1)
mc.send_angles(home, speed)
time.sleep(2)
mc.send_angles(left_air, speed)

time.sleep(10)
mc.send_angles(left_grab, speed)
time.sleep(2)
mc.set_gripper_state(1, 70)
time.sleep(20)
# confirm here
mc.send_angles(left_take, speed)
time.sleep(2)
mc.send_angles(mid_air, speed)
time.sleep(2)
mc.send_angles(right_pos, speed)
