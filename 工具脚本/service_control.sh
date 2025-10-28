#!/bin/bash
echo "=== 服务管理菜单 ==="
echo "1. 启动烧录服务"
echo "2. 停止烧录服务"
echo "3. 重启烧录服务"
echo "4. 查看服务状态"
echo "5. 查看服务日志"
echo "6. 禁用开机启动"
echo "7. 启用开机启动"

read -p "请选择操作 [1-7]: " choice

case $choice in
    1)
        sudo systemctl start fly-flash-auto.service
        echo "✅ 烧录服务已启动"
        ;;
    2)
        sudo systemctl stop fly-flash-auto.service
        echo "✅ 烧录服务已停止"
        ;;
    3)
        sudo systemctl restart fly-flash-auto.service
        echo "✅ 烧录服务已重启"
        ;;
    4)
        sudo systemctl status fly-flash-auto.service --no-pager
        ;;
    5)
        sudo journalctl -u fly-flash-auto.service -f
        ;;
    6)
        sudo systemctl disable fly-flash-auto.service
        echo "✅ 已禁用开机自动启动"
        ;;
    7)
        sudo systemctl enable fly-flash-auto.service
        echo "✅ 已启用开机自动启动"
        ;;
    *)
        echo "❌ 无效选择"
        ;;
esac