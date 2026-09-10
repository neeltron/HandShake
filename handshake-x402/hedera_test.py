# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 15:34:34 2026

@author: neeltron
"""

import requests

FACILITATOR_URL = "https://api.testnet.blocky402.com"

def get_facilitator_fee_payer() -> str:
    resp = requests.get(f"{FACILITATOR_URL}/supported", timeout=10)
    resp.raise_for_status()
    for entry in resp.json().get("kinds", []):
        if entry.get("network") == "hedera:testnet":
            return entry["extra"]["feePayer"]
    raise RuntimeError("Facilitator does not advertise hedera:testnet support")
    
    
if __name__ == "__main__":
    fee_payer = get_facilitator_fee_payer()
    print("Facilitator fee payer:", fee_payer)
    