# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 16:13:24 2026

@author: neeltron
"""

import base64
import json
import os
import requests
from hiero_sdk_python import AccountId, Client, PrivateKey, TransactionId, TransferTransaction

ROBOT_B_ACCOUNT_ID = "0.0.10447952"
ROBOT_A_URL = "http://localhost:4021"

buyer_account = AccountId.from_string(ROBOT_B_ACCOUNT_ID)
buyer_key = PrivateKey.from_string_ecdsa(os.environ["ROBOT_B_PRIVATE_KEY"])

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


def pay_for_handoff(object_id: str):
    resp = requests.post(f"{ROBOT_A_URL}/release-object", json={"objectId": object_id})

    if resp.status_code == 402:
        print("its payday 🚀")
        requirements = resp.json()["accepts"][0]
        payment_payload = {
            "x402Version": 2,
            "resource": {"url": f"{ROBOT_A_URL}/release-object"},
            "accepted": requirements,
            "payload": {"transaction": build_signed_transfer(requirements)},
        }
        header = base64.b64encode(json.dumps(payment_payload).encode()).decode()
        resp = requests.post(
            f"{ROBOT_A_URL}/release-object",
            json={"objectId": object_id},
            headers={"X-PAYMENT": header},
        )

    print(resp.status_code, resp.json())


if __name__ == "__main__":
    pay_for_handoff("cube-01")