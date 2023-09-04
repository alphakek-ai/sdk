import json
from datetime import datetime

import requests
from eth_account import Account
from eth_account.messages import encode_structured_data

EIP712_DOMAIN = {
    "name": "AlphaKEK.AI",
    "version": "1",
    "chainId": 1,  # Use the correct chainId for your target network (e.g., 1 for mainnet, 3 for Ropsten)
    "verifyingContract": "0x0000000000000000000000000000000000000001"  # An example address, update it if needed
}

EIP712_MESSAGE_SCHEMA = {
    "LoginRequest": [
        {"name": "address", "type": "address"},
        {"name": "timestamp", "type": "uint64"}
    ]
}


def generate_signature(account: Account = None):
    if account is None:
        account = Account.from_key('0123456701234567012345670123456701234567012345670123456701234567')
    address = account.address.lower()
    timestamp = int(datetime.timestamp(datetime.now()))
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **EIP712_MESSAGE_SCHEMA
        },
        "domain": EIP712_DOMAIN,
        "primaryType": "LoginRequest",
        "message": {"address": address, "timestamp": timestamp},
    }
    digest = encode_structured_data(typed_data)
    signed = account.sign_message(digest).signature.hex()
    payload = {
        "address": address,
        "signature": signed,
        "timestamp": timestamp
    }
    return payload


if __name__ == '__main__':
    auth_payload = generate_signature()
    print(f'Generated auth payload:\n{json.dumps(auth_payload, indent=2)}')
    r = requests.post('https://api.alphakek.ai/login', json=auth_payload)
    assert r.status_code == 200
    token = r.json()['token']
    print(f'Got token: {token}')
    user_info = requests.get('https://api.alphakek.ai/user-info', headers={'Authorization': f'Bearer {token}'})
    assert user_info.status_code == 200
    print(f'Got user info: {user_info.json()}')
