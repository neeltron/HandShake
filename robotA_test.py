# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 01:55:06 2026

@author: neeltron
"""

from pymycobot.mycobot import MyCobot
import time

PORT = "/dev/ttyUSB1"
BAUDRATE = "1000000"

mc = MyCobot(PORT, BAUDRATE)

home = [0, 0, 0, 0, 0, -45]
obj_1 = [0, -60, -50, 30, 0, -45]
obj_2 = [-30, -60, -50, 30, 0, -45]
left_air = [-90, -36, -30, 74, 0, -45]
left_pos = [-90, -36, -120, 74, 0, -45]
mid_air = [0, -36, -30, 74, 0, -45]
right_air = [90, -36, -30, 74, 0, -45]
right_pos = [90, -40, -120, 74, 0, 0]
mc.set_gripper_state(0, 70)
speed = 50
time.sleep(1)
mc.send_angles(home, speed)
time.sleep(2)
mc.send_angles(obj_1, speed)
time.sleep(2)
mc.set_gripper_state(1, 70)
time.sleep(2)
mc.send_angles(mid_air, speed)
time.sleep(2)
mc.send_angles(right_air, speed)
time.sleep(2)
#confirm here

mc.set_gripper_state(0, 70)
time.sleep(2)
#confirm here
mc.send_angles(home, speed)
time.sleep(2)
# confirm here
mc.send_angles(obj_2, speed)
time.sleep(2)
mc.set_gripper_state(1, 70)
time.sleep(2)
mc.send_angles(mid_air, speed)
time.sleep(2)
mc.send_angles(right_air, speed)
time.sleep(2)
#confirm here

mc.set_gripper_state(0, 70)
time.sleep(2)
#confirm here
