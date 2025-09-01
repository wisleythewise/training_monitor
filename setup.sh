#!/bin/bash

echo "Setting up Training Monitor dependencies..."

# Install Python packages
echo "Installing Python packages..."
pip3 install wandb huggingface-hub --user

# Install Node dependencies
echo "Installing Node packages..."
npm run install-all

echo ""
echo "Setup complete! To start the application, run:"
echo "  npm run dev"
echo ""
echo "Note: Make sure you have:"
echo "  1. Node.js installed (v14+)"
echo "  2. Python 3 installed"
echo "  3. Your API keys configured in .env file"