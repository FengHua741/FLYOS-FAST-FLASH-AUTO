#!/usr/bin/env python3
import requests
import json
import sys
import os
import socket
import time
from datetime import datetime

# 配置 - 使用设备A的IP地址
SERVER_URL = "http://192.168.101.239:8081/update"

def get_device_ip():
    """获取设备B的IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "未知"

def send_status(step, status, progress, log_message=None, device_info=None):
    """发送状态到设备A，支持实时日志流"""
    
    # 构建数据包
    data = {
        "step": step,
        "status": status,
        "progress": progress,
        "device_info": device_info,
        "device_b_ip": get_device_ip(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 添加日志消息 - 实时日志流支持
    if log_message:
        # 读取最近的日志文件内容作为历史上下文
        log_file = "/data/FLYOS-FAST-FLASH-AUTO/Device_B/logs/fly-flash.log"
        logs = []
        
        # 如果日志文件存在，读取最近内容
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = f.read().splitlines()[-100:]  # 最近100行作为历史上下文
            except:
                logs = []
        
        # 添加新日志消息
        logs.append(log_message)
        data["log"] = logs
    
    # 重试机制 - 为实时日志流优化
    max_retries = 2
    timeout = 5  # 适当超时时间
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                SERVER_URL,
                json=data,
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                # 成功发送
                return True
            else:
                # 服务器错误，记录但继续
                if attempt < max_retries:
                    time.sleep(0.5)  # 短暂等待后重试
                    
        except requests.exceptions.Timeout:
            # 超时，记录但继续
            if attempt < max_retries:
                time.sleep(0.5)
                
        except requests.exceptions.ConnectionError:
            # 连接错误，记录但继续
            if attempt < max_retries:
                time.sleep(1)
                
        except Exception as e:
            # 其他异常，记录但继续
            if attempt < max_retries:
                time.sleep(0.5)
    
    # 所有重试都失败
    return False

def main():
    """主函数 - 处理命令行参数"""
    if len(sys.argv) >= 4:
        step = sys.argv[1]
        status = sys.argv[2]
        progress = int(sys.argv[3])
        log_msg = sys.argv[4] if len(sys.argv) > 4 else None
        
        # 发送状态
        success = send_status(step, status, progress, log_msg)
        
        if success:
            sys.exit(0)
        else:
            # 即使发送失败也不退出，避免中断烧录流程
            # 只在日志中记录错误
            try:
                log_file = "/data/FLYOS-FAST-FLASH-AUTO/Device_B/logs/fly-flash.log"
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 状态上报失败: {step} {status} {progress} {log_msg}\n")
            except:
                pass
            sys.exit(0)  # 总是返回成功，避免中断主流程
    else:
        print("用法: send-status.py <步骤> <状态> <进度> [日志消息]")
        print("状态: waiting, running, success, error")
        print("示例: send-status.py 'BL烧录' 'running' 20 '开始烧录bootloader'")
        sys.exit(1)

if __name__ == "__main__":
    main()