#!/bin/bash
# ==============================================================================
# Procurement Standards Recommendation System - AWS EC2 Automated Deployment Script
# CSE2025 - AWS Solution Architect Project
# Supported OS: Ubuntu 22.04 / 24.04 LTS (Amazon EC2 t2.micro / t3.micro)
# ==============================================================================

set -e

echo "=== [0/6] Configuring 2GB Swap Memory (ensures t2.micro Free Tier stability) ==="
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap allocated successfully."
fi

echo "=== [1/6] Updating system packages ==="
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv nginx git curl

echo "=== [2/6] Installing Node.js & npm (v20 LTS) ==="
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

PROJECT_DIR="/home/ubuntu/ProcurementApp"
cd "$PROJECT_DIR"

echo "=== [3/6] Setting up Python virtual environment & backend ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

cd backend
python manage.py migrate
python manage.py collectstatic --noinput || true
cd ..

echo "=== [4/6] Building React Frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== [5/6] Setting up Gunicorn Systemd Service ==="
sudo bash -c "cat > /etc/systemd/system/procurement.service << 'EOF'
[Unit]
Description=Gunicorn instance to serve Procurement Standards Recommendation Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/ProcurementApp/backend
Environment=\"PATH=/home/ubuntu/ProcurementApp/venv/bin\"
ExecStart=/home/ubuntu/ProcurementApp/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 backend.wsgi:application

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl start procurement
sudo systemctl enable procurement

echo "=== [6/6] Configuring Nginx Reverse Proxy ==="
sudo bash -c "cat > /etc/nginx/sites-available/procurement << 'EOF'
server {
    listen 80;
    server_name _;

    # Serve React Frontend static files
    location / {
        root /home/ubuntu/ProcurementApp/frontend/dist;
        index index.html index.htm;
        try_files \$uri \$uri/ /index.html;
    }

    # Proxy API requests to Gunicorn Django backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 90;
    }
}
EOF"

sudo ln -sf /etc/nginx/sites-available/procurement /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "=========================================================================="
echo " Deployment Complete!"
echo " Access your public web application at: http://$(curl -s http://checkip.amazonaws.com)"
echo "=========================================================================="
