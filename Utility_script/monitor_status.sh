#!/bin/bash
echo "=== Fly-Flash 系统状态监控 ==="

read -p "请输入设备A的IP地址 (默认: 192.168.101.239): " device_a_ip
device_a_ip=${device_a_ip:-192.168.101.239}

echo "监控地址: http://$device_a_ip:8081"
echo "按 Ctrl+C 退出监控"

# 检查是否安装了 lynx 或 curl
if command -v lynx &> /dev/null; then
    # 使用 lynx 文本浏览器查看网页
    lynx http://$device_a_ip:8081
elif command -v curl &> /dev/null; then
    # 使用 curl 定期获取状态
    while true; do
        clear
        echo "=== Fly-Flash 状态监控 ==="
        echo "最后更新: $(date)"
        echo "=========================="
        curl -s http://$device_a_ip:8081/status | python3 -m json.tool
        sleep 5
    done
else
    echo "请安装 lynx 或 curl 以进行状态监控"
    echo "sudo apt install lynx"
fi