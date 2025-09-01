import json
import sys
try:
    from huggingface_hub import scan_cache_dir
    cache_info = scan_cache_dir()
    models = []
    for repo in cache_info.repos:
        if repo.repo_type == "model":
            models.append({
                "name": repo.repo_id,
                "size": str(repo.size_on_disk),
                "lastModified": str(repo.last_modified)
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