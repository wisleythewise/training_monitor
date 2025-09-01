import json
import sys
import os

try:
    from huggingface_hub import HfApi
    
    # Get token from environment variable
    token = os.environ.get('HUGGINGFACE_TOKEN', '')
    if token:
        api = HfApi(token=token)
        user_info = api.whoami()
        username = user_info['name']
        
        # List all models from the user's account
        models = api.list_models(author=username)
        
        model_list = []
        for model in models:
            model_list.append({
                "name": model.modelId,
                "private": model.private,
                "lastModified": str(model.lastModified) if model.lastModified else "",
                "downloads": model.downloads if hasattr(model, 'downloads') else 0,
                "likes": model.likes if hasattr(model, 'likes') else 0,
                "tags": model.tags if hasattr(model, 'tags') else []
            })
        
        print(json.dumps(model_list))
    else:
        print("[]", file=sys.stderr)
        print("No HUGGINGFACE_TOKEN found", file=sys.stderr)
        print("[]")
        
except ImportError as e:
    print("[]", file=sys.stderr)
    print("ImportError:", e, file=sys.stderr)
    print("[]")
except Exception as e:
    print("[]", file=sys.stderr)
    print("Exception:", e, file=sys.stderr)
    print("[]")