#!/bin/bash

# FlyOS-FAST Flash Auto 烧录脚本 - 简化直接执行版本
# 专为 FlyOS-FAST 系统设计，直接执行烧录命令组合

# 配置
LOG_FILE="/data/FLYOS-FAST-FLASH-AUTO/Device_B/logs/fly-flash.log"
SERVER_URL="http://192.168.101.239:8081/update"
SEND_STATUS_SCRIPT="/data/FLYOS-FAST-FLASH-AUTO/Device_B/send-status.py"

# ANSI 颜色代码过滤函数
filter_ansi_colors() {
    sed -r 's/\x1B\[[0-9;]*[mGK]//g' | sed 's/\r//g' | sed 's/\x1B//g' | tr -d '\000-\037'
}

# 清空旧日志
echo "=== Fly-Flash 自动执行开始: $(date) ===" > $LOG_FILE
echo "简化直接执行版本 - 执行完整命令组合" >> $LOG_FILE

# 函数：发送状态到服务器（简化版本）
send_status_simple() {
    local step="$1"
    local status="$2"
    local progress="$3"
    local message="$4"
    
    # 过滤颜色代码
    local clean_message=$(echo "$message" | filter_ansi_colors)
    
    # 记录日志
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_msg="$timestamp - $clean_message"
    echo "$log_msg" >> $LOG_FILE
    
    # 尝试发送状态（单次尝试，不重试）
    python3 $SEND_STATUS_SCRIPT "$step" "$status" "$progress" "$log_msg" || true
}

# 函数：实时执行命令并记录日志（简化版本）
execute_and_log() {
    local cmd="$1"
    local step="$2"
    
    echo "执行命令: $cmd" >> $LOG_FILE
    echo "----------------------------------------" >> $LOG_FILE
    
    # 发送开始状态
    send_status_simple "$step" "running" "50" "开始执行: $step"
    
    # 创建命名管道用于实时读取输出
    local pipe_file=$(mktemp -u)
    mkfifo "$pipe_file"
    
    # 执行命令并将输出重定向到命名管道
    eval "$cmd" > "$pipe_file" 2>&1 &
    local cmd_pid=$!
    
    # 从命名管道逐行读取输出并记录
    while IFS= read -r line; do
        # 过滤颜色代码
        clean_line=$(echo "$line" | filter_ansi_colors)
        
        # 记录到日志文件
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$timestamp - $clean_line" >> $LOG_FILE
        
        # 尝试实时上报日志行（不保证成功）
        python3 $SEND_STATUS_SCRIPT "$step" "running" "50" "$clean_line" || true
        
    done < "$pipe_file"
    
    # 等待命令完成
    wait $cmd_pid
    local exit_code=$?
    
    # 清理命名管道
    rm -f "$pipe_file"
    
    return $exit_code
}

# 主程序
echo "========================================"
echo "   Fly-Flash 自动刷写程序 (FlyOS-FAST)"
echo "   简化直接执行版本"
echo "   开始时间: $(date)"
echo "   状态服务器: http://192.168.101.239:8081"
echo "========================================"

# 记录到日志文件
{
    echo "========================================"
    echo "   Fly-Flash 自动刷写程序 (FlyOS-FAST)"
    echo "   简化直接执行版本"
    echo "   开始时间: $(date)"
    echo "   状态服务器: http://192.168.101.239:8081"
    echo "========================================"
} >> $LOG_FILE

# 发送初始状态（尝试发送，不保证成功）
send_status_simple "system_start" "running" 0 "系统启动 - 简化直接执行版本"

# 定义完整的命令组合
FULL_COMMAND="fly-flash -d auto -u -f /usr/lib/firmware/bootloader/hid_bootloader_h723_v1.0.bin && fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin && lsusb && poweroff"

# 执行完整的命令组合
echo "开始执行完整命令组合..." >> $LOG_FILE
send_status_simple "full_flash_process" "running" 25 "开始执行完整烧录流程"

if execute_and_log "$FULL_COMMAND" "full_flash_process"; then
    echo "命令组合执行成功，设备已关机" >> $LOG_FILE
    send_status_simple "completed" "success" 100 "所有命令执行成功，设备已关机"
else
    echo "命令组合执行失败，退出码: $?" >> $LOG_FILE
    send_status_simple "completed" "error" 100 "命令执行失败，请检查日志"
    
    # 即使失败也记录当前USB状态
    echo "当前USB设备状态:" >> $LOG_FILE
    lsusb >> $LOG_FILE
    
    echo ""
    echo "========================================"
    echo "   命令执行失败"
    echo "   查看详细日志: tail -f $LOG_FILE"
    echo "   状态页面: http://192.168.101.239:8081"
    echo "   可以通过设备A重新触发烧录"
    echo "========================================"
fi