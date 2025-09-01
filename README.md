# Training Monitor

A simple web application to monitor Wandb training runs and browse HuggingFace models/datasets.

## Features

- Real-time monitoring of Wandb training runs with progress tracking
- Display of total steps/epochs and current progress
- Browse locally cached HuggingFace models and datasets
- Filter models and datasets by name
- Auto-refresh every 30 seconds
- Dark theme optimized for display monitors

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Wandb CLI installed and configured
- HuggingFace CLI installed

## Installation on Raspberry Pi

### 1. Install Node.js on Raspberry Pi

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Node.js (v18)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

### 2. Install Python and CLI Tools

```bash
# Install Python and pip
sudo apt install -y python3 python3-pip

# Install Wandb CLI
pip3 install wandb
wandb login  # Follow prompts to enter your API key

# Install HuggingFace CLI
pip3 install huggingface-hub
huggingface-cli login  # Optional: for private models/datasets
```

### 3. Clone and Setup the Application

```bash
# Clone the repository (or copy the training-monitor folder)
cd ~
# If using git:
# git clone <your-repo-url> training-monitor
# Or copy the folder from your laptop via SCP:
# scp -r /path/to/training-monitor pi@raspberry-pi-ip:~/

cd training-monitor

# Install dependencies
npm install-all

# Configure environment
nano .env
# Add your WANDB_API_KEY if needed
```

### 4. Run the Application

```bash
# Start the server
npm start

# Or for development with auto-reload
npm run dev
```

The application will be available at `http://raspberry-pi-ip:5000`

### 5. Auto-start on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/training-monitor.service
```

Add the following content:

```ini
[Unit]
Description=Training Monitor Web App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/training-monitor
ExecStart=/usr/bin/node /home/pi/training-monitor/backend/server.js
Restart=on-failure
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable training-monitor.service
sudo systemctl start training-monitor.service
sudo systemctl status training-monitor.service
```

## Building for Production

If you want to build the React frontend for better performance:

```bash
cd training-monitor
npm run build

# Modify the backend to serve static files
# Add to backend/server.js:
# app.use(express.static(path.join(__dirname, '../frontend/build')));
```

## Display Configuration for Raspberry Pi

To display on a monitor in kiosk mode:

### 1. Install Chromium

```bash
sudo apt install -y chromium-browser
```

### 2. Configure Auto-login and Kiosk Mode

```bash
# Install unclutter to hide mouse cursor
sudo apt install -y unclutter

# Edit autostart
nano ~/.config/lxsession/LXDE-pi/autostart
```

Add these lines:

```
@xset s off
@xset -dpms
@xset s noblank
@chromium-browser --kiosk --incognito --disable-infobars http://localhost:5000
@unclutter -idle 0
```

### 3. Prevent Screen Sleep

```bash
# Edit lightdm config
sudo nano /etc/lightdm/lightdm.conf
```

Add under `[Seat:*]`:

```
xserver-command=X -s 0 -dpms
```

## Troubleshooting

### Wandb CLI Issues

If wandb runs command fails:
1. Ensure you're logged in: `wandb login`
2. Check you have active runs: `wandb runs`
3. Verify API key in `.env` file

### HuggingFace Models Not Showing

Models/datasets only appear if they're cached locally:
```bash
# Check cache location
ls ~/.cache/huggingface/hub/

# Download a model to cache it
huggingface-cli download <model-name>
```

### Port Already in Use

Change the port in `.env` file:
```
PORT=3000
```

### Low Memory on Raspberry Pi

For Raspberry Pi with limited RAM:
1. Build the frontend on your laptop first
2. Copy only the built files to Pi
3. Run only the backend server

## Development on Laptop

```bash
# Install all dependencies
npm run install-all

# Start development server
npm run dev

# Frontend will run on http://localhost:3000
# Backend will run on http://localhost:5000
```

## API Endpoints

- `GET /api/wandb/runs` - Get all Wandb training runs
- `GET /api/huggingface/models` - Get cached HuggingFace models
- `GET /api/huggingface/datasets` - Get cached HuggingFace datasets
- `GET /api/health` - Health check endpoint

## License

MIT# training_monitor
