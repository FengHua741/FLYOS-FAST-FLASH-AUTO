#!/bin/bash
# deploy-device-b-http.sh

echo "开始部署设备B HTTP服务..."

# 复制脚本到系统目录
echo "复制脚本到系统目录..."
cp device-b-server.py /usr/local/bin/
cp send-status.py /usr/local/bin/
cp fly-flash-auto.sh /usr/local/bin/

# 设置执行权限
chmod +x /usr/local/bin/device-b-server.py
chmod +x /usr/local/bin/send-status.py
chmod +x /usr/local/bin/fly-flash-auto.sh

# 安装Python依赖
echo "安装Python依赖..."
pip3 install requests

# 复制systemd服务文件
echo "配置systemd服务..."
cp device-b-http.service /etc/systemd/system/
cp fly-flash-auto.service /etc/systemd/system/

# 重新加载systemd配置
systemctl daemon-reload

# 启用并启动服务
systemctl enable device-b-http.service
systemctl start device-b-http.service

systemctl enable fly-flash-auto.service

# 检查服务状态
echo "检查服务状态..."
systemctl status device-b-http.service

echo "设备B HTTP服务部署完成!"
echo "服务运行在: http://0.0.0.0:8082"
echo "烧录服务已启用，将在下次启动时自动运行"