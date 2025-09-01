import os
import wandb

try:
    api_key = os.environ.get("WANDB_API_KEY")
    os.environ["WANDB_API_KEY"] = api_key
    api = wandb.Api()
    
    # Get first running run
    runs = list(api.runs("JaspervanLeuven/lerobot"))
    running_runs = [r for r in runs if r.state == "running"]
    
    if running_runs:
        run = running_runs[0]
        print(f"Testing run: {run.id} - {run.name}")
        
        # Test scan_history for GPU utilization
        try:
            print("Getting recent history entries...")
            recent_entries = list(run.scan_history(page_size=3))
            print(f"Got {len(recent_entries)} entries")
            
            if recent_entries:
                entry = recent_entries[0]  # Latest entry
                print(f"Latest entry keys: {list(entry.keys())}")
                
                # Look for GPU keys
                gpu_keys = [k for k in entry.keys() if 'gpu' in k.lower()]
                print(f"GPU-related keys: {gpu_keys}")
                
                # Check specific utilization keys
                for key in ['system.gpu.0.gpu', 'gpu.0.gpu', 'system.gpu.0.utilization']:
                    if key in entry:
                        print(f"{key}: {entry[key]}")
                
        except Exception as e:
            print(f"scan_history error: {e}")
            
    else:
        print("No running runs found")
        
except Exception as e:
    print(f"Error: {e}")