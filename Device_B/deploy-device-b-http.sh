#!/bin/bash
# deploy-device-b-http.sh

echo "开始部署设备B HTTP服务..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "脚本目录: $SCRIPT_DIR"

# 在/data目录下创建完整的目录结构
echo "在/data目录下创建目录结构..."
mkdir -p /data/fly-flash/bin
mkdir -p /data/fly-flash/logs

# 复制所有脚本到/data目录
echo "复制脚本到/data目录..."
cp "$SCRIPT_DIR/device-b-server.py" /data/fly-flash/bin/
cp "$SCRIPT_DIR/send-status.py" /data/fly-flash/bin/
cp "$SCRIPT_DIR/fly-flash-auto.sh" /data/fly-flash/bin/

# 设置执行权限 - 只在/data目录下操作
echo "设置执行权限..."
chmod +x /data/fly-flash/bin/device-b-server.py
chmod +x /data/fly-flash/bin/send-status.py
chmod +x /data/fly-flash/bin/fly-flash-auto.sh

# 确保所有脚本使用正确的路径
echo "更新脚本中的路径引用..."
sed -i 's|/usr/local/bin/|/data/fly-flash/bin/|g' /data/fly-flash/bin/fly-flash-auto.sh
sed -i 's|/usr/local/bin/|/data/fly-flash/bin/|g' /data/fly-flash/bin/send-status.py
sed -i 's|/var/log/fly-flash/|/data/fly-flash/logs/|g' /data/fly-flash/bin/fly-flash-auto.sh

# 确保烧录命令格式正确
echo "验证烧录命令格式..."
if ! grep -q "fly-flash -d auto -h -f" /data/fly-flash/bin/fly-flash-auto.sh; then
    echo "修复烧录命令格式..."
    sed -i 's|fly-flash -d auto -u -f|fly-flash -d auto -h -f|g' /data/fly-flash/bin/fly-flash-auto.sh
fi

# 安装Python依赖
echo "安装Python依赖..."
pip3 install requests

# 创建systemd服务文件 - 指向/data目录
echo "创建systemd服务文件..."
mkdir -p /etc/systemd/system

cat > /etc/systemd/system/device-b-http.service << 'EOF'
[Unit]
Description=Fly-Flash Device B HTTP Service
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=/data/fly-flash/bin/device-b-server.py
WorkingDirectory=/data/fly-flash/bin
Restart=always
RestartSec=5
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/fly-flash-auto.service << 'EOF'
[Unit]
Description=Fly-Flash Auto Programming Service
After=network.target multi-user.target
Wants=network.target

[Service]
Type=oneshot
ExecStart=/data/fly-flash/bin/fly-flash-auto.sh
RemainAfterExit=no
User=root
Group=root
StandardOutput=journal
StandardError=journal
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
systemctl daemon-reload

# 启用并启动服务
systemctl enable device-b-http.service
systemctl start device-b-http.service
systemctl enable fly-flash-auto.service

# 检查服务状态
echo "检查服务状态..."
systemctl status device-b-http.service --no-pager

echo "========================================"
echo "设备B HTTP服务部署完成!"
echo "所有文件位置: /data/fly-flash/"
echo "HTTP服务运行在: http://0.0.0.0:8082"
echo "烧录命令格式: fly-flash -d auto -h -f <固件路径>"
echo "========================================"