#!/bin/bash

# 配置
LOG_FILE="/var/log/fly-flash.log"
SERVER_URL="http://192.168.101.239:8081/update"

# 清空旧日志
echo "=== Fly-Flash 自动执行开始: $(date) ===" > $LOG_FILE

# 函数：发送状态到服务器
send_status() {
    local step="$1"
    local status="$2"
    local progress="$3"
    local message="$4"
    
    # 记录日志
    local log_msg="$(date '+%Y-%m-%d %H:%M:%S') - $message"
    echo "$log_msg" >> $LOG_FILE
    echo "$log_msg"
    
    # 发送到状态服务器
    python3 /etc/fly-flash/bin/send-status.py "$step" "$status" "$progress" "$log_msg"
}

# 函数：执行命令并发送状态
run_command() {
    local cmd="$1"
    local step="$2"
    local progress="$3"
    local success_pattern="$4"
    
    send_status "$step" "running" "$progress" "开始: $step"
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
        send_status "$step" "success" "$((progress+10))" "$step 完成"
        rm -f "$temp_file"
        return 0
    else
        send_status "$step" "error" "$progress" "$step 失败"
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
echo "   Fly-Flash 自动刷写程序 (网络版)"
echo "   开始时间: $(date)"
echo "   状态服务器: http://192.168.101.239:8081"
echo "========================================"

# 初始状态
send_status "initialization" "waiting" 0 "系统初始化" "$(get_device_info)"

# 第一步：DFU刷写
if run_command \
    "fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin" \
    "DFU模式刷写" \
    20 \
    "File downloaded successfully"; then
    
    send_status "dfu_complete" "success" 30 "DFU刷写完成，等待设备重置..."
    sleep 5
    
    # 第二步：HID刷写  
    if run_command \
        "fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin" \
        "HID模式刷写" \
        60 \
        "> Finish"; then
        
        send_status "hid_complete" "success" 80 "HID刷写完成，等待设备重置..."
        sleep 8
        
        # 第三步：设备验证
        send_status "device_verification" "running" 90 "验证USB设备"
        echo "检查USB设备..."
        usb_output=$(lsusb)
        echo "$usb_output"
        echo "$usb_output" >> $LOG_FILE
        
        if echo "$usb_output" | grep -q "1d50:614e"; then
            send_status "device_verification" "success" 100 "✅ 所有步骤完成！设备验证成功"
            echo ""
            echo "🎉 所有步骤完成！准备关机..."
            
            # 发送最终成功状态
            send_status "shutdown" "success" 100 "系统将在5秒后关机"
            
            # 🔄 更新：确保这里是5秒倒计时
            for i in {5..1}; do
                echo "关机倒计时: $i 秒 (按 Ctrl+C 取消)"
                sleep 1
            done
            
            echo "正在关机..."
            shutdown -h now
        else
            send_status "device_verification" "error" 90 "❌ 设备验证失败: 未找到目标设备"
            echo "错误: 未检测到设备 1d50:614e"
            echo "当前USB设备:"
            lsusb
        fi
    else
        send_status "hid_flash" "error" 60 "HID刷写失败"
    fi
else
    send_status "dfu_flash" "error" 20 "DFU刷写失败"
fi

echo ""
echo "========================================"
echo "   流程未完成"
echo "   查看详细日志: tail -f $LOG_FILE"
echo "   状态页面: http://192.168.101.239:8081"
echo "========================================"

# 发送最终错误状态
send_status "completed" "error" 100 "自动刷写流程未完成"