import os
import wandb

try:
    api_key = os.environ.get("WANDB_API_KEY")
    os.environ["WANDB_API_KEY"] = api_key
    api = wandb.Api()
    
    # Get just the first run
    runs = list(api.runs("JaspervanLeuven/lerobot"))
    run = runs[0]
    print(f"Run: {run.id}")
    
    # Check metadata
    if hasattr(run, 'metadata') and run.metadata:
        print(f"Metadata: {run.metadata}")
        # Look for GPU info in metadata
        for key, value in run.metadata.items():
            if 'gpu' in key.lower() or 'cuda' in key.lower():
                print(f"GPU-related metadata - {key}: {value}")
    
    # Try using the internal client to get more detailed info
    if hasattr(run, 'client'):
        try:
            # Get run data from client
            run_data = run.client.run(run.entity, run.project, run.id)
            print(f"Client run data keys: {list(run_data.keys()) if isinstance(run_data, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"Client error: {e}")
    
    # Try to access system metrics through scan_history with specific stream
    try:
        # Try to get just system events
        events = list(run.scan_history(stream="events", page_size=1))
        if events:
            event = events[0]
            print(f"Event keys: {list(event.keys())}")
            
            # Look for GPU keys
            gpu_keys = [k for k in event.keys() if 'gpu' in k.lower()]
            if gpu_keys:
                print(f"GPU keys in events: {gpu_keys}")
                for key in gpu_keys:
                    print(f"{key}: {event[key]}")
    except Exception as e:
        print(f"Events error: {e}")
        
except Exception as e:
    print(f"Error: {e}")