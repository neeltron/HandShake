# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 04:54:43 2026

@author: neeltron
"""

import json
import os
from web3 import Web3

RPC_URL = "https://sepolia.base.org"
CONTRACT_ADDRESS = "0x725C1614Eb1c9E160E4B07d809D19205c1a5a669"
ROBOT_A_ONCHAIN_ADDRESS = "0x1936Cb005DB976AB1251C3b887Ede572A5E4513f"
OBJECT_LABEL = "cube-01"


def read_key(filename):
    with open(os.path.join("..", filename)) as f:
        return f.read().strip()


with open("objcustody.abi.json") as f:
    abi = json.load(f)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
robot_b_key = read_key("X402_PRIVATE_KEY.txt")
robot_b_account = w3.eth.account.from_key(robot_b_key)

contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
object_id = Web3.keccak(text=OBJECT_LABEL)

current_holder = contract.functions.holderOf(object_id).call()
print(f"Current holder of {OBJECT_LABEL}: {current_holder}")

if current_holder.lower() == ROBOT_A_ONCHAIN_ADDRESS.lower():
    print("Already held by Robot A — nothing to reset.")
else:
    tx = contract.functions.transferCustody(
        object_id, Web3.to_checksum_address(ROBOT_A_ONCHAIN_ADDRESS)
    ).build_transaction({
        "from": robot_b_account.address,
        "nonce": w3.eth.get_transaction_count(robot_b_account.address),
        "gas": 200_000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = robot_b_account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"{OBJECT_LABEL} custody returned to Robot A ({ROBOT_A_ONCHAIN_ADDRESS})")
    print("Tx hash:", tx_hash.hex())