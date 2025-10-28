#!/bin/bash
echo "=== 测试设备间连接 ==="

read -p "请输入设备A的IP地址 (默认: 192.168.101.239): " device_a_ip
device_a_ip=${device_a_ip:-192.168.101.239}

echo "测试连接到设备A: $device_a_ip"

# 测试网络连通性
echo "1. 测试网络连通性..."
ping -c 3 $device_a_ip

# 测试Web服务器
echo "2. 测试Web服务器..."
curl -s -I http://$device_a_ip:8081/ | head -n 1

# 测试状态上报
echo "3. 测试状态上报..."
python3 /usr/local/bin/send-status.py "connection_test" "running" 50 "连接测试成功"

echo "✅ 连接测试完成!"