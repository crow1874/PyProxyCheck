#!/bin/bash
# Developer: 乌鸦 (Crow) | Telegram: https://t.me/cfwuya1
# Project: PyProxyCheck

REPO_URL_BASE="https://raw.githubusercontent.com/crow1874/PyProxyCheck/main"
INSTALL_PATH="/opt/jiance"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
PLAIN="\033[0m"

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}Error: Run as root required.${PLAIN}"
    exit 1
fi

clear
echo -e "${GREEN}### PyProxyCheck Installer | Dev: 乌鸦 ###${PLAIN}\n"
echo -e "${YELLOW}Select Mode:${PLAIN}"
echo -e "1. Base (Backend Only, port 8000)"
echo -e "2. Full (Nginx + SSL + Domain)"
read -p "Enter [1-2] (Default 1): " INSTALL_MODE
[[ -z "$INSTALL_MODE" ]] && INSTALL_MODE="1"

if [ -f /etc/debian_version ]; then
    apt-get update -y
    apt-get install -y curl git ufw python3.10 python3.10-venv python3.10-dev python3-pip socat cron
    [[ "$INSTALL_MODE" == "2" ]] && apt-get install -y nginx python3-certbot-nginx
elif [ -f /etc/redhat-release ]; then
    yum update -y
    yum install -y git curl firewalld python3 python3-pip socat cronie
    if [[ "$INSTALL_MODE" == "2" ]]; then
        yum install -y epel-release
        yum install -y nginx certbot python3-certbot-nginx
    fi
fi

if ! sysctl net.ipv4.tcp_congestion_control | grep -q "bbr"; then
    echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
    echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
    sysctl -p
fi

PORTS=("8000")
[[ "$INSTALL_MODE" == "2" ]] && PORTS+=("80" "443")
for PORT in "${PORTS[@]}"; do
    if command -v ufw &> /dev/null; then ufw allow $PORT/tcp; fi
    if command -v firewall-cmd &> /dev/null; then firewall-cmd --zone=public --add-port=$PORT/tcp --permanent; fi
    if command -v iptables &> /dev/null; then iptables -I INPUT -p tcp --dport $PORT -j ACCEPT; fi
done
if command -v ufw &> /dev/null; then ufw reload; fi
if command -v firewall-cmd &> /dev/null; then firewall-cmd --reload; fi

if [ -d "$INSTALL_PATH" ]; then rm -rf "$INSTALL_PATH"; fi
mkdir -p "$INSTALL_PATH"
cd "$INSTALL_PATH"
python3 -m venv venv
source venv/bin/activate

curl -L -o main.py "${REPO_URL_BASE}/main.py"
curl -L -o requirements.txt "${REPO_URL_BASE}/requirements.txt"
if [[ ! -s main.py ]] || grep -q "404: Not Found" main.py; then
    echo -e "${YELLOW}Private Repo detected. Enter Token:${PLAIN}"
    read -p "Token: " GITHUB_TOKEN
    if [ -n "$GITHUB_TOKEN" ]; then
        curl -L -o main.py "${REPO_URL_BASE}/main.py?token=${GITHUB_TOKEN}"
        curl -L -o requirements.txt "${REPO_URL_BASE}/requirements.txt?token=${GITHUB_TOKEN}"
    else
        exit 1
    fi
fi

pip install --upgrade pip
pip install -r requirements.txt

DEFAULT_PASS="admin123"
cat > /etc/systemd/system/jiance.service <<EOF
[Unit]
Description=PyProxyCheck Service (Dev: Crow)
After=network.target
[Service]
User=root
Group=root
WorkingDirectory=${INSTALL_PATH}
Environment="PATH=${INSTALL_PATH}/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${INSTALL_PATH}/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --access-logfile -
Restart=always
RestartSec=3
LimitNOFILE=1000000
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable jiance
systemctl restart jiance

ACCESS_URL=""
if [[ "$INSTALL_MODE" == "2" ]]; then
    read -p "Enter Domain (e.g. ip.test.com): " USER_DOMAIN
    if [[ -n "$USER_DOMAIN" ]]; then
        cat > /etc/nginx/conf.d/jiance.conf <<EOF
server {
    listen 80;
    server_name $USER_DOMAIN;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
        if command -v systemctl &> /dev/null; then systemctl restart nginx; else service nginx restart; fi
        certbot --nginx -d "$USER_DOMAIN" --non-interactive --agree-tos -m admin@$USER_DOMAIN --redirect
        if [[ $? -eq 0 ]]; then ACCESS_URL="https://${USER_DOMAIN}"; else ACCESS_URL="http://${USER_DOMAIN}"; fi
    fi
fi

IPV4=$(curl -s4m 8 ip.sb)
[[ -z "$ACCESS_URL" ]] && ACCESS_URL="http://${IPV4}:8000"
echo -e "\n${GREEN}Success! Access: ${ACCESS_URL}${PLAIN}"
echo -e "Dev: 乌鸦 | Telegram: https://t.me/cfwuya1\n"
