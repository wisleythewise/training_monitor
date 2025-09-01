#!/usr/bin/env python3
"""Debug HF token and user access"""

import json
import sys
import os

# Load .env file manually from same directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"Looking for .env at: {env_path}")

if os.path.exists(env_path):
    print("✅ .env file found")
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                if 'TOKEN' in key:
                    print(f"✅ Found token: {key}={value[:10]}...")
else:
    print("❌ .env file not found")

try:
    from huggingface_hub import list_models, list_datasets, HfApi
    
    # Get HF token from environment
    token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
    print(f"Token loaded: {'Yes' if token else 'No'}")
    
    if token:
        api = HfApi(token=token)
        try:
            user_info = api.whoami()
            username = user_info['name']
            print(f"✅ Logged in as: {username}")
            
            # Try to get user's models
            try:
                models_iter = list_models(author=username, token=token)
                user_models = list(models_iter)
                print(f"✅ Found {len(user_models)} models for {username}")
                if user_models:
                    for model in user_models[:3]:  # Show first 3
                        print(f"  - {model.modelId}")
                else:
                    print("  (No models found)")
            except Exception as e:
                print(f"❌ Error fetching user models: {e}")
                
            # Try to get user's datasets  
            try:
                datasets_iter = list_datasets(author=username, token=token)
                user_datasets = list(datasets_iter)
                print(f"✅ Found {len(user_datasets)} datasets for {username}")
                if user_datasets:
                    for dataset in user_datasets[:3]:  # Show first 3
                        print(f"  - {dataset.id}")
                else:
                    print("  (No datasets found)")
            except Exception as e:
                print(f"❌ Error fetching user datasets: {e}")
                
        except Exception as e:
            print(f"❌ Error with token: {e}")
    else:
        print("❌ No token found")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ General error: {e}")