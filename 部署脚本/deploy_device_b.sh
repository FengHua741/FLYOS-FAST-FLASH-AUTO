#!/bin/bash
echo "=== 部署设备B (烧录设备) ==="

# 安装依赖
echo "安装 Python 依赖..."
pip install requests

# 部署脚本
echo "部署烧录脚本..."
sudo cp send-status.py /usr/local/bin/
sudo cp fly-flash-auto.py /usr/local/bin/
sudo chmod +x /usr/local/bin/send-status.py
sudo chmod +x /usr/local/bin/fly-flash-auto.py

# 部署服务
echo "部署 systemd 服务..."
sudo cp fly-flash-auto.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fly-flash-auto.service

# 验证部署
echo "验证脚本权限..."
ls -la /usr/local/bin/send-status.py
ls -la /usr/local/bin/fly-flash-auto.py

echo "✅ 设备B部署完成!"
echo "烧录服务已启用开机自动启动"