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
left_air = [-90, -36, -30, 74, 0, -45]
left_pos = [-90, -36, -120, 74, 0, -45]
mid_air = [0, -36, -30, 74, 0, -45]
right_air = [135, -36, -30, 74, 0, -45]
right_pos = [135, -40, -120, 74, 0, 0]

speed = 50
time.sleep(1)
mc.send_angles(home, speed)
time.sleep(2)
mc.send_angles(left_air, speed)
time.sleep(2)
mc.send_angles(left_pos, speed)
time.sleep(2)
mc.set_gripper_state(1, 70)
time.sleep(2)
mc.send_angles(left_air, speed)
time.sleep(2)
mc.send_angles(mid_air, speed)
time.sleep(2)
mc.send_angles(right_air, speed)
time.sleep(2)
mc.send_angles(right_pos, speed)
time.sleep(2)
mc.set_gripper_state(0, 70)
time.sleep(2)
mc.send_angles(right_air, speed)
time.sleep(2)
mc.send_angles(mid_air, speed)
time.sleep(2)
mc.send_angles(home, speed)
time.sleep(2)
