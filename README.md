# Fly-Flash 自动烧录系统

## 项目简介

这是一个用于自动化烧录 Fly-C8P、Fly-C5、Fly-C5-V1.1自动烧录脚本，包含两个设备的协同工作：

- **设备A**：Web 状态服务器，提供实时状态监控界面
- **设备B**：烧录设备，自动执行固件烧录流程并上报状态

## 系统架构

```
设备A (Web服务器)         设备B (烧录设备)
     │                         │
     ├─ 显示实时状态界面         ├─ 执行DFU烧录
     ├─ 接收状态更新            ├─ 执行HID烧录  
     └─ 提供Web访问界面         └─ 上报状态到设备A
```

## 文件说明

### 核心文件
- `flash-web-server.py` - Web 状态服务器（设备A运行）
- `fly-flash-auto.py` - 主烧录脚本（设备B运行）
- `send-status.py` - 状态上报脚本（设备B运行）

### 服务配置
- `flash-web-server.service` - Web 服务器的 systemd 服务文件
- `fly-flash-auto.service` - 烧录服务的 systemd 服务文件

### 部署脚本
- `deploy_device_a.sh` - 设备A一键部署脚本
- `deploy_device_b.sh` - 设备B一键部署脚本
- `deploy_all.sh` - 自动检测设备类型的一键部署
- `test_connection.sh` - 设备间连接测试脚本
- `service_control.sh` - 服务管理脚本
- `monitor_status.sh` - 状态监控脚本

## 快速开始

### 1. 克隆仓库

#### 设备A
```bash
git clone https://github.com/FengHua741/FLYOS-FAST-FLASH-AUTO.git
cd FLYOS-FAST-FLASH-AUTO
```

#### 设备B
```bash
cd /data && git clone https://github.com/FengHua741/FLYOS-FAST-FLASH-AUTO.git
cd /data/FLYOS-FAST-FLASH-AUTO/
```


### 2. 给脚本添加执行权限
```bash
chmod +x *.sh
```

### 3. 部署设备A (Web服务器)
```bash
./deploy_device_a.sh
```

### 4. 部署设备B (烧录设备)
```bash
./deploy_device_b.sh
```

### 5. 测试连接
```bash
./test_connection.sh
```

### 6. 开始监控
```bash
./monitor_status.sh
```

## 详细部署流程

### 设备A配置 (Web服务器)
1. 运行 `./deploy_device_a.sh`
2. 脚本会自动：
   - 复制必要文件到系统目录
   - 设置执行权限
   - 配置并启动 systemd 服务
   - 验证服务状态

访问地址：`http://设备A-IP:8081`

### 设备B配置 (烧录设备)
1. 运行 `./deploy_device_b.sh`
2. 脚本会自动：
   - 安装系统依赖 (Python3, pip, requests)
   - 部署烧录脚本到系统目录
   - 配置 systemd 服务并启用开机启动

## 日常使用

### 启动烧录流程
设备B开机后会自动开始烧录流程，或在设备B上运行：
```bash
./service_control.sh
```
选择选项 1 启动服务

### 监控状态
在任意可访问设备A的设备上打开浏览器：
```
http://192.168.101.239:8081
```
或使用监控脚本：
```bash
./monitor_status.sh
```

### 服务管理
```bash
./service_control.sh
```
菜单选项：
- 启动/停止/重启服务
- 查看服务状态和日志
- 启用/禁用开机启动

## 烧录流程

系统自动执行以下步骤：
1. ✅ DFU 模式烧写引导程序
2. ✅ HID 模式烧写固件
3. ✅ USB 设备验证
4. ✅ 成功完成后自动关机

## 故障排除

### 查看日志
```bash
# 设备A Web服务器日志
sudo journalctl -u flash-web-server.service -f

# 设备B烧录服务日志
sudo journalctl -u fly-flash-auto.service -f

# 设备B详细烧录日志
tail -f /var/log/fly-flash.log
```

### 测试连接
```bash
./test_connection.sh
```

### 重新部署
```bash
# 设备A
./deploy_device_a.sh

# 设备B  
./deploy_device_b.sh
```

## 网络要求

- 设备A和设备B需要在同一局域网
- 设备A的 8081 端口需要开放访问
- 默认设备A IP: `192.168.101.239` (可在脚本中修改)

## 注意事项

- ⚠️ 首次部署请先手动测试烧录流程
- ⚠️ 确保烧录设备连接正常
- ⚠️ 烧录过程中不要断开电源或网络
- ⚠️ 成功完成后设备B会自动关机

## 更新日志

### v1.0
- 初始版本发布
- 支持自动DFU和HID烧录
- Web界面实时状态监控
- 一键部署脚本

## 技术支持

如有问题请检查：
1. 网络连接是否正常
2. 服务状态是否运行
3. 系统日志是否有错误信息
4. 设备间连接是否畅通

---

**提示**: 使用前请确保理解烧录流程，错误的操作可能导致设备损坏。