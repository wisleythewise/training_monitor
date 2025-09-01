const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const util = require('util');
const path = require('path');
const execPromise = util.promisify(exec);
require('dotenv').config();

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
    const pythonPath = '/home/jasper/miniconda3/envs/lerobot/bin/python3';
    
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
    const pythonPath = '/home/jasper/miniconda3/envs/lerobot/bin/python3';
    
    const { stdout } = await execPromise(`WANDB_API_KEY="${wandbApiKey}" ${pythonPath} "${scriptPath}"`, { cwd: workingDir });
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error fetching Wandb projects:', error.message);
    return [];
  }
}

async function getHuggingFaceModels() {
  try {
    const scriptPath = path.join(__dirname, '..', 'scripts', 'get_hf_models.py');
    const workingDir = path.join(__dirname, '..');
    const pythonPath = '/home/jasper/miniconda3/envs/lerobot/bin/python3';
    console.log('Executing:', `${pythonPath} "${scriptPath}"`, 'in', workingDir);
    const { stdout, stderr } = await execPromise(`${pythonPath} "${scriptPath}"`, { cwd: workingDir });
    if (stderr) console.error('HF Models stderr:', stderr);
    console.log('HF Models stdout length:', stdout.length);
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error fetching HuggingFace models:', error.message);
    return [];
  }
}

async function getHuggingFaceDatasets() {
  try {
    const scriptPath = path.join(__dirname, '..', 'scripts', 'get_hf_datasets.py');
    const workingDir = path.join(__dirname, '..');
    const pythonPath = '/home/jasper/miniconda3/envs/lerobot/bin/python3';
    const { stdout } = await execPromise(`${pythonPath} "${scriptPath}"`, { cwd: workingDir });
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error fetching HuggingFace datasets:', error.message);
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