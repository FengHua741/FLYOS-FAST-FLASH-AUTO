#!/usr/bin/env python3
import http.server
import socketserver
import json
import subprocess
import os
import socket
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = 8082

class DeviceBHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = self.generate_web_interface()
            self.wfile.write(html.encode('utf-8'))
            
        elif path == '/lsusb':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result = self.execute_lsusb()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        elif path == '/device-info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result = self.get_device_info()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        elif path == '/run-command':
            query_params = parse_qs(parsed_path.query)
            command = query_params.get('cmd', [''])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result = self.execute_system_command(command)
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/retry-flash':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            result = self.trigger_retry_flash()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        else:
            self.send_error(404)

    def execute_lsusb(self):
        """执行lsusb命令"""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=10)
            output = result.stdout if result.returncode == 0 else result.stderr
            
            return {
                "success": result.returncode == 0,
                "output": output,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "命令执行超时"}
        except Exception as e:
            return {"success": False, "output": f"执行错误: {str(e)}"}

    def get_device_info(self):
        """获取设备信息"""
        try:
            # 获取IP地址
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            
            return {
                "success": True,
                "ip": ip,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {"success": False, "error": f"获取设备信息失败: {str(e)}"}

    def execute_system_command(self, command):
        """执行系统命令"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout if result.returncode == 0 else result.stderr
            
            return {
                "success": result.returncode == 0,
                "output": output,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "命令执行超时"}
        except Exception as e:
            return {"success": False, "output": f"执行错误: {str(e)}"}

    def trigger_retry_flash(self):
        """触发重新烧录"""
        try:
            # 直接执行烧录脚本
            script_path = "/data/FLYOS-FAST-FLASH-AUTO/Device_B/fly-flash-auto.sh"
            result = subprocess.run(
                [script_path],
                capture_output=True, text=True, timeout=5
            )
            
            # 超时是正常的，因为脚本会运行较长时间
            return {
                "success": True,
                "message": "重新烧录指令已发送，烧录流程正在启动...",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
                
        except subprocess.TimeoutExpired:
            return {
                "success": True,
                "message": "重新烧录指令已发送，烧录流程正在启动...",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"success": False, "message": f"触发重新烧录时出错: {str(e)}"}

    def generate_web_interface(self):
        """生成设备B的Web界面"""
        # 获取设备信息
        device_info = self.get_device_info()
        ip_address = device_info.get('ip', '未知') if device_info['success'] else '未知'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>设备B - Fly-Flash 烧录设备</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
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
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .section {{
                    margin-bottom: 30px;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                }}
                .btn {{
                    padding: 10px 20px;
                    background: #007cba;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    margin: 5px;
                }}
                .btn:hover {{
                    background: #005a87;
                }}
                .btn-retry {{
                    background: #ffc107;
                    color: #000;
                }}
                .btn-retry:hover {{
                    background: #e0a800;
                }}
                .result-container {{
                    background: #1a202c;
                    color: #e2e8f0;
                    padding: 15px;
                    border-radius: 6px;
                    margin-top: 10px;
                    font-family: 'Courier New', monospace;
                    white-space: pre-wrap;
                    max-height: 400px;
                    overflow-y: auto;
                }}
                .status {{
                    padding: 10px;
                    border-radius: 4px;
                    margin: 10px 0;
                    font-weight: bold;
                }}
                .status.success {{
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }}
                .status.error {{
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }}
                .device-info {{
                    background: #e9ecef;
                    padding: 15px;
                    border-radius: 4px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 设备B - Fly-Flash 烧录设备</h1>
                
                <div class="device-info">
                    <h3>设备信息</h3>
                    <p><strong>IP地址:</strong> {ip_address}</p>
                    <p><strong>最后更新:</strong> <span id="lastUpdate">-</span></p>
                </div>
                
                <div class="section">
                    <h3>USB设备检测</h3>
                    <p>查看当前连接的USB设备：</p>
                    <button class="btn" onclick="getLsusb()">运行 lsusb</button>
                    <div id="lsusb-result" class="result-container" style="display: none;"></div>
                </div>
                
                <div class="section">
                    <h3>烧录控制</h3>
                    <p>手动触发重新烧录流程：</p>
                    <button class="btn btn-retry" onclick="retryFlash()">重新烧录</button>
                    <div id="retry-status" style="display: none;"></div>
                </div>
                
                <div class="section">
                    <h3>服务管理</h3>
                    <button class="btn" onclick="checkServiceStatus()">检查烧录服务状态</button>
                    <div id="service-result" style="display: none;"></div>
                </div>
            </div>
            
            <script>
                function getLsusb() {{
                    const resultElement = document.getElementById('lsusb-result');
                    resultElement.style.display = 'block';
                    resultElement.innerHTML = '执行中...';
                    
                    fetch('/lsusb')
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                resultElement.innerHTML = data.output;
                                resultElement.style.color = '#0f0';
                            }} else {{
                                resultElement.innerHTML = '错误: ' + data.output;
                                resultElement.style.color = '#f00';
                            }}
                            updateLastUpdate(data.timestamp);
                        }})
                        .catch(error => {{
                            resultElement.innerHTML = '请求失败: ' + error;
                            resultElement.style.color = '#f00';
                        }});
                }}
                
                function retryFlash() {{
                    const statusElement = document.getElementById('retry-status');
                    statusElement.style.display = 'block';
                    statusElement.innerHTML = '<div class="status">发送重新烧录指令...</div>';
                    
                    fetch('/retry-flash', {{method: 'POST'}})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                statusElement.innerHTML = `<div class="status success">✅ ${{data.message}}</div>`;
                            }} else {{
                                statusElement.innerHTML = `<div class="status error">❌ ${{data.message}}</div>`;
                            }}
                            updateLastUpdate(data.timestamp);
                        }})
                        .catch(error => {{
                            statusElement.innerHTML = `<div class="status error">❌ 请求失败: ${{error}}</div>`;
                        }});
                }}
                
                function checkServiceStatus() {{
                    executeSystemCommand('ps aux | grep fly-flash', 'service-result');
                }}
                
                function executeSystemCommand(command, resultId) {{
                    const resultElement = document.getElementById(resultId);
                    resultElement.style.display = 'block';
                    resultElement.innerHTML = '<div class="status">执行中...</div>';
                    
                    fetch('/run-command?cmd=' + encodeURIComponent(command))
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                resultElement.innerHTML = `<div class="status success">✅ 命令执行成功</div><div class="result-container">${{data.output}}</div>`;
                            }} else {{
                                resultElement.innerHTML = `<div class="status error">❌ 命令执行失败</div><div class="result-container">${{data.output}}</div>`;
                            }}
                            updateLastUpdate(data.timestamp);
                        }})
                        .catch(error => {{
                            resultElement.innerHTML = `<div class="status error">❌ 请求失败: ${{error}}</div>`;
                        }});
                }}
                
                function updateLastUpdate(timestamp) {{
                    document.getElementById('lastUpdate').textContent = timestamp;
                }}
            </script>
        </body>
        </html>
        """

    def log_message(self, format, *args):
        # 静默日志，减少输出
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), DeviceBHandler) as httpd:
        print(f"设备B HTTP服务运行在 http://0.0.0.0:{PORT}")
        print("按 Ctrl+C 停止服务器")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")

if __name__ == "__main__":
    start_server()