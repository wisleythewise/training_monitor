import json
try:
    from huggingface_hub import scan_cache_dir
    cache_info = scan_cache_dir()
    datasets = []
    for repo in cache_info.repos:
        if repo.repo_type == "dataset":
            datasets.append({
                "name": repo.repo_id,
                "size": str(repo.size_on_disk),
                "lastModified": str(repo.last_modified)
            })
    print(json.dumps(datasets))
except ImportError:
    print("[]")
except Exception:
    print("[]")