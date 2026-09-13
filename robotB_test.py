# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 01:55:06 2026

@author: neeltron
"""

import base64
import json
import os
import subprocess
import time

import cv2
import requests
from pyzbar.pyzbar import decode
from eth_account import Account
from web3 import Web3
from x402 import x402ClientSync
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.client import ExactEvmScheme
from x402.http.clients.requests import wrapRequestsWithPayment
from hiero_sdk_python import AccountId, Client, PrivateKey, TransactionId, TransferTransaction
from pymycobot.mycobot import MyCobot

PORT = "/dev/ttyUSB0"
BAUDRATE = "1000000"

mc = MyCobot(PORT, BAUDRATE)

ALLOWED_OBJECT_IDS = {"cube-01", "cube-03"}

ROBOT_B_ACCOUNT_ID = "0.0.10447952"
ROBOT_A_URL = "https://entertaining-acknowledge-cat-clearly.trycloudflare.com "

def read_key(filename):
    with open(os.path.join("..", filename)) as f:
        return f.read().strip()

X402_PRIVATE_KEY = read_key("X402_PRIVATE_KEY.txt")
SUBGRAPH_ID = "QmcTd2zdQvix9Cr9GvJsnFeWRNsanya8qD6MnTV5hMntoY"
GRAPH_GATEWAY_URL = os.environ.get("GRAPH_GATEWAY_URL", "https://testnet.gateway.thegraph.com/api/x402")
GRAPH_ENDPOINT = f"{GRAPH_GATEWAY_URL}/subgraphs/id/{SUBGRAPH_ID}"
ROBOT_A_ONCHAIN_ADDRESS = "0x1936Cb005DB976AB1251C3b887Ede572A5E4513f"

buyer_account = AccountId.from_string(ROBOT_B_ACCOUNT_ID)
buyer_key = PrivateKey.from_string_ecdsa(read_key("ROBOT_B_PRIVATE_KEY.txt"))
hedera_client = Client.for_testnet()
hedera_client.set_operator(buyer_account, buyer_key)

_graph_account = Account.from_key(X402_PRIVATE_KEY)
_graph_signer = EthAccountSigner(_graph_account)
_graph_client = x402ClientSync().register("base-sepolia", ExactEvmScheme(_graph_signer))
_graph_session = wrapRequestsWithPayment(requests.Session(), _graph_client)
class QRReadError(Exception):
    pass


class CustodyVerificationError(Exception):
    pass


def speak(text: str):
    print(f"[TTS] {text}")
    subprocess.run(["espeak", text])


def scan_from_camera(camera_index: int = 0, timeout_seconds: float = 10.0) -> dict:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise QRReadError(f"Could not open camera at index {camera_index}")

    start = time.time()
    try:
        while time.time() - start < timeout_seconds:
            ok, frame = cap.read()
            if not ok:
                continue
            results = decode(frame)
            if results:
                raw = results[0].data.decode()
                payload = json.loads(raw)
                for field in ("objectId", "cost", "payTo"):
                    if field not in payload:
                        raise QRReadError(f"QR code missing required field '{field}': {payload}")
                return payload
    finally:
        cap.release()

    raise QRReadError(f"No QR code detected within {timeout_seconds}s")


def get_current_holder(object_id: str) -> str | None:
    object_id_bytes32 = Web3.keccak(text=object_id).hex()
    query = """
    query GetHolder($id: Bytes!) {
      object(id: $id) { id label currentHolder transferCount }
    }
    """
    resp = _graph_session.post(
        GRAPH_ENDPOINT,
        json={"query": query, "variables": {"id": "0x" + object_id_bytes32}},
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise CustodyVerificationError(f"Subgraph query failed: {data['errors']}")
    obj = data.get("data", {}).get("object")
    return obj["currentHolder"] if obj else None


def should_accept_object(offered_object_id: str, robot_a_address: str) -> bool:
    if offered_object_id not in ALLOWED_OBJECT_IDS:
        print(f"'{offered_object_id}' is not on the allowed list {ALLOWED_OBJECT_IDS}.")
        return False

    current_holder = get_current_holder(offered_object_id)
    if current_holder is None:
        raise CustodyVerificationError(f"Object '{offered_object_id}' is not registered on-chain")

    match = current_holder.lower() == robot_a_address.lower()
    print(f"[Custody check] {offered_object_id}: on-chain holder={current_holder}, match={match}")
    return match


def build_signed_transfer(requirements: dict, object_id: str) -> str:
    pay_to = AccountId.from_string(requirements["payTo"])
    fee_payer = AccountId.from_string(requirements["extra"]["feePayer"])
    amount = int(requirements["amount"])
    tx_id = TransactionId.generate(fee_payer)
    tx = (
        TransferTransaction()
        .add_hbar_transfer(buyer_account, -amount)
        .add_hbar_transfer(pay_to, amount)
        .set_transaction_id(tx_id)
        .set_transaction_memo(f"HandShake x402 handoff: {object_id}")
    )
    tx.freeze_with(hedera_client)
    tx.sign(buyer_key)
    return base64.b64encode(tx.to_bytes()).decode()


def verify_and_pay(camera_index: int = 0) -> bool:
    """Scan the QR, verify via The Graph, and pay if authorized.
    Returns True if payment succeeded, False otherwise."""
    print("Looking for QR code on object...")
    try:
        qr = scan_from_camera(camera_index=camera_index, timeout_seconds=15)
    except QRReadError as e:
        speak("Could not read QR code")
        print(e)
        return False

    offered_object_id = qr["objectId"]
    posted_cost_hbar = qr["cost"]
    posted_pay_to = qr["payTo"]

    try:
        if not should_accept_object(offered_object_id, ROBOT_A_ONCHAIN_ADDRESS):
            speak("Wrong object provided")
            return False
    except CustodyVerificationError as e:
        speak("Could not verify object")
        print(e)
        return False

    print(f'"{offered_object_id}" is authorized — requesting release...')
    resp = requests.post(f"{ROBOT_A_URL}/release-object", json={"objectId": offered_object_id})

    if resp.status_code == 402:
        requirements = resp.json()["accepts"][0]

        server_amount_hbar = int(requirements["amount"]) / 100_000_000
        if abs(server_amount_hbar - float(posted_cost_hbar)) > 1e-8:
            speak("Price mismatch, payment aborted")
            return False
        if requirements["payTo"] != posted_pay_to:
            speak("Payee mismatch, payment aborted")
            return False

        payment_payload = {
            "x402Version": 2,
            "resource": {"url": f"{ROBOT_A_URL}/release-object"},
            "accepted": requirements,
            "payload": {"transaction": build_signed_transfer(requirements, offered_object_id)},
        }
        payment_header = base64.b64encode(json.dumps(payment_payload).encode()).decode()

        resp = requests.post(
            f"{ROBOT_A_URL}/release-object",
            json={"objectId": offered_object_id},
            headers={"X-PAYMENT": payment_header},
        )

    if not resp.ok:
        speak("Payment failed")
        print(resp.status_code, resp.text)
        return False

    print("Payment settled:", resp.json())
    speak("Payment successful")
    return True

home = [0, 0, 0, 0, 0, 45]
left_air = [-90, 0, 0, 0, 0, 45]
left_pos = [-90, -36, -120, 74, 0, -45]
mid_air = [0, -36, -30, 74, 0, -45]
right_air = [135, -36, -30, 74, 0, -45]
right_pos = [90, -40, -120, 74, 0, 0]

left_grab = [-90, -28, -60, 95, 0, 135]
left_take = [-90, 0, -60, 135, 0, 135]

speed = 50
mc.set_gripper_state(0, 70)
time.sleep(1)
mc.send_angles(home, speed)
time.sleep(2)
mc.send_angles(left_air, speed)

payment_ok = verify_and_pay(camera_index=0)

if not payment_ok:
    print("Aborting — object not authorized or payment failed.")
else:
    mc.send_angles(left_grab, speed)
    time.sleep(2)
    mc.set_gripper_state(1, 70)
    time.sleep(20)
    # confirm here
    mc.send_angles(left_take, speed)
    time.sleep(2)
    mc.send_angles(mid_air, speed)
    time.sleep(2)
    mc.send_angles(right_pos, speed)
