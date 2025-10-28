#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import time
from datetime import datetime
import threading

PORT = 8081
STATUS_FILE = "/tmp/flash-status.json"

current_status = {
    "status": "waiting",
    "step": "未开始",
    "progress": 0,
    "log": ["系统就绪..."],
    "last_update": None,
    "device_info": None
}

class FlashStatusHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.generate_status_page()
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(current_status, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/log':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            log_text = "\n".join(current_status["log"][-50:])
            self.wfile.write(log_text.encode('utf-8'))
            
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
        else:
            self.send_error(404)

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

    def generate_status_page(self):
        status_color = {
            "waiting": "#888",
            "running": "#ff0", 
            "success": "#0f0",
            "error": "#f00"
        }.get(current_status["status"], "#888")
        
        status_text = {
            "waiting": "等待",
            "running": "运行中", 
            "success": "成功",
            "error": "错误"
        }.get(current_status["status"], "未知")
        
        progress = current_status["progress"]
        log_entries = current_status["log"][-20:]
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fly-Flash 烧录状态</title>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="5">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .status-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eee;
                }}
                .status-badge {{
                    padding: 8px 16px;
                    border-radius: 20px;
                    background: {status_color};
                    color: white;
                    font-weight: bold;
                }}
                .progress-bar {{
                    width: 100%;
                    height: 20px;
                    background: #eee;
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 10px 0;
                }}
                .progress-fill {{
                    height: 100%;
                    background: #4CAF50;
                    width: {progress}%;
                    transition: width 0.3s;
                }}
                .log-container {{
                    background: #000;
                    color: #0f0;
                    padding: 15px;
                    border-radius: 5px;
                    font-family: monospace;
                    height: 400px;
                    overflow-y: auto;
                    margin-top: 20px;
                }}
                .log-entry {{
                    margin: 2px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="status-header">
                    <h1>Fly-Flash 自动烧录系统</h1>
                    <div class="status-badge">
                        {status_text}
                    </div>
                </div>
                
                <div>
                    <h3>当前步骤: {current_status["step"]}</h3>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <div>进度: {progress}%</div>
                </div>
                
                <div>
                    <h3>最后更新: {current_status["last_update"] or "从未"}</h3>
                </div>
                
                <div>
                    <h3>实时日志:</h3>
                    <div class="log-container">
                        {"".join(f'<div class="log-entry">{entry}</div>' for entry in log_entries)}
                    </div>
                </div>
            </div>
            
            <script>
                window.onload = function() {{
                    var logContainer = document.querySelector('.log-container');
                    logContainer.scrollTop = logContainer.scrollHeight;
                }};
            </script>
        </body>
        </html>
        """

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
