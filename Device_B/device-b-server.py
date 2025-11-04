def trigger_retry_flash(self):
    """触发重新烧录"""
    try:
        # 直接执行烧录脚本
        script_path = "/data/FLYOS-FAST-FLASH-AUTO/Device_B/fly-flash-auto.sh"
        
        # 使用nohup在后台执行，避免阻塞HTTP请求
        result = subprocess.run(
            ["nohup", "bash", script_path, "&"],
            capture_output=True, text=True, timeout=3
        )
        
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