# FlyOS-FAST Flash Auto 自动烧录系统

## 🚀 项目简介

这是一个专为 FlyOS-FAST 系统设计的自动化烧录完整解决方案，包含两个设备的协同工作：

- **设备A**：Web 状态服务器，提供实时状态监控界面，支持智能轮询和完整日志显示
- **设备B**：烧录设备，自动执行固件烧录流程，支持实时日志流上报

## ✨ 最新特性

### 🆕 实时日志流系统
- ✅ 设备B逐行实时上报烧录日志
- ✅ 设备A实时显示完整烧录过程
- ✅ 支持所有历史日志查看

### 🆕 智能轮询机制
- ✅ 10秒基础轮询间隔，降低服务器压力
- ✅ 检测到步骤变化时立即刷新
- ✅ 网络状态实时显示，无弹窗干扰

### 🆕 现代化复制功能
- ✅ 使用 Clipboard API 重写复制功能
- ✅ 完美支持 Win系统 Edge/Chrome 浏览器
- ✅ 智能错误处理和用户反馈

### 🆕 优化系统架构
- ✅ 统一文件结构，消除重复文件
- ✅ 集中化管理脚本
- ✅ 简化部署流程

## 🏗️ 系统架构

```
设备A (Web服务器)         设备B (烧录设备)
     │                         │
     ├─ 智能轮询状态监控         ├─ 实时日志流上报
     ├─ 完整历史日志显示         ├─ 逐行实时日志输出
     ├─ 现代化复制工具          ├─ 自动BL+HID烧录
     ├─ 远程重新烧录触发        ├─ 设备验证和关机
     └─ Web访问界面(8081)       └─ HTTP服务(8082)
```

## 📁 项目文件结构

```
FLYOS-FAST-FLASH-AUTO/
├── README.md                          # 项目说明文档（本文档）
├── Deployment_script/                 # 部署脚本目录
│   ├── deploy_all.sh                  # 一键部署脚本（自动检测设备类型）
│   └── deploy_device_a.sh             # 设备A部署脚本
├── Device_A/                          # 设备A相关文件
│   ├── flash-web-server.py            # Web状态服务器脚本（实时日志接收）
│   ├── flash-web-server.service       # Web服务器systemd服务文件
│   └── templates/                     # HTML模板目录
│       ├── status.html               # 状态监控页面（智能轮询）
│       └── tools.html                # 系统工具页面（修复复制功能）
└── Device_B/                          # 设备B相关文件（所有功能集中）
    ├── device-b-server.py             # 设备B HTTP服务器
    ├── deploy-device-b.sh             # 设备B一键部署脚本
    ├── send-status.py                 # 状态上报脚本（实时日志上报）
    ├── fly-flash-auto.sh              # 自动烧录主脚本（实时日志流）
    ├── service-control.sh             # 服务管理脚本
    ├── verify-deployment.sh           # 部署验证脚本
    ├── monitor_status.sh              # 状态监控脚本
    ├── test_connection.sh             # 连接测试脚本
    └── logs/                          # 日志目录
        └── fly-flash.log              # 烧录日志文件
```

## 🚀 快速开始

### 1. 克隆仓库

#### 设备A（Web服务器）
```bash
cd && rm -rf ~/FLYOS-FAST-FLASH-AUTO
git clone https://github.com/FengHua741/FLYOS-FAST-FLASH-AUTO.git
cd FLYOS-FAST-FLASH-AUTO
chmod +x Deployment_script/*.sh
chmod +x Device_A/flash-web-server.py
./Deployment_script/deploy_device_a.sh
```

#### 设备B（烧录设备）
```bash
rm -rf /data//FLYOS-FAST-FLASH-AUTO
cd /data && git clone https://github.com/FengHua741/FLYOS-FAST-FLASH-AUTO.git
cd /data/FLYOS-FAST-FLASH-AUTO/Device_B
chmod +x deploy-device-b.sh
./deploy-device-b.sh
```

### 3. 验证部署
```bash
cd Device_B
./verify-deployment.sh
```

### 4. 开始监控
访问设备A的Web界面：
```
http://192.168.101.239:8081
```

访问设备B的Web界面：
```
http://<设备B-IP>:8082
```

## 🔧 详细部署指南

### 设备A配置 (Web服务器)

设备A运行Web状态服务器，提供智能轮询监控界面。

**部署命令：**
```bash
./Deployment_script/deploy_device_a.sh
```

**新特性：**
- 智能轮询（10秒间隔 + 步骤变化检测）
- 完整实时日志流显示
- 现代化复制功能
- 连接状态实时显示

**访问地址：** `http://设备A-IP:8081`

### 设备B配置 (烧录设备)

设备B执行实时烧录操作并逐行上报日志。

**部署命令：**
```bash
cd Device_B
./deploy-device-b.sh
```

**新特性：**
- 逐行实时日志上报
- 流式烧录过程监控
- 优化的网络重连机制

**验证部署：**
```bash
./verify-deployment.sh
```

**日常管理：**
```bash
./service-control.sh
```

**访问地址：** `http://设备B-IP:8082`

## 🎯 烧录流程

设备B自动执行以下烧录步骤，并实时上报每行日志：

1. **BL烧录 (DFU模式)**
   - 执行命令：`fly-flash -d auto -u -f /usr/lib/firmware/bootloader/hid_bootloader_h723_v1.0.bin`
   - 成功标志：`File downloaded successfully`
   - 进度：20%

2. **HID烧录**
   - 执行命令：`fly-flash -d auto -h -f /usr/lib/firmware/klipper/stm32h723-128k-usb.bin`
   - 成功标志：`> Finish`
   - 进度：60%

3. **设备验证**
   - 执行命令：`lsusb`
   - 成功标志：检测到 `1d50:614e` 设备
   - 进度：90%

4. **自动关机**
   - 成功完成后5秒倒计时关机
   - 按 Ctrl+C 可取消关机
   - 进度：100%

## 🛠️ 日常使用

### 启动烧录流程
设备B开机后会自动开始烧录流程，或通过以下方式手动触发：

**方法1：设备B Web界面**
```
http://<设备B-IP>:8082
```

**方法2：服务管理**
```bash
cd /data/FLYOS-FAST-FLASH-AUTO/Device_B
./service-control.sh
```

### 监控状态

**设备A Web界面**（推荐）
在浏览器中访问设备A的地址：
```
http://192.168.101.239:8081
```

**设备B Web界面**
在浏览器中访问设备B的地址：
```
http://<设备B-IP>:8082
```

**命令行监控**
```bash
cd /data/FLYOS-FAST-FLASH-AUTO/Device_B
./monitor_status.sh
```

### 设备A Web界面功能
- **智能轮询显示** - 10秒自动刷新，步骤变化立即刷新
- **实时日志流** - 显示完整的烧录过程日志
- **状态指示灯** - 彩色状态标识（等待/运行中/成功/错误）
- **连接状态** - 实时网络连接状态显示
- **刷新按钮** - 手动刷新页面获取最新状态
- **重置按钮** - 清空所有日志和进度，重置为初始状态
- **重新烧录按钮** - 远程触发设备B重新烧录

### 设备B Web界面功能
- **设备信息** - 显示设备B的IP地址和服务状态
- **USB设备检测** - 运行 `lsusb` 命令查看连接的USB设备
- **烧录控制** - 手动触发重新烧录流程
- **服务管理** - 检查系统服务状态

### 系统工具功能
访问 `http://192.168.101.239:8081/tools` 使用：
- **设备搜索** - USB设备和CAN设备搜索
- **命令复制** - 现代化复制功能，支持所有浏览器
- **系统命令** - 常用系统命令快速执行

### 服务管理功能
通过 `service-control.sh` 可以：
- 启动/停止/重启烧录服务
- 查看服务状态和日志
- 管理开机启动设置
- 重启 HTTP 服务

## 🔍 故障排除

### 查看日志

**设备A Web服务器日志：**
```bash
sudo journalctl -u flash-web-server.service -f
```

**设备B HTTP服务日志：**
```bash
sudo journalctl -u device-b-http.service -f
```

**设备B烧录服务日志：**
```bash
sudo journalctl -u fly-flash-auto.service -f
```

**设备B详细烧录日志：**
```bash
tail -f /data/FLYOS-FAST-FLASH-AUTO/Device_B/logs/fly-flash.log
```

### 系统验证

**设备B验证：**
```bash
cd /data/FLYOS-FAST-FLASH-AUTO/Device_B
./verify-deployment.sh
```

**连接测试：**
```bash
./test_connection.sh
```

### 常见问题

1. **复制功能失效**
   - 确保使用现代浏览器（Chrome/Edge/Firefox）
   - 检查浏览器控制台错误信息

2. **日志不显示**
   - 检查设备B网络连接
   - 验证设备A和设备B的IP配置
   - 查看设备B的烧录日志文件

3. **服务启动失败**
   - 检查 Python 依赖：`pip3 install requests`
   - 查看详细错误日志

4. **网络连接问题**
   - 运行 `./test_connection.sh` 测试连接
   - 检查防火墙设置
   - 验证IP地址配置

### 重新部署

**设备A重新部署：**
```bash
./Deployment_script/deploy_device_a.sh
```

**设备B重新部署：**
```bash
cd /data/FLYOS-FAST-FLASH-AUTO/Device_B
./deploy-device-b.sh
```

## ⚙️ 网络配置

- **设备A IP**: `192.168.101.239` (可在脚本中修改)
- **设备A端口**: `8081`
- **设备B端口**: `8082`
- **网络要求**: 设备A和设备B需要在同一局域网
- **IP获取**: 设备B使用 DHCP 自动获取IP

## 📞 技术支持

如果遇到问题，按以下步骤排查：

1. **运行验证脚本**
   ```bash
   cd /data/FLYOS-FAST-FLASH-AUTO/Device_B
   ./verify-deployment.sh
   ```

2. **测试网络连接**
   ```bash
   ./test_connection.sh
   ```

3. **查看详细日志**
   ```bash
   ./service-control.sh
   # 选择选项 5 或 6 查看日志
   ```

4. **重新部署系统**
   ```bash
   # 设备A
   ./Deployment_script/deploy_device_a.sh
   
   # 设备B
   cd Device_B && ./deploy-device-b.sh
   ```
