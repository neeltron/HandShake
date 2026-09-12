# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 16:15:50 2026

@author: neeltron
"""

from eth_account import Account

account = Account.create()

print("Public - ", account.address)
print("Private - ")
print(account.key.hex())
