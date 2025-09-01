#!/usr/bin/env python3
"""Test script for get_hf_models.py and get_hf_datasets.py"""

import subprocess
import sys
import json
import os

def run_script(script_path):
    """Run a script and return stdout, stderr, and return code"""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Script timed out", 1
    except Exception as e:
        return "", f"Error running script: {e}", 1

def test_script(script_name, script_path):
    """Test a single script"""
    print(f"\n=== Testing {script_name} ===")
    
    if not os.path.exists(script_path):
        print(f"❌ FAIL: Script not found at {script_path}")
        return False
    
    stdout, stderr, returncode = run_script(script_path)
    
    print(f"Return code: {returncode}")
    
    if stderr:
        print(f"Stderr: {stderr}")
    
    # Try to parse stdout as JSON
    try:
        data = json.loads(stdout)
        print(f"✅ SUCCESS: Valid JSON output with {len(data)} items")
        
        # Show sample data if available
        if data:
            print(f"Sample item: {data[0]}")
        else:
            print("No cached items found (empty list)")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: Invalid JSON output")
        print(f"JSON Error: {e}")
        print(f"Raw output: {stdout}")
        return False

def main():
    """Run tests for both scripts"""
    print("Testing Hugging Face cache scripts...")
    
    # Test both scripts
    scripts_dir = "scripts"
    models_script = os.path.join(scripts_dir, "get_hf_models.py")
    datasets_script = os.path.join(scripts_dir, "get_hf_datasets.py")
    
    models_ok = test_script("get_hf_models.py", models_script)
    datasets_ok = test_script("get_hf_datasets.py", datasets_script)
    
    print("\n=== Test Summary ===")
    print(f"Models script: {'✅ PASS' if models_ok else '❌ FAIL'}")
    print(f"Datasets script: {'✅ PASS' if datasets_ok else '❌ FAIL'}")
    
    if models_ok and datasets_ok:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())