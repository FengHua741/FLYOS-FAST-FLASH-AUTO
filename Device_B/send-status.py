#!/usr/bin/env python3
import requests
import json
import sys
import os
import socket

# 配置 - 使用设备A的IP地址
SERVER_URL = "http://192.168.101.239:8081/update"  # 设备A的地址

def get_device_ip():
    """获取设备B的IP地址"""
    try:
        # 获取本机IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "未知"

def send_status(step, status, progress, log_message=None, device_info=None):
    data = {
        "step": step,
        "status": status,
        "progress": progress,
        "device_info": device_info,
        "device_b_ip": get_device_ip()  # 添加设备B的IP地址
    }
    
    # 添加日志消息
    if log_message:
        # 从文件读取当前日志或创建新日志
        log_file = "/data/FLYOS-FAST-FLASH-AUTO/Device_B/logs/fly-flash.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.read().splitlines()[-100:]  # 最近100行
        else:
            logs = []
        
        logs.append(log_message)
        data["log"] = logs
    
    try:
        response = requests.post(
            SERVER_URL,
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            print(f"状态上报成功: {step} - {status}")
            return True
        else:
            print(f"状态上报失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"状态上报错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        step = sys.argv[1]
        status = sys.argv[2]
        progress = int(sys.argv[3])
        log_msg = sys.argv[4] if len(sys.argv) > 4 else None
        send_status(step, status, progress, log_msg)
    else:
        print("用法: send-status.py <步骤> <状态> <进度> [日志消息]")
        print("状态: waiting, running, success, error")