# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 17:39:17 2026

@author: neeltron
"""

import json
import os
from web3 import Web3

def read_key(filename):
    with open(os.path.join("..", filename)) as f:
        return f.read().strip()

RPC_URL = os.environ.get("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
DEPLOYER_PRIVATE_KEY = read_key("DEPLOYER_PRIVATE_KEY.txt")

with open("objcustody.abi.json") as f:
    abi = json.load(f)
with open("objcustody.bytecode.txt") as f:
    bytecode = f.read().strip()

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(DEPLOYER_PRIVATE_KEY)
w3.eth.default_account = account.address

balance = w3.eth.get_balance(account.address)
if balance == 0:
    raise RuntimeError("no money for gas, we broke :(")

Custody = w3.eth.contract(abi=abi, bytecode=bytecode)
tx = Custody.constructor().build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address),
    "gas": 1_000_000,
    "gasPrice": w3.eth.gas_price,
})
signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Deployed to:", receipt.contractAddress)
print("Deployment block:", receipt.blockNumber)