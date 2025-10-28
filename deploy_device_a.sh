#!/bin/bash
echo "=== 部署设备A (Web服务器) ==="

# 复制文件
echo "复制 Web 服务器脚本..."
sudo cp flash-web-server.py /home/fenghua/
sudo chmod +x /home/fenghua/flash-web-server.py

echo "复制 systemd 服务文件..."
sudo cp flash-web-server.service /etc/systemd/system/

# 重新加载并启用服务
echo "设置 systemd 服务..."
sudo systemctl daemon-reload
sudo systemctl enable flash-web-server.service
sudo systemctl start flash-web-server.service

# 验证部署
echo "验证部署..."
sleep 2
sudo systemctl status flash-web-server.service --no-pager

echo "✅ 设备A部署完成!"
echo "Web 服务器地址: http://$(hostname -I | awk '{print $1}'):8081"