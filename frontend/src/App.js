import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [wandbRuns, setWandbRuns] = useState([]);
  const [wandbProjects, setWandbProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [models, setModels] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [modelFilter, setModelFilter] = useState('');
  const [datasetFilter, setDatasetFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('models');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const projectParam = selectedProject ? `?project=${encodeURIComponent(selectedProject)}` : '';
      
      const [runsRes, projectsRes, modelsRes, datasetsRes] = await Promise.all([
        fetch(`/api/wandb/runs${projectParam}`).then(r => r.json()).catch(() => []),
        fetch('/api/wandb/projects').then(r => r.json()).catch(() => []),
        fetch('/api/huggingface/models').then(r => r.json()).catch(() => []),
        fetch('/api/huggingface/datasets').then(r => r.json()).catch(() => [])
      ]);

      setWandbRuns(runsRes);
      setWandbProjects(projectsRes);
      setModels(modelsRes);
      setDatasets(datasetsRes);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProject !== undefined) {
      fetchData();
    }
  }, [selectedProject]);

  const filteredModels = models.filter(model => 
    model.name.toLowerCase().includes(modelFilter.toLowerCase())
  );

  const filteredDatasets = datasets.filter(dataset => 
    dataset.name.toLowerCase().includes(datasetFilter.toLowerCase())
  );

  const calculateProgress = (run) => {
    if (!run.totalSteps || run.totalSteps === 0) return 0;
    return Math.min(100, (run.progress / run.totalSteps) * 100);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Training Monitor</h1>
      </header>

      <div className="container">
        <div className="main-panel">
          <div className="runs-header">
            <div className="project-selector">
              <select 
                value={selectedProject} 
                onChange={(e) => setSelectedProject(e.target.value)}
                className="project-dropdown"
              >
                <option value="">All Projects</option>
                {wandbProjects.map((project, idx) => (
                  <option key={idx} value={project.name}>
                    {project.entity}/{project.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {error && <div className="error">{error}</div>}
          
          <div className="runs-container">
            {wandbRuns.length === 0 ? (
              <div className="no-data">No active training runs</div>
            ) : (
              <div className="runs-table">
                <div className="table-header">
                  <div className="col-name">Name</div>
                  <div className="col-status">Status</div>
                  <div className="col-steps">Steps</div>
                  <div className="col-progress">Progress</div>
                  <div className="col-eta">ETA</div>
                  <div className="col-gpu">GPU</div>
                  <div className="col-gpu-util">GPU %</div>
                </div>
                {wandbRuns.map(run => (
                  <div key={run.id} className="table-row">
                    <div className="col-name">
                      <div className="run-name">{run.name || run.id}</div>
                    </div>
                    <div className="col-status">
                      <span className={`status ${run.state}`}>{run.state}</span>
                    </div>
                    <div className="col-steps">
                      <div className="steps-info">
                        <div className="current-steps">{run.progress}</div>
                        <div className="total-steps">/{run.totalSteps || '?'}</div>
                      </div>
                    </div>
                    <div className="col-progress">
                      <div className="progress-container">
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{ width: `${calculateProgress(run)}%` }}
                          />
                        </div>
                        <div className="progress-text">
                          {calculateProgress(run).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    <div className="col-eta">
                      <div className="eta-text">{run.eta || 'N/A'}</div>
                    </div>
                    <div className="col-gpu">
                      <div className="gpu-text">{run.gpu || 'N/A'}</div>
                    </div>
                    <div className="col-gpu-util">
                      <div className="gpu-util-text">{run.gpuUtilization || 'N/A'}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="side-panel">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'models' ? 'active' : ''}`}
              onClick={() => setActiveTab('models')}
            >
              Models
            </button>
            <button 
              className={`tab ${activeTab === 'datasets' ? 'active' : ''}`}
              onClick={() => setActiveTab('datasets')}
            >
              Datasets
            </button>
          </div>

          {activeTab === 'models' && (
            <div className="tab-content">
              <input
                type="text"
                placeholder="Filter models..."
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value)}
                className="filter-input"
              />
              <div className="items-list">
                {filteredModels.length === 0 ? (
                  <div className="no-data">No models found</div>
                ) : (
                  filteredModels.map((model, idx) => (
                    <div key={idx} className="item-card">
                      <div className="item-name">{model.name}</div>
                      <div className="item-meta">Size: {model.size}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'datasets' && (
            <div className="tab-content">
              <input
                type="text"
                placeholder="Filter datasets..."
                value={datasetFilter}
                onChange={(e) => setDatasetFilter(e.target.value)}
                className="filter-input"
              />
              <div className="items-list">
                {filteredDatasets.length === 0 ? (
                  <div className="no-data">No datasets found</div>
                ) : (
                  filteredDatasets.map((dataset, idx) => (
                    <div key={idx} className="item-card">
                      <div className="item-name">{dataset.name}</div>
                      <div className="item-meta">Size: {dataset.size}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;