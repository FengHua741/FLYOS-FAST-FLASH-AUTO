#!/bin/bash

# FlyOS-FAST Flash Auto 烧录脚本 - 实时日志流版本（修复ANSI颜色代码）
# 专为 FlyOS-FAST 系统设计，支持逐行实时日志上报

# 配置
LOG_FILE="/data/FLYOS-FAST-FLASH-AUTO/Device_B/logs/fly-flash.log"
SERVER_URL="http://192.168.101.239:8081/update"
SEND_STATUS_SCRIPT="/data/FLYOS-FAST-FLASH-AUTO/Device_B/send-status.py"

# ANSI 颜色代码过滤函数
filter_ansi_colors() {
    # 过滤 ANSI 颜色代码和控制字符
    sed -r 's/\x1B\[[0-9;]*[mGK]//g' | sed 's/\r//g' | sed 's/\x1B//g' | tr -d '\000-\037'
}

# 清空旧日志
echo "=== Fly-Flash 自动执行开始: $(date) ===" > $LOG_FILE
echo "实时日志流版本 - 支持逐行上报" >> $LOG_FILE

# 函数：发送状态到服务器（带重试）
send_status_with_retry() {
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
    
    # 发送到状态服务器（最多重试2次）
    local retry_count=0
    local max_retries=2
    
    while [ $retry_count -le $max_retries ]; do
        if python3 $SEND_STATUS_SCRIPT "$step" "$status" "$progress" "$log_msg"; then
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -le $max_retries ]; then
                echo "状态上报失败，重试中... ($retry_count/$max_retries)" >> $LOG_FILE
                sleep 1
            fi
        fi
    done
    
    echo "状态上报失败，跳过此状态" >> $LOG_FILE
    return 1
}

# 函数：实时执行命令并逐行上报日志
run_command_realtime() {
    local cmd="$1"
    local step="$2"
    local progress="$3"
    local success_pattern="$4"
    
    # 发送开始状态
    send_status_with_retry "$step" "running" "$progress" "开始执行: $step"
    echo "执行命令: $cmd" >> $LOG_FILE
    echo "----------------------------------------" >> $LOG_FILE
    
    # 创建命名管道用于实时读取输出
    local pipe_file=$(mktemp -u)
    mkfifo "$pipe_file"
    
    # 执行命令并将输出重定向到命名管道
    eval "$cmd" > "$pipe_file" 2>&1 &
    local cmd_pid=$!
    
    # 从命名管道逐行读取输出并实时上报
    local line_count=0
    local success_found=0
    
    while IFS= read -r line; do
        # 过滤颜色代码
        clean_line=$(echo "$line" | filter_ansi_colors)
        
        # 记录到日志文件
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$timestamp - $clean_line" >> $LOG_FILE
        
        # 实时上报日志行（使用过滤后的内容）
        python3 $SEND_STATUS_SCRIPT "$step" "running" "$progress" "$clean_line" || true
        
        # 检查成功模式（使用原始行进行模式匹配）
        if [[ $line == *"$success_pattern"* ]]; then
            success_found=1
        fi
        
        line_count=$((line_count + 1))
        
        # 每10行更新一次进度（避免过于频繁的上报）
        if [ $((line_count % 10)) -eq 0 ]; then
            send_status_with_retry "$step" "running" "$progress" "执行中... 已处理 $line_count 行输出"
        fi
        
    done < "$pipe_file"
    
    # 等待命令完成
    wait $cmd_pid
    local exit_code=$?
    
    # 清理命名管道
    rm -f "$pipe_file"
    
    # 检查命令执行结果
    if [ $exit_code -eq 0 ] && [ $success_found -eq 1 ]; then
        send_status_with_retry "$step" "success" "$((progress+10))" "$step 完成 - 成功模式匹配: $success_pattern"
        return 0
    else
        send_status_with_retry "$step" "error" "$progress" "$step 失败 - 退出码: $exit_code, 成功模式匹配: $success_found"
        return 1
    fi
}

# 函数：获取设备信息
get_device_info() {
    local device_info=$(lsusb | grep -E "1d50:614e|0483:df11" | head -1)
    echo "$device_info"
}

# 函数：检查网络连接（后台运行）
check_network_connectivity() {
    echo "检查网络连接..." >> $LOG_FILE
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if ping -c 1 -W 2 192.168.101.239 &> /dev/null; then
            echo "网络连接正常 (尝试 $attempt/$max_attempts)" >> $LOG_FILE
            return 0
        else
            echo "网络连接检查中... ($attempt/$max_attempts)" >> $LOG_FILE
            sleep 2
            ((attempt++))
        fi
    done
    
    echo "网络连接可能不稳定，继续执行但状态上报可能延迟" >> $LOG_FILE
    return 1
}

# 主程序
echo "========================================"
echo "   Fly-Flash 自动刷写程序 (FlyOS-FAST)"
echo "   实时日志流版本"
echo "   开始时间: $(date)"
echo "   状态服务器: http://192.168.101.239:8081"
echo "========================================"

# 记录到日志文件
{
    echo "========================================"
    echo "   Fly-Flash 自动刷写程序 (FlyOS-FAST)"
    echo "   实时日志流版本"
    echo "   开始时间: $(date)"
    echo "   状态服务器: http://192.168.101.239:8081"
    echo "========================================"
} >> $LOG_FILE

# 立即发送初始状态
send_status_with_retry "system_start" "running" 0 "系统启动 - 实时日志流版本"

# 在后台检查网络连接
check_network_connectivity &

# 初始状态
send_status_with_retry "initialization" "waiting" 5 "系统初始化" "$(get_device_info)"

# 第一步：BL烧录 (DFU模式)
if run_command_realtime \
    "fly-flash -d auto -u -f /usr/lib/firmware/bootloader/hid_bootloader_h723_v1.0.bin" \
    "BL烧录" \
    20 \
    "File downloaded successfully"; then
    
    send_status_with_retry "bl_complete" "success" 30 "BL烧录完成，等待设备重置..."
    sleep 5
    
    # 第二步：HID烧录  
    if run_command_realtime \
        "fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin" \
        "HID烧录" \
        60 \
        "> Finish"; then
        
        send_status_with_retry "hid_complete" "success" 80 "HID烧录完成，等待设备重置..."
        sleep 8
        
        # 第三步：设备验证
        send_status_with_retry "device_verification" "running" 90 "验证USB设备"
        echo "检查USB设备..." >> $LOG_FILE
        
        # 实时检查USB设备 - 增加到30次检查（60秒）
        local usb_check_count=0
        local max_usb_checks=30
        local device_found=0
        
        while [ $usb_check_count -lt $max_usb_checks ] && [ $device_found -eq 0 ]; do
            usb_output=$(lsusb)
            clean_usb_output=$(echo "$usb_output" | filter_ansi_colors)
            echo "$clean_usb_output" >> $LOG_FILE
            
            # 实时上报USB检查结果
            python3 $SEND_STATUS_SCRIPT "device_verification" "running" "90" "USB设备检查 $((usb_check_count + 1))/$max_usb_checks: $clean_usb_output" || true
            
            if echo "$usb_output" | grep -q "1d50:614e"; then
                device_found=1
                send_status_with_retry "device_verification" "success" 100 "设备验证成功 - 检测到目标设备 1d50:614e"
                
                echo ""
                echo "所有步骤完成！立即关机..."
                echo "所有步骤完成！立即关机..." >> $LOG_FILE
                
                # 发送最终成功状态
                send_status_with_retry "shutdown" "success" 100 "所有步骤完成！系统立即关机"
                
                echo "正在关机..." >> $LOG_FILE
                # 立即关机，不等待
                shutdown -h now
                exit 0
            else
                usb_check_count=$((usb_check_count + 1))
                sleep 2
            fi
        done
        
        if [ $device_found -eq 0 ]; then
            send_status_with_retry "device_verification" "error" 90 "设备验证失败: 未找到目标设备 1d50:614e"
            echo "错误: 未检测到设备 1d50:614e" >> $LOG_FILE
            echo "当前USB设备:" >> $LOG_FILE
            lsusb >> $LOG_FILE
        fi
    else
        send_status_with_retry "hid_flash" "error" 60 "HID烧录失败"
    fi
else
    send_status_with_retry "bl_flash" "error" 20 "BL烧录失败"
fi

echo ""
echo "========================================"
echo "   流程未完成"
echo "   查看详细日志: tail -f $LOG_FILE"
echo "   状态页面: http://192.168.101.239:8081"
echo "========================================"

# 记录到日志文件
{
    echo ""
    echo "========================================"
    echo "   流程未完成"
    echo "   最后检查时间: $(date)"
    echo "========================================"
} >> $LOG_FILE

# 发送最终错误状态
send_status_with_retry "completed" "error" 100 "自动烧录流程未完成"