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
    from huggingface_hub import list_models, HfApi
    
    # Get HF token from environment or use default (public access)
    token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
    api = HfApi(token=token)
    
    # Get current user's models if token is available
    if token:
        try:
            user_info = api.whoami()
            username = user_info['name']
            models_iter = list_models(author=username, token=token)
        except Exception:
            # Fallback to listing popular models if user fetch fails
            models_iter = list_models(limit=50, sort="downloads", direction=-1)
    else:
        # No token - list popular public models
        models_iter = list_models(limit=50, sort="downloads", direction=-1)
    
    models = []
    for model in models_iter:
        models.append({
            "name": model.modelId,
            "downloads": getattr(model, 'downloads', 0),
            "lastModified": model.lastModified.isoformat() if model.lastModified else None,
            "tags": getattr(model, 'tags', [])
        })
    
    print(json.dumps(models))
except ImportError as e:
    print("[]", file=sys.stderr)
    print("ImportError:", e, file=sys.stderr)
    print("[]")
except Exception as e:
    print("[]", file=sys.stderr)
    print("Exception:", e, file=sys.stderr)
    print("[]")
