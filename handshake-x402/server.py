# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 15:50:57 2026

@author: neeltron
"""

import requests
from flask import Flask, request, jsonify

FACILITATOR_URL = "https://api.testnet.blocky402.com"
ROBOT_A_ACCOUNT_ID = "0.0.10422144"  # this is the seller

app = Flask(__name__)

def get_facilitator_fee_payer() -> str:
    resp = requests.get(f"{FACILITATOR_URL}/supported", timeout=10)
    resp.raise_for_status()
    for entry in resp.json().get("kinds", []):
        if entry.get("network") == "hedera:testnet":
            return entry["extra"]["feePayer"]
    raise RuntimeError("Facilitator does not advertise hedera:testnet support")

def build_payment_requirements(fee_payer: str) -> dict:
    return {
        "scheme": "exact",
        "network": "hedera:testnet",
        "amount": "1000000",  # 0.01 hbar
        "asset": "0.0.0",
        "payTo": ROBOT_A_ACCOUNT_ID,
        "maxTimeoutSeconds": 180,
        "extra": {"feePayer": fee_payer},
    }

@app.post("/release-object")
def release_object():
    payment_header = request.headers.get("X-PAYMENT")

    if not payment_header:
        fee_payer = get_facilitator_fee_payer()
        requirements = build_payment_requirements(fee_payer)
        return jsonify({
            "x402Version": 2,
            "accepts": [requirements],
            "error": "Payment required to release object",
        }), 402

    # i will work on payment path later, just testing the pipeline up until now
    return jsonify({"status": "not yet implemented"}), 501

if __name__ == "__main__":
    print("Robot A listening on http://localhost:4021")
    app.run(port=4021)