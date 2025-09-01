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
        
        # Check summary for GPU utilization
        if run.summary:
            gpu_summary_keys = [k for k in run.summary.keys() if 'gpu' in k.lower()]
            print(f"GPU keys in summary: {gpu_summary_keys}")
            for key in gpu_summary_keys:
                print(f"  {key}: {run.summary[key]}")
        
        # Try to get latest GPU utilization from history
        try:
            # Get latest entry with GPU metrics
            history_sample = list(run.scan_history(page_size=1))
            if history_sample:
                entry = history_sample[0]
                gpu_keys = [k for k in entry.keys() if 'gpu' in k.lower()]
                print(f"GPU keys in latest history: {gpu_keys}")
                for key in gpu_keys:
                    if entry[key] is not None:
                        print(f"  {key}: {entry[key]}")
        except Exception as e:
            print(f"History error: {e}")
            
    else:
        print("No running runs found")
        
except Exception as e:
    print(f"Error: {e}")