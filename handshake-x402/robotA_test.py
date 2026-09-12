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

target_angles = [0, 0, 0, 0, 0, 0]
speed = 50

mc.send_angles(target_angles, speed)
time.sleep(2)

mc.send_angle(2, 0, speed)

print("J1 min/max:", mc.get_joint_min_angle(1), mc.get_joint_max_angle(1))

print("Current angles:", mc.get_angles)
