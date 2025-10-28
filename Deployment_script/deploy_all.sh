#!/bin/bash
echo "=== Fly-Flash 系统一键部署 ==="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 检测当前设备类型
echo "检测设备类型..."

if [ -f "/usr/local/bin/fly-flash-auto.sh" ]; then
    echo "检测到烧录脚本，当前设备为设备B (烧录设备)"
    $SCRIPT_DIR/deploy_device_b.sh
else
    echo "未检测到烧录脚本，当前设备为设备A (Web服务器)"
    $SCRIPT_DIR/deploy_device_a.sh
fi

echo ""
echo "部署完成后，请运行以下脚本:"
echo "1. ./Utility_script/test_connection.sh - 测试设备间连接"
echo "2. ./Utility_script/monitor_status.sh - 监控系统状态"
echo "3. ./Utility_script/service_control.sh - 管理服务"