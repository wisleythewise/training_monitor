const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const util = require('util');
const path = require('path');
const execPromise = util.promisify(exec);
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

// Cache for API responses
const cache = {
  hf_models: { data: null, timestamp: 0 },
  hf_datasets: { data: null, timestamp: 0 }
};
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

async function getWandbRuns(projectFilter = null) {
  try {
    const wandbApiKey = process.env.WANDB_API_KEY;
    const scriptPath = path.join(__dirname, '..', 'scripts', 'get_wandb_runs.py');
    const projectArg = projectFilter ? `"${projectFilter}"` : '';
    const workingDir = path.join(__dirname, '..');
    const pythonPath = path.join(__dirname, '..', 'venv', 'bin', 'python3');
    
    console.log('Wandb: Executing with project filter:', projectFilter);
    const { stdout, stderr } = await execPromise(`WANDB_API_KEY="${wandbApiKey}" ${pythonPath} "${scriptPath}" ${projectArg}`, { cwd: workingDir });
    if (stderr) console.error('Wandb stderr:', stderr);
    console.log('Wandb stdout length:', stdout.length);
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error fetching Wandb runs:', error.message);
    return [];
  }
}

async function getWandbProjects() {
  try {
    const wandbApiKey = process.env.WANDB_API_KEY;
    const scriptPath = path.join(__dirname, '..', 'scripts', 'get_wandb_projects.py');
    const workingDir = path.join(__dirname, '..');
    const pythonPath = path.join(__dirname, '..', 'venv', 'bin', 'python3');
    
    console.log('Fetching Wandb projects with command:', `WANDB_API_KEY="${wandbApiKey}" ${pythonPath} "${scriptPath}"`);
    const { stdout, stderr } = await execPromise(`WANDB_API_KEY="${wandbApiKey}" ${pythonPath} "${scriptPath}"`, { cwd: workingDir });
    if (stderr) console.error('Wandb projects stderr:', stderr);
    console.log('Wandb projects stdout:', stdout);
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error fetching Wandb projects:', error.message);
    console.error('Full error:', error);
    return [];
  }
}

async function getHuggingFaceModels() {
  try {
    // Check cache first
    const now = Date.now();
    if (cache.hf_models.data && (now - cache.hf_models.timestamp) < CACHE_DURATION) {
      console.log('Returning cached HF models');
      return cache.hf_models.data;
    }

    const hfToken = process.env.HUGGINGFACE_TOKEN;
    const scriptPath = path.join(__dirname, '..', 'scripts', 'get_hf_models.py');
    const workingDir = path.join(__dirname, '..');
    const pythonPath = path.join(__dirname, '..', 'venv', 'bin', 'python3');
    console.log('Executing HF models fetch with token');
    const { stdout, stderr } = await execPromise(`HUGGINGFACE_TOKEN="${hfToken}" ${pythonPath} "${scriptPath}"`, { cwd: workingDir });
    if (stderr) console.error('HF Models stderr:', stderr);
    console.log('HF Models stdout length:', stdout.length);
    
    const data = JSON.parse(stdout);
    // Update cache
    cache.hf_models = { data, timestamp: now };
    return data;
  } catch (error) {
    console.error('Error fetching HuggingFace models:', error.message);
    // Return cached data if available, otherwise empty array
    return cache.hf_models.data || [];
  }
}

async function getHuggingFaceDatasets() {
  try {
    // Check cache first
    const now = Date.now();
    if (cache.hf_datasets.data && (now - cache.hf_datasets.timestamp) < CACHE_DURATION) {
      console.log('Returning cached HF datasets');
      return cache.hf_datasets.data;
    }

    const hfToken = process.env.HUGGINGFACE_TOKEN;
    const scriptPath = path.join(__dirname, '..', 'scripts', 'get_hf_datasets.py');
    const workingDir = path.join(__dirname, '..');
    const pythonPath = path.join(__dirname, '..', 'venv', 'bin', 'python3');
    console.log('Executing HF datasets fetch with token');
    const { stdout, stderr } = await execPromise(`HUGGINGFACE_TOKEN="${hfToken}" ${pythonPath} "${scriptPath}"`, { cwd: workingDir });
    if (stderr) console.error('HF Datasets stderr:', stderr);
    console.log('HF Datasets stdout length:', stdout.length);
    
    const data = JSON.parse(stdout);
    // Update cache
    cache.hf_datasets = { data, timestamp: now };
    return data;
  } catch (error) {
    console.error('Error fetching HuggingFace datasets:', error.message);
    // Return cached data if available, otherwise empty array
    return cache.hf_datasets.data || [];
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