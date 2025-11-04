#!/bin/bash
# FlyOS-FAST Flash Auto 部署验证脚本

echo "========================================"
echo "  FlyOS-FAST Flash Auto 部署验证"
echo "========================================"

BASE_DIR="/data/FLYOS-FAST-FLASH-AUTO/Device_B"
LOG_DIR="$BASE_DIR/logs"

# 检查目录结构
echo "1. 检查目录结构..."
if [ -d "$BASE_DIR" ]; then
    echo "✅ 基础目录存在: $BASE_DIR"
else
    echo "❌ 基础目录不存在: $BASE_DIR"
    exit 1
fi

if [ -d "$LOG_DIR" ]; then
    echo "✅ 日志目录存在: $LOG_DIR"
else
    echo "❌ 日志目录不存在: $LOG_DIR"
fi

# 检查文件权限
echo ""
echo "2. 检查文件权限..."
files=(
    "device-b-server.py"
    "send-status.py" 
    "fly-flash-auto.sh"
    "deploy-device-b.sh"
    "service-control.sh"
    "verify-deployment.sh"
)

for file in "${files[@]}"; do
    if [ -x "$BASE_DIR/$file" ]; then
        echo "✅ 可执行: $file"
    else
        echo "❌ 不可执行: $file"
    fi
done

# 检查服务状态
echo ""
echo "3. 检查服务状态..."
services=(
    "device-b-http.service"
    "fly-flash-auto.service"
)

for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "✅ 运行中: $service"
    else
        echo "⚠️  未运行: $service"
    fi
    
    if systemctl is-enabled --quiet "$service"; then
        echo "✅ 已启用: $service"
    else
        echo "⚠️  未启用: $service"
    fi
done

# 检查网络连接
echo ""
echo "4. 检查网络连接..."
if ping -c 1 -W 3 192.168.101.239 &> /dev/null; then
    echo "✅ 可以连接到设备A (192.168.101.239)"
else
    echo "❌ 无法连接到设备A (192.168.101.239)"
fi

# 检查 HTTP 服务
echo ""
echo "5. 检查 HTTP 服务..."
if curl -s http://localhost:8082 > /dev/null; then
    echo "✅ 设备B HTTP 服务正常 (端口 8082)"
else
    echo "❌ 设备B HTTP 服务异常"
fi

# 检查固件文件
echo ""
echo "6. 检查固件文件..."
firmware_files=(
    "/usr/lib/firmware/bootloader/hid_bootloader_h723_v1.0.bin"
    "/usr/lib/firmware/klipper/stm32h723-128k-usb.bin"
)

for firmware in "${firmware_files[@]}"; do
    if [ -f "$firmware" ]; then
        echo "✅ 存在: $firmware"
    else
        echo "❌ 不存在: $firmware"
    fi
done

# 检查 fly-flash 工具
echo ""
echo "7. 检查 fly-flash 工具..."
if command -v fly-flash &> /dev/null; then
    echo "✅ fly-flash 工具可用"
else
    echo "❌ fly-flash 工具不可用"
fi

# 检查 Python 依赖
echo ""
echo "8. 检查 Python 依赖..."
if python3 -c "import requests" &> /dev/null; then
    echo "✅ Python requests 库已安装"
else
    echo "❌ Python requests 库未安装"
fi

echo ""
echo "========================================"
echo "验证完成!"
echo "========================================"
echo "访问地址:"
echo "- 设备B HTTP 服务: http://$(hostname -I | awk '{print $1}'):8082"
echo "- 设备A 状态页面: http://192.168.101.239:8081"
echo ""
echo "管理命令:"
echo "- 服务管理: $BASE_DIR/service-control.sh"
echo "- 查看日志: tail -f $LOG_DIR/fly-flash.log"
echo "========================================"