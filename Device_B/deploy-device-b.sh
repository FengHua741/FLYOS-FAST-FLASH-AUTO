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

# 3. 检查并安装 Python 依赖
echo "检查并安装 Python 依赖..."
if python3 -c "import requests" &> /dev/null; then
    echo "requests 库已安装"
else
    echo "安装 requests 库..."
    pip3 install requests
fi

# 4. 更新 fly-flash-auto.sh 中的烧录命令和路径
echo "更新烧录脚本..."
sed -i 's|fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin|fly-flash -d auto -u -f /usr/lib/firmware/bootloader/hid_bootloader_h723_v1.0.bin|g' "$BASE_DIR/fly-flash-auto.sh"

# 添加 HID 烧录命令（在 DFU 烧录成功后）
sed -i '/sleep 5/a\\n    # 第二步：HID刷写  \n    if run_command \\\n        "fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin" \\\n        "HID模式刷写" \\\n        60 \\\n        "> Finish"; then' "$BASE_DIR/fly-flash-auto.sh"

# 更新 send-status.py 调用路径
sed -i "s|/etc/fly-flash/bin/send-status.py|$BASE_DIR/send-status.py|g" "$BASE_DIR/fly-flash-auto.sh"

# 更新日志文件路径
sed -i "s|/var/log/fly-flash.log|$LOG_DIR/fly-flash.log|g" "$BASE_DIR/fly-flash-auto.sh"

# 5. 更新 send-status.py 中的日志路径
sed -i "s|/var/log/fly-flash.log|$LOG_DIR/fly-flash.log|g" "$BASE_DIR/send-status.py"

# 6. 创建 systemd 服务文件
echo "创建 systemd 服务文件..."

# device-b-http.service
cat > /etc/systemd/system/device-b-http.service << EOF
[Unit]
Description=Fly-Flash Device B HTTP Service
After=network.target
Wants=network.target

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

# fly-flash-auto.service
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

# 7. 重新加载 systemd 配置
echo "重新加载 systemd 配置..."
systemctl daemon-reload

# 8. 启用并启动服务
echo "启用并启动服务..."
systemctl enable device-b-http.service
systemctl enable fly-flash-auto.service
systemctl start device-b-http.service

# 9. 检查服务状态
echo "检查服务状态..."
echo "device-b-http.service 状态:"
systemctl status device-b-http.service --no-pager

echo "fly-flash-auto.service 状态:"
systemctl status fly-flash-auto.service --no-pager

echo ""
echo "========================================"
echo "部署完成!"
echo "========================================"
echo "服务已安装并启用:"
echo "- device-b-http.service (HTTP 服务, 端口 8082)"
echo "- fly-flash-auto.service (自动烧录服务)"
echo ""
echo "文件位置:"
echo "- 脚本目录: $BASE_DIR"
echo "- 日志目录: $LOG_DIR"
echo ""
echo "访问地址:"
echo "- 设备B HTTP 服务: http://<设备B-IP>:8082"
echo "- 设备A 状态页面: http://192.168.101.239:8081"
echo ""
echo "烧录命令:"
echo "- BL烧录: fly-flash -d auto -u -f /usr/lib/firmware/bootloader/hid_bootloader_h723_v1.0.bin"
echo "- HID烧录: fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin"
echo "========================================"