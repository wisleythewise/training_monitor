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
    
    # Check available attributes
    attrs = [attr for attr in dir(run) if not attr.startswith('_') and not callable(getattr(run, attr))]
    print(f"Non-callable attributes: {attrs}")
    
    # Check if there are any system-related attributes
    system_attrs = [attr for attr in attrs if 'system' in attr.lower()]
    print(f"System attributes: {system_attrs}")
    
except Exception as e:
    print(f"Error: {e}")