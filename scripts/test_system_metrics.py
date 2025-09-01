import os
import wandb

try:
    api_key = os.environ.get("WANDB_API_KEY")
    os.environ["WANDB_API_KEY"] = api_key
    api = wandb.Api()
    
    # Get first running run to test system metrics
    runs = list(api.runs("JaspervanLeuven/lerobot"))
    running_runs = [r for r in runs if r.state == "running"]
    
    if running_runs:
        run = running_runs[0]
        print(f"Testing run: {run.id} - {run.name}")
        
        # Try to get system metrics using history with stream="events"
        try:
            print("Trying to get system events...")
            # Get just the latest few system events
            system_events = run.history(stream="events", samples=1)
            print(f"System events type: {type(system_events)}")
            
            if hasattr(system_events, 'columns'):
                print(f"Available columns: {list(system_events.columns)}")
                # Look for GPU utilization columns
                gpu_cols = [col for col in system_events.columns if 'gpu' in col.lower() and 'util' in col.lower()]
                print(f"GPU utilization columns: {gpu_cols}")
                
                if not system_events.empty:
                    latest_row = system_events.iloc[-1]
                    print(f"Latest system metrics:")
                    for col in gpu_cols:
                        if col in latest_row and pd.notna(latest_row[col]):
                            print(f"  {col}: {latest_row[col]}")
            
        except Exception as e:
            print(f"System events error: {e}")
        
        # Try alternative approach - scan_history for system metrics
        try:
            print("\nTrying scan_history approach...")
            # Look for specific GPU utilization keys
            gpu_util_keys = ['system.gpu.0.gpu', 'gpu.0.gpu', 'system.gpu.0.utilization']
            
            for key in gpu_util_keys:
                try:
                    sample = list(run.scan_history(keys=[key], page_size=1))
                    if sample and key in sample[0] and sample[0][key] is not None:
                        print(f"Found {key}: {sample[0][key]}")
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"scan_history error: {e}")
            
    else:
        print("No running runs found to test")
        
except Exception as e:
    print(f"Error: {e}")