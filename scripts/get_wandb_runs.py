import os
import sys
import json
try:
    import wandb
    
    # Get API key from environment
    api_key = os.environ.get("WANDB_API_KEY")
    project_filter = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if not api_key:
        print("[]")
        sys.exit(0)
        
    os.environ["WANDB_API_KEY"] = api_key
    api = wandb.Api()
    runs = []
    
    if project_filter:
        # Get runs from specific project
        try:
            print(f"Filtering by project: {project_filter}", file=sys.stderr)
            project_runs = list(api.runs(project_filter))
            print(f"Found {len(project_runs)} runs for project {project_filter}", file=sys.stderr)
            for i, run in enumerate(project_runs):
                try:
                    print(f"Processing run {run.id}: summary keys: {list(run.summary.keys()) if run.summary else []}", file=sys.stderr)
                    print(f"Config keys: {list(run.config.keys()) if run.config else []}", file=sys.stderr)
                    
                    # Look for hardware info in summary and config
                    if run.summary:
                        hw_keys = [k for k in run.summary.keys() if any(hw in k.lower() for hw in ['gpu', 'cpu', 'cuda', 'device', 'hardware', 'memory', 'ram'])]
                        if hw_keys:
                            print(f"Hardware summary keys: {hw_keys}", file=sys.stderr)
                    
                    if run.config:
                        hw_config_keys = [k for k in run.config.keys() if any(hw in k.lower() for hw in ['gpu', 'cpu', 'cuda', 'device', 'hardware', 'memory', 'ram'])]
                        if hw_config_keys:
                            print(f"Hardware config keys: {hw_config_keys}", file=sys.stderr)
                    
                    # Safely convert summary to dict with only JSON-serializable values
                    metrics = {}
                    if run.summary:
                        for key, value in run.summary.items():
                            try:
                                # Test if value is JSON serializable
                                json.dumps(value)
                                metrics[key] = value
                            except (TypeError, ValueError):
                                # Convert non-serializable values to string
                                metrics[key] = str(value)
                    
                    # Get total steps from various possible config keys
                    total_steps = 0
                    if run.config:
                        total_steps = (run.config.get("steps") or 
                                     run.config.get("total_steps") or 
                                     run.config.get("num_train_epochs") or 
                                     run.config.get("training_steps") or 0)
                    
                    # Extract GPU information from metadata (fast and reliable)
                    gpu_info = "N/A"
                    gpu_utilization = "N/A"
                    try:
                        # Check metadata for GPU info - WandB stores hardware info here
                        if hasattr(run, 'metadata') and run.metadata:
                            # Check for direct GPU field
                            if 'gpu' in run.metadata and run.metadata['gpu']:
                                gpu_info = str(run.metadata['gpu'])
                            # Check for GPU nvidia array (more detailed info)
                            elif 'gpu_nvidia' in run.metadata and run.metadata['gpu_nvidia']:
                                gpu_data = run.metadata['gpu_nvidia'][0]  # Get first GPU
                                gpu_info = str(gpu_data.get('name', 'Unknown GPU'))
                        
                        # Try to get GPU utilization from summary (if available)
                        if run.summary:
                            # Look for GPU utilization metrics in summary
                            gpu_util_keys = ['gpu.0.gpu', 'system.gpu.0.gpu', 'gpu_utilization', 'gpu_usage', 'system.gpu.0.utilization']
                            for key in gpu_util_keys:
                                if key in run.summary and run.summary[key] is not None:
                                    util_val = run.summary[key]
                                    # Convert to percentage if needed
                                    if isinstance(util_val, (int, float)):
                                        if util_val <= 1.0:  # Assume decimal format
                                            gpu_utilization = f"{util_val * 100:.1f}%"
                                        else:  # Assume percentage format
                                            gpu_utilization = f"{util_val:.1f}%"
                                    break
                        
                        # For now, skip history lookup to keep API fast
                        # GPU utilization will show "N/A" until WandB logs it in summary
                        # Future: Could implement background job to get GPU utilization
                        
                        # Clean up GPU info (remove NVIDIA prefix to save space)
                        if gpu_info != "N/A":
                            gpu_info = gpu_info.replace("NVIDIA ", "").strip()
                            # Limit length for display
                            if len(gpu_info) > 25:
                                gpu_info = gpu_info[:22] + "..."
                                
                    except Exception:
                        gpu_info = "N/A"
                        gpu_utilization = "N/A"
                    
                    # Calculate ETA using Wandb's runtime value - only for running jobs
                    eta = run.state.capitalize() if run.state else "N/A"
                    
                    if run.state == "running":
                        current_progress = run.summary.get("_step", 0) if run.summary else 0
                        
                        try:
                            if total_steps > 0 and current_progress > 0 and current_progress < total_steps:
                                # Get runtime from summary (in seconds)
                                runtime_seconds = run.summary.get("_runtime", 0) if run.summary else 0
                                
                                if runtime_seconds > 0:
                                    progress_ratio = current_progress / total_steps
                                    estimated_total_time = runtime_seconds / progress_ratio
                                    remaining_seconds = estimated_total_time - runtime_seconds
                                    
                                    if remaining_seconds > 0:
                                        # Format ETA
                                        hours = int(remaining_seconds // 3600)
                                        minutes = int((remaining_seconds % 3600) // 60)
                                        if hours > 0:
                                            eta = f"{hours}h {minutes}m"
                                        else:
                                            eta = f"{minutes}m"
                        except Exception:
                            eta = "Running"
                    
                    run_data = {
                        "id": run.id,
                        "name": run.name,
                        "state": run.state,
                        "progress": run.summary.get("_step", 0) if run.summary else 0,
                        "totalSteps": total_steps,
                        "createdAt": str(run.created_at),
                        "eta": eta,
                        "entity": run.entity,
                        "project": run.project,
                        "gpu": gpu_info,
                        "gpuUtilization": gpu_utilization,
                        "metrics": metrics
                    }
                    runs.append(run_data)
                    print(f"Successfully processed run {i}", file=sys.stderr)
                except Exception as e:
                    print(f"Error processing run {i}: {type(e).__name__}: {e}", file=sys.stderr)
                    continue
            
            print(f"Final runs count: {len(runs)}", file=sys.stderr)
        except Exception as e:
            print(f"Error filtering project {project_filter}: {e}", file=sys.stderr)
            pass
    else:
        # Get runs from all projects
        try:
            for project in api.projects():
                project_path = f"{project.entity}/{project.name}"
                for run in api.runs(project_path):
                    # Safely convert summary to dict with only JSON-serializable values
                    metrics = {}
                    if run.summary:
                        for key, value in run.summary.items():
                            try:
                                # Test if value is JSON serializable
                                json.dumps(value)
                                metrics[key] = value
                            except (TypeError, ValueError):
                                # Convert non-serializable values to string
                                metrics[key] = str(value)
                    
                    # Get total steps from various possible config keys
                    total_steps = 0
                    if run.config:
                        total_steps = (run.config.get("steps") or 
                                     run.config.get("total_steps") or 
                                     run.config.get("num_train_epochs") or 
                                     run.config.get("training_steps") or 0)
                    
                    # Extract GPU information from metadata (fast and reliable)
                    gpu_info = "N/A"
                    gpu_utilization = "N/A"
                    try:
                        # Check metadata for GPU info - WandB stores hardware info here
                        if hasattr(run, 'metadata') and run.metadata:
                            # Check for direct GPU field
                            if 'gpu' in run.metadata and run.metadata['gpu']:
                                gpu_info = str(run.metadata['gpu'])
                            # Check for GPU nvidia array (more detailed info)
                            elif 'gpu_nvidia' in run.metadata and run.metadata['gpu_nvidia']:
                                gpu_data = run.metadata['gpu_nvidia'][0]  # Get first GPU
                                gpu_info = str(gpu_data.get('name', 'Unknown GPU'))
                        
                        # Try to get GPU utilization from summary (if available)
                        if run.summary:
                            # Look for GPU utilization metrics in summary
                            gpu_util_keys = ['gpu.0.gpu', 'system.gpu.0.gpu', 'gpu_utilization', 'gpu_usage', 'system.gpu.0.utilization']
                            for key in gpu_util_keys:
                                if key in run.summary and run.summary[key] is not None:
                                    util_val = run.summary[key]
                                    # Convert to percentage if needed
                                    if isinstance(util_val, (int, float)):
                                        if util_val <= 1.0:  # Assume decimal format
                                            gpu_utilization = f"{util_val * 100:.1f}%"
                                        else:  # Assume percentage format
                                            gpu_utilization = f"{util_val:.1f}%"
                                    break
                        
                        # For now, skip history lookup to keep API fast
                        # GPU utilization will show "N/A" until WandB logs it in summary
                        # Future: Could implement background job to get GPU utilization
                        
                        # Clean up GPU info (remove NVIDIA prefix to save space)
                        if gpu_info != "N/A":
                            gpu_info = gpu_info.replace("NVIDIA ", "").strip()
                            # Limit length for display
                            if len(gpu_info) > 25:
                                gpu_info = gpu_info[:22] + "..."
                                
                    except Exception:
                        gpu_info = "N/A"
                        gpu_utilization = "N/A"
                    
                    # Calculate ETA using Wandb's runtime value - only for running jobs
                    eta = run.state.capitalize() if run.state else "N/A"
                    
                    if run.state == "running":
                        current_progress = run.summary.get("_step", 0) if run.summary else 0
                        
                        try:
                            if total_steps > 0 and current_progress > 0 and current_progress < total_steps:
                                # Get runtime from summary (in seconds)
                                runtime_seconds = run.summary.get("_runtime", 0) if run.summary else 0
                                
                                if runtime_seconds > 0:
                                    progress_ratio = current_progress / total_steps
                                    estimated_total_time = runtime_seconds / progress_ratio
                                    remaining_seconds = estimated_total_time - runtime_seconds
                                    
                                    if remaining_seconds > 0:
                                        # Format ETA
                                        hours = int(remaining_seconds // 3600)
                                        minutes = int((remaining_seconds % 3600) // 60)
                                        if hours > 0:
                                            eta = f"{hours}h {minutes}m"
                                        else:
                                            eta = f"{minutes}m"
                        except Exception:
                            eta = "Running"
                    
                    runs.append({
                        "id": run.id,
                        "name": run.name,
                        "state": run.state,
                        "progress": run.summary.get("_step", 0) if run.summary else 0,
                        "totalSteps": total_steps,
                        "createdAt": str(run.created_at),
                        "eta": eta,
                        "entity": run.entity,
                        "project": run.project,
                        "gpu": gpu_info,
                        "gpuUtilization": gpu_utilization,
                        "metrics": metrics
                    })
        except Exception:
            pass
    
    # Sort runs by creation date (newest first)
    runs.sort(key=lambda x: x["createdAt"], reverse=True)
    
    # Always output the runs list, even if empty
    print(f"About to output {len(runs)} runs", file=sys.stderr)
    print(json.dumps(runs))
    
except ImportError as e:
    print(f"ImportError: {e}", file=sys.stderr)
    print("[]")
except Exception as e:
    print(f"Global exception: {type(e).__name__}: {e}", file=sys.stderr)
    print("[]")