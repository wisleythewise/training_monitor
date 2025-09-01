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
        
        # List all datasets from the user's account
        datasets = api.list_datasets(author=username)
        
        dataset_list = []
        for dataset in datasets:
            dataset_list.append({
                "name": dataset.id,
                "private": dataset.private,
                "lastModified": str(dataset.lastModified) if dataset.lastModified else "",
                "downloads": dataset.downloads if hasattr(dataset, 'downloads') else 0,
                "likes": dataset.likes if hasattr(dataset, 'likes') else 0,
                "tags": dataset.tags if hasattr(dataset, 'tags') else []
            })
        
        print(json.dumps(dataset_list))
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