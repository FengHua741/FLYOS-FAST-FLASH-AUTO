#!/bin/bash

# FlyOS-FAST Flash Auto 烧录脚本 - 优化版
# 专为 FlyOS-FAST 系统设计

# 配置
LOG_FILE="/data/FLYOS-FAST-FLASH-AUTO/Device_B/logs/fly-flash.log"
SERVER_URL="http://192.168.101.239:8081/update"
SEND_STATUS_SCRIPT="/data/FLYOS-FAST-FLASH-AUTO/Device_B/send-status.py"

# 清空旧日志
echo "=== Fly-Flash 自动执行开始: $(date) ===" > $LOG_FILE

# 函数：检查网络连接
check_network_connectivity() {
    echo "检查网络连接..."
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if ping -c 1 -W 2 192.168.101.239 &> /dev/null; then
            echo "✅ 网络连接正常 (尝试 $attempt/$max_attempts)"
            return 0
        else
            echo "⏳ 网络连接检查中... ($attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    echo "⚠️ 网络连接可能不稳定，继续执行但状态上报可能延迟"
    return 1
}

# 函数：发送状态到服务器（带重试）
send_status_with_retry() {
    local step="$1"
    local status="$2"
    local progress="$3"
    local message="$4"
    
    # 记录日志
    local log_msg="$(date '+%Y-%m-%d %H:%M:%S') - $message"
    echo "$log_msg" >> $LOG_FILE
    echo "$log_msg"
    
    # 发送到状态服务器（最多重试2次）
    local retry_count=0
    local max_retries=2
    
    while [ $retry_count -le $max_retries ]; do
        if python3 $SEND_STATUS_SCRIPT "$step" "$status" "$progress" "$log_msg"; then
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -le $max_retries ]; then
                echo "状态上报失败，重试中... ($retry_count/$max_retries)"
                sleep 1
            fi
        fi
    done
    
    echo "❌ 状态上报失败，跳过此状态"
    return 1
}

# 函数：执行命令并发送状态
run_command() {
    local cmd="$1"
    local step="$2"
    local progress="$3"
    local success_pattern="$4"
    
    send_status_with_retry "$step" "running" "$progress" "开始: $step"
    echo "执行: $cmd"
    echo "----------------------------------------"
    
    # 临时文件用于存储命令输出
    local temp_file=$(mktemp)
    
    # 执行命令并同时输出到终端和文件
    if eval "$cmd" 2>&1 | tee "$temp_file" | while IFS= read -r line; do
        echo "$line"
        echo "$line" >> $LOG_FILE
    done; then
        local exit_code=0
    else
        local exit_code=1
    fi
    
    # 检查命令输出是否包含成功模式
    if [ $exit_code -eq 0 ] && grep -q "$success_pattern" "$temp_file"; then
        send_status_with_retry "$step" "success" "$((progress+10))" "$step 完成"
        rm -f "$temp_file"
        return 0
    else
        send_status_with_retry "$step" "error" "$progress" "$step 失败"
        rm -f "$temp_file"
        return 1
    fi
}

# 获取设备信息
get_device_info() {
    local device_info=$(lsusb | grep -E "1d50:614e|0483:df11" | head -1)
    echo "$device_info"
}

# 主程序
echo "========================================"
echo "   Fly-Flash 自动刷写程序 (FlyOS-FAST)"
echo "   开始时间: $(date)"
echo "   状态服务器: http://192.168.101.239:8081"
echo "========================================"

# 立即发送初始状态（不等待网络检查）
send_status_with_retry "system_start" "running" 0 "系统启动"

# 检查网络连接（在后台进行，不阻塞主流程）
check_network_connectivity &

# 初始状态
send_status_with_retry "initialization" "waiting" 5 "系统初始化" "$(get_device_info)"

# 第一步：BL烧录 (DFU模式)
if run_command \
    "fly-flash -d auto -u -f /usr/lib/firmware/bootloader/hid_bootloader_h723_v1.0.bin" \
    "BL烧录" \
    20 \
    "File downloaded successfully"; then
    
    send_status_with_retry "bl_complete" "success" 30 "BL烧录完成，等待设备重置..."
    sleep 5
    
    # 第二步：HID烧录  
    if run_command \
        "fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin" \
        "HID烧录" \
        60 \
        "> Finish"; then
        
        send_status_with_retry "hid_complete" "success" 80 "HID烧录完成，等待设备重置..."
        sleep 8
        
        # 第三步：设备验证
        send_status_with_retry "device_verification" "running" 90 "验证USB设备"
        echo "检查USB设备..."
        usb_output=$(lsusb)
        echo "$usb_output"
        echo "$usb_output" >> $LOG_FILE
        
        if echo "$usb_output" | grep -q "1d50:614e"; then
            send_status_with_retry "device_verification" "success" 100 "✅ 所有步骤完成！设备验证成功"
            echo ""
            echo "🎉 所有步骤完成！准备关机..."
            
            # 发送最终成功状态
            send_status_with_retry "shutdown" "success" 100 "系统将在5秒后关机"
            
            # 5秒倒计时
            for i in {5..1}; do
                echo "关机倒计时: $i 秒 (按 Ctrl+C 取消)"
                sleep 1
            done
            
            echo "正在关机..."
            shutdown -h now
            exit 0
        else
            send_status_with_retry "device_verification" "error" 90 "❌ 设备验证失败: 未找到目标设备"
            echo "错误: 未检测到设备 1d50:614e"
            echo "当前USB设备:"
            lsusb
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

# 发送最终错误状态
send_status_with_retry "completed" "error" 100 "自动烧录流程未完成"