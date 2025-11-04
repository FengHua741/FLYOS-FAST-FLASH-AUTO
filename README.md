# FlyOS-FAST Flash Auto 自动烧录系统

## 项目简介

这是一个用于自动化烧录的完整解决方案，包含两个设备的协同工作：

- **设备A**：Web 状态服务器，提供实时状态监控界面，支持刷新和重置功能
- **设备B**：烧录设备，自动执行固件烧录流程，5秒关机倒计时，并实时上报状态

## 🚀 最新更新

### FlyOS-FAST
- ✅ 专为 FlyOS-FAST 系统
- ✅ 设备B所有文件集中在 `/data/FLYOS-FAST-FLASH-AUTO/Device_B` 目录
- ✅ 完整的 BL + HID 双阶段烧录流程
- ✅ 设备B HTTP 服务 (8082端口)
- ✅ 一键部署和验证脚本
- ✅ 完整的服务管理工具

## 系统架构

```
设备A (Web服务器)         设备B (烧录设备)
     │                         │
     ├─ 显示实时状态界面         ├─ 执行BL烧录 (DFU模式)
     ├─ 接收状态更新            ├─ 执行HID烧录  
     ├─ 提供刷新/重置功能       ├─ 上报状态到设备A
     ├─ 远程触发重新烧录        └─ HTTP服务(8082端口)
     └─ 提供Web访问界面              ├─ lsusb功能
                                     ├─ 重新烧录触发
                                     └─ 服务管理
```

## 📁 项目文件结构

```
fly-flash-system/
├── README.md                          # 项目说明文档（本文档）
├── Deployment_script/                 # 部署脚本目录
│   ├── deploy_all.sh                  # 一键部署脚本（自动检测设备类型）
│   ├── deploy_device_a.sh             # 设备A部署脚本
│   └── deploy_device_b.sh             # 设备B部署脚本
├── Device_A/                          # 设备A相关文件
│   ├── flash-web-server.py            # Web状态服务器脚本
│   ├── flash-web-server.service       # Web服务器systemd服务文件
│   └── templates/                     # HTML模板目录
│       ├── status.html               # 状态监控页面模板
│       └── tools.html                # 系统工具页面模板
├── Device_B/                          # 设备B相关文件
│   ├── device-b-server.py             # 设备B HTTP服务器
│   ├── deploy-device-b.sh             # 设备B一键部署脚本
│   ├── send-status.py                 # 状态上报脚本
│   ├── fly-flash-auto.sh              # 自动烧录主脚本
│   ├── service-control.sh             # 服务管理脚本
│   └── verify-deployment.sh           # 部署验证脚本
└── Utility_script/                    # 工具脚本目录
    ├── service_control.sh             # 服务管理脚本
    ├── monitor_status.sh              # 状态监控脚本
    └── test_connection.sh             # 连接测试脚本
```

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

### 2. 设置执行权限
```bash
chmod +x Deployment_script/*.sh
chmod +x Utility_script/*.sh
chmod +x Device_B/*.sh
chmod +x Device_B/*.py
```

### 3. 部署设备A (Web服务器)
```bash
./Deployment_script/deploy_device_a.sh
```

### 4. 部署设备B (烧录设备)
```bash
cd Device_B
./deploy-device-b.sh
```

### 5. 验证部署
```bash
./verify-deployment.sh
```

### 6. 开始监控
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

设备A运行Web状态服务器，提供实时监控界面。

**部署命令：**
```bash
./Deployment_script/deploy_device_a.sh
```

**特性：**
- HTML模板分离，便于维护
- 设备ID识别功能（串口和CAN设备）
- 状态页面自动刷新
- 远程触发设备B重新烧录

**访问地址：** `http://设备A-IP:8081`

### 设备B配置 (烧录设备)

设备B执行实际的烧录操作并上报状态。

**部署命令：**
```bash
cd Device_B
./deploy-device-b.sh
```

**部署脚本将自动完成：**
- 创建日志目录
- 设置脚本执行权限
- 安装 Python 依赖 (requests)
- 更新烧录命令和路径
- 创建 systemd 服务文件
- 启用并启动服务

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

设备B自动执行以下烧录步骤：

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

**设备A Web界面**
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
./service-control.sh
```

### 设备A Web界面功能
- **实时进度显示** - 显示当前烧录步骤和进度百分比
- **状态指示灯** - 彩色状态标识（等待/运行中/成功/错误）
- **实时日志** - 显示烧录过程的详细日志
- **刷新按钮** - 手动刷新页面获取最新状态
- **重置按钮** - 清空所有日志和进度，重置为初始状态
- **重新烧录按钮** - 远程触发设备B重新烧录

### 设备B Web界面功能
- **设备信息** - 显示设备B的IP地址和服务状态
- **USB设备检测** - 运行 `lsusb` 命令查看连接的USB设备
- **烧录控制** - 手动触发重新烧录流程
- **服务管理** - 检查系统服务状态

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

### 常见问题

1. **部署失败**
   - 检查脚本执行权限：`chmod +x *.sh *.py`
   - 确认在正确的目录运行部署脚本

2. **服务启动失败**
   - 检查 Python 依赖：`pip3 install requests`
   - 查看详细错误日志

3. **烧录过程异常**
   - 检查固件文件是否存在
   - 验证 `fly-flash` 工具可用性
   - 查看详细烧录日志

4. **网络连接失败**
   - 检查设备A和设备B的网络连通性
   - 确认设备A的8081端口和设备B的8082端口可访问
   - 验证IP地址配置是否正确

5. **状态上报失败**
   - 检查设备A的IP地址配置
   - 验证网络连接
   - 查看状态上报日志

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

2. **查看详细日志**
   ```bash
   ./service-control.sh
   # 选择选项 5 或 6 查看日志
   ```

3. **重新部署系统**
   ```bash
   # 设备A
   ./Deployment_script/deploy_device_a.sh
   
   # 设备B
   cd Device_B && ./deploy-device-b.sh
   ```

4. **检查网络连接**
   ```bash
   ping 192.168.101.239
   ```

---

**注意**: 本系统专为 FlyOS-FAST 系统设计，所有路径和配置均已针对该环境优化。设备B的所有文件都位于 `/data/FLYOS-FAST-FLASH-AUTO/Device_B` 目录下。