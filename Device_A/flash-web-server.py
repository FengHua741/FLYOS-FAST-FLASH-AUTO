#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import time
import subprocess
import threading
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = 8081
STATUS_FILE = "/tmp/flash-status.json"

# 初始状态
initial_status = {
    "status": "waiting",
    "step": "未开始",
    "progress": 0,
    "log": ["系统就绪，等待烧录..."],
    "last_update": None,
    "device_info": None
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
            html = self.generate_status_page()
            self.wfile.write(html.encode('utf-8'))
            
        elif path == '/tools':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = self.generate_tools_page()
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

    def generate_navigation(self, current_page):
        """生成导航栏"""
        status_active = "active" if current_page == "status" else ""
        tools_active = "active" if current_page == "tools" else ""
        
        return f"""
        <nav class="navbar">
            <div class="nav-container">
                <div class="nav-logo">
                    <h2>Fly-Flash 系统</h2>
                </div>
                <div class="nav-menu">
                    <a href="/" class="nav-link {status_active}">状态监控</a>
                    <a href="/tools" class="nav-link {tools_active}">系统工具</a>
                </div>
            </div>
        </nav>
        """

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
            <meta http-equiv="refresh" content="10">
            <style>
                {self.get_common_styles()}
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
                .controls {{
                    margin: 15px 0;
                    text-align: right;
                }}
            </style>
        </head>
        <body>
            {self.generate_navigation("status")}
            <div class="container">
                <div class="status-header">
                    <h1>Fly-Flash 自动烧录系统</h1>
                    <div class="status-badge">
                        {status_text}
                    </div>
                </div>
                
                <div class="controls">
                    <button class="btn" onclick="window.location.reload()">刷新页面</button>
                    <button class="btn btn-reset" onclick="resetStatus()">重置状态</button>
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
                function resetStatus() {{
                    fetch('/reset', {{method: 'POST'}})
                        .then(response => {{
                            if(response.ok) {{
                                window.location.reload();
                            }}
                        }});
                }}
                
                window.onload = function() {{
                    var logContainer = document.querySelector('.log-container');
                    logContainer.scrollTop = logContainer.scrollHeight;
                }};
            </script>
        </body>
        </html>
        """

    def generate_tools_page(self):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fly-Flash 系统工具</title>
            <meta charset="utf-8">
            <style>
                {self.get_common_styles()}
                .tools-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-top: 20px;
                }}
                .tool-section {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .command-group {{
                    margin-bottom: 25px;
                }}
                .command-group h3 {{
                    color: #333;
                    border-bottom: 2px solid #007cba;
                    padding-bottom: 8px;
                    margin-bottom: 15px;
                }}
                .command-item {{
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 12px;
                    margin-bottom: 10px;
                    display: flex;
                    justify-content: between;
                    align-items: center;
                }}
                .command-text {{
                    flex-grow: 1;
                    font-family: 'Courier New', monospace;
                    background: #2d3748;
                    color: #e2e8f0;
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin-right: 10px;
                    word-break: break-all;
                }}
                .command-actions {{
                    display: flex;
                    gap: 8px;
                }}
                .btn-copy {{
                    background: #28a745;
                }}
                .btn-run {{
                    background: #007cba;
                }}
                .btn-run:hover {{
                    background: #005a87;
                }}
                .btn-copy:hover {{
                    background: #218838;
                }}
                .result-container {{
                    background: #1a202c;
                    color: #e2e8f0;
                    padding: 15px;
                    border-radius: 6px;
                    margin-top: 10px;
                    font-family: 'Courier New', monospace;
                    white-space: pre-wrap;
                    max-height: 300px;
                    overflow-y: auto;
                    display: none;
                }}
                .search-section {{
                    grid-column: 1 / -1;
                }}
                .search-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }}
                @media (max-width: 768px) {{
                    .tools-grid {{
                        grid-template-columns: 1fr;
                    }}
                    .search-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            {self.generate_navigation("tools")}
            <div class="container">
                <div class="page-header">
                    <h1>系统工具</h1>
                    <p>设备搜索和常用命令工具</p>
                </div>

                <div class="search-section tool-section">
                    <h2>设备搜索</h2>
                    <div class="search-grid">
                        <div class="command-group">
                            <h3>USB 设备搜索</h3>
                            <div class="command-item">
                                <div class="command-text">lsusb</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('lsusb')">复制</button>
                                    <button class="btn btn-run" onclick="runCommand('lsusb', 'system', 'usb-result')">执行</button>
                                </div>
                            </div>
                            <div id="usb-result" class="result-container"></div>
                        </div>

                        <div class="command-group">
                            <h3>设备ID搜索</h3>
                            <div class="command-item">
                                <div class="command-text">ls /dev/serial/by-id/*</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('ls /dev/serial/by-id/*')">复制</button>
                                    <button class="btn btn-run" onclick="runCommand('ls /dev/serial/by-id/*', 'system', 'usbid-result')">执行</button>
                                </div>
                            </div>
                            <div class="command-item">
                                <div class="command-text">~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0')">复制</button>
                                    <button class="btn btn-run" onclick="runCommand('~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0', 'system', 'canid-result')">执行</button>
                                </div>
                            </div>
                            <div id="usbid-result" class="result-container"></div>
                            <div id="canid-result" class="result-container"></div>
                        </div>
                    </div>
                </div>

                <div class="tools-grid">
                    <div class="tool-section">
                        <div class="command-group">
                            <h3>📄 文档指令</h3>
                            <div class="command-item">
                                <div class="command-text">pnpm run start --host 0.0.0.0 --port 3000</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('pnpm run start --host 0.0.0.0 --port 3000')">复制</button>
                                </div>
                            </div>
                            <div class="command-item">
                                <div class="command-text">pnpm run build-all</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('pnpm run build-all')">复制</button>
                                </div>
                            </div>
                            <div class="command-item">
                                <div class="command-text">python3 scripts/all-png2webp.py</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('python3 scripts/all-png2webp.py')">复制</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tool-section">
                        <div class="command-group">
                            <h3>🔧 设备指令</h3>
                            <div class="command-item">
                                <div class="command-text">ls /dev/serial/by-id/*</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('ls /dev/serial/by-id/*')">复制</button>
                                </div>
                            </div>
                            <div class="command-item">
                                <div class="command-text">~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0')">复制</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tool-section">
                        <div class="command-group">
                            <h3>⚙️ 系统指令</h3>
                            <div class="command-item">
                                <div class="command-text">sudo modprobe can && echo "您的内核支持CAN" || echo "您的内核不支持CAN"</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('sudo modprobe can && echo \"您的内核支持CAN\" || echo \"您的内核不支持CAN\"')">复制</button>
                                </div>
                            </div>
                            <div class="command-item">
                                <div class="command-text">ip -details link show can0</div>
                                <div class="command-actions">
                                    <button class="btn btn-copy" onclick="copyCommand('ip -details link show can0')">复制</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                function copyCommand(command) {{
                    navigator.clipboard.writeText(command).then(function() {{
                        showNotification('命令已复制到剪贴板');
                    }}).catch(function(err) {{
                        showNotification('复制失败: ' + err);
                    }});
                }}

                function runCommand(command, type, resultId) {{
                    const resultElement = document.getElementById(resultId);
                    resultElement.style.display = 'block';
                    resultElement.innerHTML = '执行中...';
                    
                    fetch(`/run-command?type=${{type}}&cmd=${{encodeURIComponent(command)}}`)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                resultElement.innerHTML = data.output || '命令执行成功，无输出';
                                resultElement.style.color = '#0f0';
                            }} else {{
                                resultElement.innerHTML = data.output || '命令执行失败';
                                resultElement.style.color = '#f00';
                            }}
                        }})
                        .catch(error => {{
                            resultElement.innerHTML = '请求失败: ' + error;
                            resultElement.style.color = '#f00';
                        }});
                }}

                function showNotification(message) {{
                    // 简单的通知实现
                    const notification = document.createElement('div');
                    notification.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #28a745;
                        color: white;
                        padding: 12px 20px;
                        border-radius: 4px;
                        z-index: 1000;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    `;
                    notification.textContent = message;
                    document.body.appendChild(notification);
                    
                    setTimeout(() => {{
                        document.body.removeChild(notification);
                    }}, 2000);
                }}
            </script>
        </body>
        </html>
        """

    def get_common_styles(self):
        """返回通用样式"""
        return """
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .navbar {
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 0 20px;
        }
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
        }
        .nav-logo h2 {
            margin: 0;
            color: #333;
        }
        .nav-menu {
            display: flex;
            gap: 30px;
        }
        .nav-link {
            text-decoration: none;
            color: #666;
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 4px;
            transition: all 0.3s;
        }
        .nav-link:hover {
            color: #007cba;
            background: #f8f9fa;
        }
        .nav-link.active {
            color: #007cba;
            background: #e3f2fd;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .page-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .page-header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .page-header p {
            color: #666;
            font-size: 16px;
        }
        .btn {
            padding: 8px 16px;
            background: #007cba;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #005a87;
        }
        .btn-reset {
            background: #dc3545;
        }
        .btn-reset:hover {
            background: #c82333;
        }
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