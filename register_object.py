# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 17:44:49 2026

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
CONTRACT_ADDRESS = "725C1614Eb1c9E160E4B07d809D19205c1a5a669"
OBJECT_LABEL = os.environ.get("OBJECT_LABEL", "cube-01")

with open("objcustody.abi.json") as f:
    abi = json.load(f)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(DEPLOYER_PRIVATE_KEY)
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
object_id = Web3.keccak(text=OBJECT_LABEL)

tx = contract.functions.registerObject(object_id, OBJECT_LABEL).build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address),
    "gas": 200_000,
    "gasPrice": w3.eth.gas_price,
})
signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
w3.eth.wait_for_transaction_receipt(tx_hash)

print(f'Registered "{OBJECT_LABEL}"')
print("ObjectID (bytes32, hex):", object_id.hex())