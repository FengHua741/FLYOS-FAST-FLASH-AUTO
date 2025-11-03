#!/bin/bash
# deploy-device-b-http.sh

echo "开始部署设备B HTTP服务..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "脚本目录: $SCRIPT_DIR"

# 创建必要的目录
echo "创建系统目录..."
mkdir -p /etc/fly-flash/bin
mkdir -p /etc/fly-flash/firmware
mkdir -p /var/log/fly-flash

# 复制脚本到/etc目录
echo "复制脚本到系统目录..."
cp "$SCRIPT_DIR/device-b-server.py" /etc/fly-flash/bin/
cp "$SCRIPT_DIR/send-status.py" /etc/fly-flash/bin/
cp "$SCRIPT_DIR/fly-flash-auto.sh" /etc/fly-flash/bin/

# 设置执行权限
chmod +x /etc/fly-flash/bin/device-b-server.py
chmod +x /etc/fly-flash/bin/send-status.py
chmod +x /etc/fly-flash/bin/fly-flash-auto.sh

# 更新脚本中的路径
echo "更新脚本路径..."
sed -i 's|/usr/local/bin/|/etc/fly-flash/bin/|g' /etc/fly-flash/bin/fly-flash-auto.sh
sed -i 's|/usr/local/bin/|/etc/fly-flash/bin/|g' /etc/fly-flash/bin/send-status.py

# 安装Python依赖
echo "安装Python依赖..."
pip3 install requests

# 复制systemd服务文件并更新路径
echo "配置systemd服务..."
cp "$SCRIPT_DIR/device-b-http.service" /etc/systemd/system/
cp "$SCRIPT_DIR/fly-flash-auto.service" /etc/systemd/system/

# 更新服务文件中的路径
sed -i 's|/usr/local/bin/|/etc/fly-flash/bin/|g' /etc/systemd/system/device-b-http.service
sed -i 's|/usr/local/bin/|/etc/fly-flash/bin/|g' /etc/systemd/system/fly-flash-auto.service

# 重新加载systemd配置
systemctl daemon-reload

# 启用并启动服务
systemctl enable device-b-http.service
systemctl start device-b-http.service
systemctl enable fly-flash-auto.service

# 检查服务状态
echo "检查服务状态..."
systemctl status device-b-http.service

echo "设备B HTTP服务部署完成!"
echo "服务运行在: http://0.0.0.0:8082"
echo "脚本路径: /etc/fly-flash/bin/"
echo "日志路径: /var/log/fly-flash/"