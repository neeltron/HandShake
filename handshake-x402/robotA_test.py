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

home = [0, 0, 0, 0, 0, 0]

left_air = [-90, -38, -30, 72, 0, -45]

left_pos = [-90, -38, -120, 72, 0, -45]



speed = 50
time.sleep(1)
mc.send_angles(home, speed)
time.sleep(2)
mc.send_angles(left_air, speed)
time.sleep(2)
mc.send_angles(left_pos, speed)

print("Current angles:", mc.get_angles)
