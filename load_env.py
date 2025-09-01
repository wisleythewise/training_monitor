#!/usr/bin/env python3
"""Load environment variables from .env file"""

import os

def load_env():
    """Load .env file manually"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

if __name__ == "__main__":
    load_env()
    print(f"HUGGINGFACE_TOKEN loaded: {'Yes' if os.getenv('HUGGINGFACE_TOKEN') else 'No'}")