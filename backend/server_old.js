const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

async function getWandbRuns(projectFilter = null) {
  try {
    const wandbApiKey = process.env.WANDB_API_KEY;
    const scriptPath = 'scripts/get_wandb_runs.py';
    const projectArg = projectFilter ? `"${projectFilter}"` : '';
    
    const { stdout } = await execPromise(`WANDB_API_KEY="${wandbApiKey}" python3 ${scriptPath} ${projectArg}`);
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error fetching Wandb runs:', error.message);
    
    // Fallback to using the Wandb HTTP API directly
    try {
      const axios = require('axios');
      const apiKey = process.env.WANDB_API_KEY;
      
      // This is a simplified version - you might need to specify entity/project
      const response = await axios.get('https://api.wandb.ai/graphql', {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        data: {
          query: `
            query Runs {
              viewer {
                runs(first: 50) {
                  edges {
                    node {
                      id
                      name
                      state
                      createdAt
                      project {
                        name
                        entity {
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
          `
        }
      });
      
      if (response.data?.data?.viewer?.runs?.edges) {
        return response.data.data.viewer.runs.edges.map(edge => ({
          id: edge.node.id,
          name: edge.node.name,
          state: edge.node.state,
          progress: 0,
          totalSteps: 0,
          createdAt: edge.node.createdAt,
          entity: edge.node.project?.entity?.name || '',
          project: edge.node.project?.name || '',
          metrics: {}
        }));
      }
    } catch (apiError) {
      console.error('Error with Wandb API:', apiError.message);
    }
    
    return [];
  }
}

async function getHuggingFaceModels() {
  try {
    // Try using huggingface_hub Python module first
    const pythonScript = `import json
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
except ImportError:
    print("[]")
except Exception:
    print("[]")`;
    
    const { stdout } = await execPromise(`python3 -c "${pythonScript}"`);
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error with Python approach:', error.message);
    
    // Fallback to direct directory listing
    try {
      const { stdout } = await execPromise('ls ~/.cache/huggingface/hub 2>/dev/null | grep "models--" || true');
      const models = stdout.split('\n')
        .filter(line => line.includes('models--'))
        .map(line => {
          const name = line.replace('models--', '').replace(/--/g, '/');
          return {
            name: name,
            size: 'Unknown',
            lastModified: new Date().toISOString()
          };
        });
      
      // If no models-- directories, try model-- (older format)
      if (models.length === 0) {
        const { stdout: oldFormat } = await execPromise('ls ~/.cache/huggingface/hub 2>/dev/null | grep "model--" || true');
        return oldFormat.split('\n')
          .filter(line => line.includes('model--'))
          .map(line => ({
            name: line.replace('model--', '').replace(/--/g, '/'),
            size: 'Unknown',
            lastModified: new Date().toISOString()
          }));
      }
      
      return models;
    } catch (fallbackError) {
      console.error('Fallback error:', fallbackError);
      return [];
    }
  }
}

async function getHuggingFaceDatasets() {
  try {
    // Try using huggingface_hub Python module first
    const pythonScript = `import json
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
    print("[]")`;
    
    const { stdout } = await execPromise(`python3 -c "${pythonScript}"`);
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error with Python approach:', error.message);
    
    // Fallback to direct directory listing
    try {
      const { stdout } = await execPromise('ls ~/.cache/huggingface/hub 2>/dev/null | grep "datasets--" || true');
      const datasets = stdout.split('\n')
        .filter(line => line.includes('datasets--'))
        .map(line => ({
          name: line.replace('datasets--', '').replace(/--/g, '/'),
          size: 'Unknown',
          lastModified: new Date().toISOString()
        }));
      
      // If no datasets-- directories, try dataset-- (older format)
      if (datasets.length === 0) {
        const { stdout: oldFormat } = await execPromise('ls ~/.cache/huggingface/hub 2>/dev/null | grep "dataset--" || true');
        return oldFormat.split('\n')
          .filter(line => line.includes('dataset--'))
          .map(line => ({
            name: line.replace('dataset--', '').replace(/--/g, '/'),
            size: 'Unknown',
            lastModified: new Date().toISOString()
          }));
      }
      
      return datasets;
    } catch (fallbackError) {
      console.error('Fallback error:', fallbackError);
      return [];
    }
  }
}

async function getWandbProjects() {
  try {
    const wandbApiKey = process.env.WANDB_API_KEY;
    const scriptPath = 'scripts/get_wandb_projects.py';
    
    const { stdout } = await execPromise(`WANDB_API_KEY="${wandbApiKey}" python3 ${scriptPath}`);
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error fetching Wandb projects:', error.message);
    return [];
  }
}

app.get('/api/wandb/runs', async (req, res) => {
  try {
    const projectFilter = req.query.project;
    const runs = await getWandbRuns(projectFilter);
    res.json(runs);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch Wandb runs' });
  }
});

app.get('/api/wandb/projects', async (req, res) => {
  try {
    const projects = await getWandbProjects();
    res.json(projects);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch Wandb projects' });
  }
});

app.get('/api/huggingface/models', async (req, res) => {
  try {
    const models = await getHuggingFaceModels();
    res.json(models);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch HuggingFace models' });
  }
});

app.get('/api/huggingface/datasets', async (req, res) => {
  try {
    const datasets = await getHuggingFaceDatasets();
    res.json(datasets);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch HuggingFace datasets' });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'OK' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});