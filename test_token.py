#!/usr/bin/env python3
"""Test HF token and check user info"""

import os
from huggingface_hub import HfApi

# Load token from .env
token = os.getenv('HUGGINGFACE_TOKEN')
print(f"Token found: {'Yes' if token else 'No'}")

if token:
    try:
        api = HfApi(token=token)
        user_info = api.whoami()
        print(f"Username: {user_info['name']}")
        print(f"Full name: {user_info.get('fullname', 'N/A')}")
        print(f"User type: {user_info.get('type', 'N/A')}")
    except Exception as e:
        print(f"Error getting user info: {e}")
        print("Token may be invalid or expired")
else:
    print("No token found")