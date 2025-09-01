import os
import json
try:
    import wandb
    
    # Get API key from environment
    api_key = os.environ.get("WANDB_API_KEY")
    
    if not api_key:
        print("[]")
        exit(0)
        
    os.environ["WANDB_API_KEY"] = api_key
    api = wandb.Api()
    projects = []
    
    try:
        for project in api.projects():
            projects.append({
                "name": project.name,
                "entity": project.entity
            })
    except Exception:
        pass
        
    print(json.dumps(projects))
    
except ImportError:
    print("[]")
except Exception:
    print("[]")