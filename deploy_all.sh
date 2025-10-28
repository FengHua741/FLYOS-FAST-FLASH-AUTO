#!/bin/bash
echo "=== Fly-Flash 系统一键部署 ==="

# 检测当前设备类型
echo "检测设备类型..."

if [ -f "/usr/local/bin/fly-flash-auto.py" ]; then
    echo "检测到烧录脚本，当前设备为设备B (烧录设备)"
    ./deploy_device_b.sh
else
    echo "未检测到烧录脚本，当前设备为设备A (Web服务器)"
    ./deploy_device_a.sh
fi

echo ""
echo "部署完成后，请运行以下脚本:"
echo "1. ./test_connection.sh - 测试设备间连接"
echo "2. ./monitor_status.sh - 监控系统状态"
echo "3. ./service_control.sh - 管理服务"