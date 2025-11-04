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
    "log": ["系统就绪，等待烧录..."],
    "last_update": None,
    "device_info": None,
    "device_b_ip": None
}

# 全局状态变量
current_status = initial_status.copy()

def debug_log(message):
    """调试日志函数"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] DEBUG: {message}")
    # 同时写入调试文件
    with open("/tmp/flash-server-debug.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] DEBUG: {message}\n")

class FlashStatusHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        debug_log(f"GET请求: {path}")
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = self.load_template("status.html")
            self.wfile.write(html.encode('utf-8'))
            
        elif path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps(current_status, ensure_ascii=False)
            debug_log(f"返回状态: {response}")
            self.wfile.write(response.encode('utf-8'))
            
        elif path == '/debug':
            # 调试端点，返回调试信息
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            try:
                with open("/tmp/flash-server-debug.log", "r", encoding="utf-8") as f:
                    debug_content = f.read()
                self.wfile.write(debug_content.encode('utf-8'))
            except:
                self.wfile.write("调试日志文件不存在")
            
        else:
            self.send_error(404)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        debug_log(f"POST请求: {path}")
        
        if path == '/update':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            debug_log(f"接收到数据长度: {content_length}")
            debug_log(f"原始数据: {post_data.decode('utf-8')}")
            
            try:
                update_data = json.loads(post_data.decode('utf-8'))
                debug_log(f"解析后的JSON: {json.dumps(update_data, ensure_ascii=False, indent=2)}")
                
                self.update_status(update_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({"success": True, "message": "状态更新成功"})
                self.wfile.write(response.encode('utf-8'))
                debug_log("成功处理更新请求")
                
            except Exception as e:
                error_msg = f"处理更新时出错: {str(e)}"
                debug_log(error_msg)
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = json.dumps({"success": False, "error": error_msg})
                self.wfile.write(error_response.encode('utf-8'))
                
        elif path == '/reset':
            # 重置状态端点
            self.reset_status()
            
        elif path == '/retry-flash':
            # 重新烧录端点
            self.retry_flash()
            
        else:
            self.send_error(404)

    def update_status(self, data):
        """更新状态 - 修复日志显示问题"""
        global current_status
        
        debug_log(f"开始更新状态，当前步骤: {current_status.get('step')}")
        
        # 更新基本状态信息
        for key in ["step", "status", "device_info", "device_b_ip"]:
            if key in data and data[key] is not None:
                old_value = current_status.get(key)
                new_value = data[key]
                current_status[key] = new_value
                debug_log(f"更新字段 {key}: {old_value} -> {new_value}")
        
        # 处理日志更新 - 修复日志显示问题
        if "log" in data and data["log"] is not None:
            if isinstance(data["log"], list):
                old_log_count = len(current_status["log"])
                
                # 关键修复：正确处理日志更新
                # 如果接收到的是完整的日志数组，替换整个日志
                # 如果接收到的是新日志条目，追加到现有日志
                if data.get("replace_log", False) or len(data["log"]) > 10:
                    # 如果明确要求替换或者日志条目很多，认为是完整日志
                    current_status["log"] = data["log"]
                    debug_log(f"替换整个日志数组: {old_log_count} -> {len(data['log'])} 行")
                else:
                    # 否则认为是新日志条目，追加到现有日志
                    current_status["log"].extend(data["log"])
                    debug_log(f"追加日志: {old_log_count} -> {len(current_status['log'])} 行")
                
                # 限制日志长度，避免过大
                if len(current_status["log"]) > 1000:
                    current_status["log"] = current_status["log"][-500:]
                    debug_log("日志过长，截断到500行")
                
                # 打印前几行日志作为示例
                sample_logs = current_status["log"][-5:] if len(current_status["log"]) >= 5 else current_status["log"]
                for i, log_line in enumerate(sample_logs):
                    debug_log(f"日志示例[{i}]: {log_line}")
            elif isinstance(data["log"], str):
                # 如果是字符串，作为单条日志追加
                current_status["log"].append(data["log"])
                debug_log(f"追加单条日志: {data['log']}")
            else:
                debug_log(f"警告: log字段不是列表或字符串类型: {type(data['log'])}")
        
        current_status["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存到文件
        try:
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_status, f, ensure_ascii=False, indent=2)
            debug_log("状态已保存到文件")
        except Exception as e:
            debug_log(f"保存状态文件失败: {str(e)}")

    def reset_status(self):
        """重置状态到初始值"""
        global current_status
        current_status = initial_status.copy()
        current_status["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存到文件
        try:
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_status, f, ensure_ascii=False, indent=2)
            debug_log("状态已重置到初始状态")
        except Exception as e:
            debug_log(f"保存状态文件失败: {str(e)}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"success": True, "message": "状态重置成功"})
        self.wfile.write(response.encode('utf-8'))

    def retry_flash(self):
        """重新烧录 - 重置状态并准备重新开始"""
        global current_status
        
        # 完全重置状态，包括清理日志
        current_status = initial_status.copy()
        current_status["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_status["log"] = ["系统就绪，准备重新烧录..."]  # 明确清理日志
        
        # 保存到文件
        try:
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_status, f, ensure_ascii=False, indent=2)
            debug_log("状态已重置，准备重新烧录")
        except Exception as e:
            debug_log(f"保存状态文件失败: {str(e)}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"success": True, "message": "重新烧录已开始"})
        self.wfile.write(response.encode('utf-8'))

    def load_template(self, template_name):
        """加载HTML模板文件"""
        template_path = os.path.expanduser(f"~/FLYOS-FAST-FLASH-AUTO/Device_A/templates/{template_name}")
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            debug_log(f"模板文件未找到: {template_path}")
            return f"<h1>模板文件 {template_name} 未找到</h1>"

    def log_message(self, format, *args):
        """静默日志，减少输出"""
        pass

def start_server():
    """启动HTTP服务器"""
    debug_log("启动Fly-Flash状态服务器")
    
    # 确保调试文件存在
    open("/tmp/flash-server-debug.log", "w").close()
    
    with socketserver.TCPServer(("", PORT), FlashStatusHandler) as httpd:
        debug_log(f"Fly-Flash 状态服务器运行在 http://0.0.0.0:{PORT}")
        print(f"Fly-Flash 状态服务器运行在 http://0.0.0.0:{PORT}")
        print("调试版本 - 详细日志输出到 /tmp/flash-server-debug.log")
        print("按 Ctrl+C 停止服务器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            debug_log("服务器被用户停止")
            print("\n服务器已停止")

if __name__ == "__main__":
    start_server()
