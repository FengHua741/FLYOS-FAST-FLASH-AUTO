#!/bin/bash
echo "=== 部署设备B (烧录设备) ==="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "项目根目录: $PROJECT_ROOT"

# 安装依赖
echo "安装 Python 依赖..."
pip install requests

# 部署脚本
echo "部署烧录脚本..."
sudo cp $PROJECT_ROOT/Device_B/fly-flash-auto.sh /usr/local/bin/
sudo cp $PROJECT_ROOT/Device_B/send-status.py /usr/local/bin/
sudo chmod +x /usr/local/bin/fly-flash-auto.sh
sudo chmod +x /usr/local/bin/send-status.py

# 部署服务
echo "部署 systemd 服务..."
sudo cp $PROJECT_ROOT/Device_B/fly-flash-auto.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fly-flash-auto.service

# 验证部署
echo "验证脚本权限..."
ls -la /usr/local/bin/send-status.py
ls -la /usr/local/bin/fly-flash-auto.sh

echo "✅ 设备B部署完成!"
echo "烧录服务已启用开机自动启动"