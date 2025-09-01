import json
import sys
import os

# Load .env file manually from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

try:
    from huggingface_hub import list_datasets, HfApi
    
    # Get HF token from environment or use default (public access)
    token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
    api = HfApi(token=token)
    
    # Get current user's datasets if token is available
    if token:
        try:
            user_info = api.whoami()
            username = user_info['name']
            datasets_iter = list_datasets(author=username, token=token)
        except Exception:
            # Fallback to listing popular datasets if user fetch fails
            datasets_iter = list_datasets(limit=50, sort="downloads", direction=-1)
    else:
        # No token - list popular public datasets
        datasets_iter = list_datasets(limit=50, sort="downloads", direction=-1)
    
    datasets = []
    for dataset in datasets_iter:
        datasets.append({
            "name": dataset.id,
            "downloads": getattr(dataset, 'downloads', 0),
            "lastModified": dataset.lastModified.isoformat() if dataset.lastModified else None,
            "tags": getattr(dataset, 'tags', [])
        })
    
    print(json.dumps(datasets))
except ImportError as e:
    print("[]", file=sys.stderr)
    print("ImportError:", e, file=sys.stderr)
    print("[]")
except Exception as e:
    print("[]", file=sys.stderr)
    print("Exception:", e, file=sys.stderr)
    print("[]")
