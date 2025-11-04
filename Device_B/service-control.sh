#!/bin/bash
# FlyOS-FAST Flash Auto 服务管理脚本

BASE_DIR="/data/FLYOS-FAST-FLASH-AUTO/Device_B"
LOG_DIR="$BASE_DIR/logs"

show_menu() {
    echo "========================================"
    echo "  FlyOS-FAST Flash Auto 服务管理"
    echo "========================================"
    echo "1. 启动烧录服务"
    echo "2. 停止烧录服务"
    echo "3. 重启烧录服务"
    echo "4. 查看服务状态"
    echo "5. 查看服务日志"
    echo "6. 查看烧录日志"
    echo "7. 禁用开机启动"
    echo "8. 启用开机启动"
    echo "9. 重启 HTTP 服务"
    echo "0. 退出"
    echo "========================================"
}

start_service() {
    echo "启动烧录服务..."
    systemctl start fly-flash-auto.service
    echo "服务启动完成"
}

stop_service() {
    echo "停止烧录服务..."
    systemctl stop fly-flash-auto.service
    echo "服务停止完成"
}

restart_service() {
    echo "重启烧录服务..."
    systemctl restart fly-flash-auto.service
    echo "服务重启完成"
}

show_status() {
    echo "========================================"
    echo "服务状态:"
    echo "----------------------------------------"
    echo "fly-flash-auto.service:"
    systemctl status fly-flash-auto.service --no-pager
    echo "----------------------------------------"
    echo "device-b-http.service:"
    systemctl status device-b-http.service --no-pager
}

show_service_logs() {
    echo "========================================"
    echo "服务日志 (最近20行):"
    echo "----------------------------------------"
    echo "fly-flash-auto.service:"
    journalctl -u fly-flash-auto.service -n 20 --no-pager
    echo "----------------------------------------"
    echo "device-b-http.service:"
    journalctl -u device-b-http.service -n 20 --no-pager
}

show_flash_logs() {
    echo "========================================"
    echo "烧录日志 (最近20行):"
    echo "----------------------------------------"
    if [ -f "$LOG_DIR/fly-flash.log" ]; then
        tail -n 20 "$LOG_DIR/fly-flash.log"
    else
        echo "烧录日志文件不存在: $LOG_DIR/fly-flash.log"
    fi
}

disable_autostart() {
    echo "禁用开机启动..."
    systemctl disable fly-flash-auto.service
    systemctl disable device-b-http.service
    echo "开机启动已禁用"
}

enable_autostart() {
    echo "启用开机启动..."
    systemctl enable fly-flash-auto.service
    systemctl enable device-b-http.service
    echo "开机启动已启用"
}

restart_http_service() {
    echo "重启 HTTP 服务..."
    systemctl restart device-b-http.service
    echo "HTTP 服务重启完成"
}

# 主循环
while true; do
    show_menu
    read -p "请选择操作 [0-9]: " choice
    
    case $choice in
        1) start_service ;;
        2) stop_service ;;
        3) restart_service ;;
        4) show_status ;;
        5) show_service_logs ;;
        6) show_flash_logs ;;
        7) disable_autostart ;;
        8) enable_autostart ;;
        9) restart_http_service ;;
        0) echo "退出服务管理"; exit 0 ;;
        *) echo "无效选择，请重新输入" ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
    clear
done