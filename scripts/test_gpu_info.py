import os
import wandb

try:
    api_key = os.environ.get("WANDB_API_KEY")
    if not api_key:
        print("No API key")
        exit(1)
    
    os.environ["WANDB_API_KEY"] = api_key
    api = wandb.Api()
    
    # Get just the first run
    runs = list(api.runs("JaspervanLeuven/lerobot"))
    if not runs:
        print("No runs found")
        exit(1)
    
    run = runs[0]
    print(f"Testing run: {run.id} - {run.name}")
    
    # Check what attributes are available on the run object
    print(f"Run attributes: {[attr for attr in dir(run) if not attr.startswith('_')]}")
    
    # Check if system_metrics exists
    if hasattr(run, 'system_metrics'):
        print(f"System metrics available: {run.system_metrics}")
    else:
        print("No system_metrics attribute")
    
    # Try config
    print(f"Config keys: {list(run.config.keys()) if run.config else 'None'}")
    
    # Try summary
    print(f"Summary keys: {list(run.summary.keys()) if run.summary else 'None'}")
    
    # Try to get just one system metric sample efficiently
    try:
        sample = run.scan_history(page_size=1)
        first_entry = next(sample, {})
        print(f"Sample history keys: {list(first_entry.keys())}")
        
        # Look for GPU related keys
        gpu_keys = [k for k in first_entry.keys() if 'gpu' in k.lower()]
        print(f"GPU-related keys in history: {gpu_keys}")
        
        # Check specific system GPU keys
        for key in ["system.gpu.0.name", "system.gpu.0.gpu", "gpu.0.name"]:
            if key in first_entry:
                print(f"{key}: {first_entry[key]}")
                
    except Exception as e:
        print(f"scan_history error: {e}")

except Exception as e:
    print(f"Error: {e}")