# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 15:47:39 2026

@author: neeltron
"""

import base64
import os
from hiero_sdk_python import AccountId, Client, PrivateKey, TransactionId, TransferTransaction

ROBOT_B_ACCOUNT_ID = "0.0.10447952"
ROBOT_B_PRIVATE_KEY = os.environ["ROBOT_B_PRIVATE_KEY"]

buyer_account = AccountId.from_string(ROBOT_B_ACCOUNT_ID)
buyer_key = PrivateKey.from_string_ecdsa(ROBOT_B_PRIVATE_KEY)

client = Client.for_testnet()
client.set_operator(buyer_account, buyer_key)

def build_signed_transfer(requirements: dict) -> str:
    pay_to = AccountId.from_string(requirements["payTo"])
    fee_payer = AccountId.from_string(requirements["extra"]["feePayer"])
    amount = int(requirements["amount"])

    tx_id = TransactionId.generate(fee_payer)  # i guess i should charge the facilitator instead of the buyer LMAO

    tx = (
        TransferTransaction()
        .add_hbar_transfer(buyer_account, -amount)
        .add_hbar_transfer(pay_to, amount)
        .set_transaction_id(tx_id)
    )
    tx.freeze_with(client)
    tx.sign(buyer_key)
    return base64.b64encode(tx.to_bytes()).decode()

if __name__ == "__main__":
    requirements = {
        "amount": "1000000", # 0.01 hbar LFG
        "asset": "0.0.0",
        "extra": {"feePayer": "0.0.7162784"},
        "maxTimeoutSeconds": 180,
        "network": "hedera:testnet",
        "payTo": "0.0.10422144",
        "scheme": "exact",
    }
    tx_b64 = build_signed_transfer(requirements)
    print("Signed transaction (base64):")
    print(tx_b64)
    
    