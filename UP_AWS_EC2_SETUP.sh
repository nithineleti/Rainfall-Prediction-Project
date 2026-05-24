#!/bin/bash
# 🚀 UP Rainfall Prediction Pipeline - AWS EC2 Automated Setup Script

echo "--- 1. Updating System & Installing Dependencies ---"
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv git curl libgomp1

echo "--- 2. Cloning Repository ---"
git clone https://github.com/nithineleti/Rainfall-Prediction-Project.git
cd Rainfall-Prediction-Project

echo "--- 3. Setting up Python Virtual Environment ---"
python3 -m venv .venv
source .venv/bin/activate

echo "--- 4. Installing ML Backend Dependencies ---"
pip install --upgrade pip
pip install -r requirements.txt
pip install uvicorn fastapi httpx python-multipart

echo "--- 5. Installing Node.js & Frontend Dependencies ---"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
cd up-weather-intelligence-system
npm install
cd ..

echo "--- 6. Launching Services in Background (Screen) ---"
sudo apt-get install -y screen

# Start Backend on Port 80
screen -dmS backend bash -c "source .venv/bin/activate && uvicorn main_api:app --host 0.0.0.0 --port 80 --workers 4"

# Start Frontend on Port 5176 (or Port 80 via Nginx/Vite build)
cd up-weather-intelligence-system
screen -dmS frontend npx vite --host --port 5176 --force

echo "✅ SETUP COMPLETE!"
echo "Global API Port: 80"
echo "Global Dashboard Port: 5176"
