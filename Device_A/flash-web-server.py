#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import time
import subprocess
import threading
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests

PORT = 8081
STATUS_FILE = "/tmp/flash-status.json"

# 初始状态
initial_status = {
    "status": "waiting",
    "step": "未开始",
    "progress": 0,
    "log": ["系统就绪，等待烧录..."],
    "last_update": None,
    "device_info": None,
    "device_b_ip": None
}

current_status = initial_status.copy()

class FlashStatusHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = self.load_template("status.html")
            self.wfile.write(html.encode('utf-8'))
            
        elif path == '/tools':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = self.load_template("tools.html")
            self.wfile.write(html.encode('utf-8'))
            
        elif path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(current_status, ensure_ascii=False).encode('utf-8'))
            
        elif path == '/log':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            log_text = "\n".join(current_status["log"][-50:])
            self.wfile.write(log_text.encode('utf-8'))
            
        elif path == '/reset':
            self.reset_status()
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            
        elif path == '/run-command':
            # 执行命令的API
            query_params = parse_qs(parsed_path.query)
            command_type = query_params.get('type', [''])[0]
            command = query_params.get('cmd', [''])[0]
            
            result = self.execute_command(command_type, command)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/update':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                update_data = json.loads(post_data.decode('utf-8'))
                self.update_status(update_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                
            except Exception as e:
                print(f"Error processing update: {e}")
                self.send_response(400)
                self.end_headers()
                
        elif self.path == '/reset':
            self.reset_status()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            
        elif self.path == '/retry-flash':
            # 重新烧录的API
            success = self.trigger_retry_flash()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": success}).encode('utf-8'))
            
        else:
            self.send_error(404)

    def execute_command(self, command_type, command):
        """执行命令并返回结果"""
        try:
            if command_type == "system":
                # 系统命令直接执行
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            elif command_type == "python":
                # Python脚本
                result = subprocess.run(['python3', '-c', command], capture_output=True, text=True, timeout=30)
            else:
                return {"success": False, "output": "未知命令类型"}
            
            output = result.stdout if result.returncode == 0 else result.stderr
            return {
                "success": result.returncode == 0,
                "output": output,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "命令执行超时"}
        except Exception as e:
            return {"success": False, "output": f"执行错误: {str(e)}"}

    def trigger_retry_flash(self):
        """触发设备B重新烧录"""
        try:
            # 获取设备B的IP地址
            device_b_ip = current_status.get("device_b_ip")
            if not device_b_ip:
                print("设备B IP地址未知，无法触发重新烧录")
                return False
            
            # 向设备B发送重新烧录命令
            response = requests.post(
                f"http://{device_b_ip}:8082/retry-flash",
                timeout=10
            )
            
            if response.status_code == 200:
                print("重新烧录指令已发送到设备B")
                return True
            else:
                print(f"重新烧录指令发送失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"触发重新烧录时出错: {e}")
            return False

    def reset_status(self):
        global current_status
        current_status = initial_status.copy()
        current_status["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_status, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        print("状态已重置")

    def update_status(self, data):
        global current_status
        for key in data:
            if key in current_status:
                current_status[key] = data[key]
        
        current_status["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_status, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        print(f"状态更新: {data.get('step', 'unknown')}")

    def load_template(self, template_name):
        """加载HTML模板文件"""
        template_path = os.path.expanduser(f"~/FLYOS-FAST-FLASH-AUTO/Device_A/templates/{template_name}")
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"模板文件未找到: {template_path}")
            return f"<h1>模板文件 {template_name} 未找到</h1>"

    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), FlashStatusHandler) as httpd:
        print(f"Fly-Flash 状态服务器运行在 http://0.0.0.0:{PORT}")
        print("按 Ctrl+C 停止服务器")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")

if __name__ == "__main__":
    start_server()