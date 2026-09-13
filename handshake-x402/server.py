# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 15:50:57 2026

@author: neeltron
"""

import base64
import json
import requests
from flask import Flask, request, jsonify

FACILITATOR_URL = "https://api.testnet.blocky402.com"
ROBOT_A_ACCOUNT_ID = "0.0.10422144"

OBJECT_PRICES_HBAR = {
    "cube-01": "10",
    "cube-03": "50",
}

app = Flask(__name__)


def get_facilitator_fee_payer() -> str:
    resp = requests.get(f"{FACILITATOR_URL}/supported", timeout=10)
    resp.raise_for_status()
    for entry in resp.json().get("kinds", []):
        if entry.get("network") == "hedera:testnet":
            return entry["extra"]["feePayer"]
    raise RuntimeError("Facilitator does not advertise hedera:testnet support")


def build_payment_requirements(fee_payer: str, object_id: str) -> dict:
    if object_id not in OBJECT_PRICES_HBAR:
        raise ValueError(f"Unknown object_id: {object_id!r}")

    amount_tinybars = str(int(float(OBJECT_PRICES_HBAR[object_id]) * 100_000_000))

    return {
        "scheme": "exact",
        "network": "hedera:testnet",
        "amount": amount_tinybars,
        "asset": "0.0.0",
        "payTo": ROBOT_A_ACCOUNT_ID,
        "maxTimeoutSeconds": 180,
        "extra": {"feePayer": fee_payer},
    }


@app.post("/release-object")
def release_object():
    payment_header = request.headers.get("X-PAYMENT")
    body = request.get_json(silent=True) or {}
    object_id = body.get("objectId")

    if not payment_header:
        if object_id not in OBJECT_PRICES_HBAR:
            return jsonify({"error": f"Unknown or missing objectId: {object_id!r}"}), 400

        fee_payer = get_facilitator_fee_payer()
        requirements = build_payment_requirements(fee_payer, object_id)
        return jsonify({
            "x402Version": 2,
            "accepts": [requirements],
            "error": "Payment required to release object",
        }), 402

    payment_payload = json.loads(base64.b64decode(payment_header))

    verify_resp = requests.post(f"{FACILITATOR_URL}/verify", json={
        "paymentPayload": payment_payload,
        "paymentRequirements": payment_payload["accepted"],
    }, timeout=10)
    if not verify_resp.json().get("isValid"):
        return jsonify({"error": "Payment invalid"}), 402

    settle_resp = requests.post(f"{FACILITATOR_URL}/settle", json={
        "paymentPayload": payment_payload,
        "paymentRequirements": payment_payload["accepted"],
    }, timeout=30)
    settlement = settle_resp.json()
    if not settlement.get("success"):
        return jsonify({"error": "Settlement failed", "detail": settlement}), 402

    print(f"[Robot A] Payment settled ({settlement.get('transactionId')}) — releasing: {object_id}")

    return jsonify({"status": "released", "objectId": object_id, "settlement": settlement})


if __name__ == "__main__":
    print(f"payments to be settled to {ROBOT_A_ACCOUNT_ID}")
    print(f"Known objects and prices: {OBJECT_PRICES_HBAR}")
    app.run(port=4021)