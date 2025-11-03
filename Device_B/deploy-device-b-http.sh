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
mkdir -p /data/fly-flash/templates

# 复制所有脚本到/data目录
echo "复制脚本到/data目录..."
cp "$SCRIPT_DIR/device-b-server.py" /data/fly-flash/bin/
cp "$SCRIPT_DIR/send-status.py" /data/fly-flash/bin/
cp "$SCRIPT_DIR/fly-flash-auto.sh" /data/fly-flash/bin/

# 设置执行权限
chmod +x /data/fly-flash/bin/device-b-server.py
chmod +x /data/fly-flash/bin/send-status.py
chmod +x /data/fly-flash/bin/fly-flash-auto.sh
