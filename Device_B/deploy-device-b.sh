#!/bin/bash
# FlyOS-FAST Flash Auto 部署脚本 - 设备B

set -e

echo "========================================"
echo "  FlyOS-FAST Flash Auto 部署脚本 - 设备B"
echo "========================================"

# 基础目录
BASE_DIR="/data/FLYOS-FAST-FLASH-AUTO/Device_B"
LOG_DIR="$BASE_DIR/logs"

echo "基础目录: $BASE_DIR"
echo "日志目录: $LOG_DIR"

# 检查是否在正确目录
if [ ! -f "$BASE_DIR/device-b-server.py" ]; then
    echo "错误: 请在 /data/FLYOS-FAST-FLASH-AUTO/Device_B 目录中运行此脚本"
    exit 1
fi

# 1. 创建日志目录
echo "创建日志目录..."
mkdir -p "$LOG_DIR"

# 2. 设置脚本权限
echo "设置脚本权限..."
chmod +x "$BASE_DIR/device-b-server.py"
chmod +x "$BASE_DIR/send-status.py"
chmod +x "$BASE_DIR/fly-flash-auto.sh"
chmod +x "$BASE_DIR/deploy-device-b.sh"
chmod +x "$BASE_DIR/service-control.sh"
chmod +x "$BASE_DIR/verify-deployment.sh"

# 3. 检查并安装 Python 依赖
echo "检查并安装 Python 依赖..."
if python3 -c "import requests" &> /dev/null; then
    echo "requests 库已安装"
else
    echo "安装 requests 库..."
    pip3 install requests
fi

# 4. 创建优化的 systemd 服务文件
echo "创建 systemd 服务文件..."

# device-b-http.service - 添加网络依赖
cat > /etc/systemd/system/device-b-http.service << EOF
[Unit]
Description=Fly-Flash Device B HTTP Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=$BASE_DIR/device-b-server.py
WorkingDirectory=$BASE_DIR
Restart=always
RestartSec=5
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

# fly-flash-auto.service - 保持原有配置
cat > /etc/systemd/system/fly-flash-auto.service << EOF
[Unit]
Description=Fly-Flash Auto Programming Service
After=network.target multi-user.target
Wants=network.target

[Service]
Type=oneshot
ExecStart=$BASE_DIR/fly-flash-auto.sh
RemainAfterExit=no
User=root
Group=root
StandardOutput=journal
StandardError=journal
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF

# 5. 重新加载 systemd 配置
echo "重新加载 systemd 配置..."
systemctl daemon-reload

# 6. 启用并启动服务
echo "启用并启动服务..."
systemctl enable device-b-http.service
systemctl enable fly-flash-auto.service
systemctl start device-b-http.service

# 7. 检查服务状态
echo "检查服务状态..."
echo "device-b-http.service 状态:"
systemctl status device-b-http.service --no-pager | head -10

echo ""
echo "========================================"
echo "部署完成!"
echo "========================================"
echo "优化内容:"
echo "- 网络连接检查机制"
echo "- 状态上报重试机制" 
echo "- 更快的状态上报超时"
echo "- HTTP服务网络依赖优化"
echo ""
echo "服务已安装并启用:"
echo "- device-b-http.service (HTTP 服务, 端口 8082)"
echo "- fly-flash-auto.service (自动烧录服务)"
echo ""
echo "访问地址:"
echo "- 设备B HTTP 服务: http://<设备B-IP>:8082"
echo "- 设备A 状态页面: http://192.168.101.239:8081"
echo "========================================"