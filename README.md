# Fly-Flash 自动烧录系统

## 项目简介

这是一个用于自动化烧录，包含两个设备的协同工作：

- **设备A**：Web 状态服务器，提供实时状态监控界面，支持刷新和重置功能
- **设备B**：烧录设备，自动执行固件烧录流程，5秒关机倒计时，并实时上报状态

## 🚀 最新更新

### v2.0 更新内容
- ✅ HTML模板从Python代码中分离
- ✅ 导航顺序调整为系统工具在前
- ✅ 设备ID识别功能（串口和CAN设备）
- ✅ 修复复制按钮兼容性问题
- ✅ 状态监控页面每秒自动刷新
- ✅ 设备B IP地址上报
- ✅ 设备B HTTP服务（8082端口）
- ✅ 设备A远程触发设备B重新烧录

## 系统架构

```
设备A (Web服务器)         设备B (烧录设备)
     │                         │
     ├─ 显示实时状态界面         ├─ 执行DFU烧录
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
│   ├── fly-flash-auto.sh              # 主烧录脚本（5秒关机版本）
│   ├── fly-flash-auto.service         # 烧录服务systemd服务文件
│   ├── send-status.py                 # 状态上报脚本（含IP地址）
│   ├── device-b-server.py             # 设备B HTTP服务器
│   ├── device-b-http.service          # 设备B HTTP服务systemd文件
│   └── deploy-device-b-http.sh        # 设备B HTTP服务部署脚本
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
chmod +x Device_B/deploy-device-b-http.sh
```

### 3. 部署设备A (Web服务器)
```bash
./Deployment_script/deploy_device_a.sh
```

### 4. 部署设备B (烧录设备)
```bash
# 部署烧录服务
./Deployment_script/deploy_device_b.sh

# 部署HTTP服务
./Device_B/deploy-device-b-http.sh
```

### 5. 测试连接
```bash
./Utility_script/test_connection.sh
```

### 6. 开始监控
访问设备A的Web界面：
```
http://192.168.101.239:8081
```

访问设备B的Web界面：
```
http://设备B-IP:8082
```

## 🔧 详细部署指南

### 设备A配置 (Web服务器)

设备A运行Web状态服务器，提供实时监控界面。

**部署命令：**
```bash
./Deployment_script/deploy_device_a.sh
```

**新特性：**
- HTML模板分离，便于维护
- 导航顺序：系统工具在前，状态监控在后
- 设备ID识别功能：
  - 串口设备：自动添加`serial:`前缀
  - CAN设备：提取`canbus_uuid`并格式化
- 兼容性更好的复制功能
- 状态页面每秒自动刷新

**访问地址：** `http://设备A-IP:8081`

### 设备B配置 (烧录设备)

设备B执行实际的烧录操作并上报状态。

**部署命令：**
```bash
# 部署烧录服务
./Deployment_script/deploy_device_b.sh

# 部署HTTP服务
./Device_B/deploy-device-b-http.sh
```

**新特性：**
- 状态上报包含设备B的IP地址
- 独立的HTTP服务（8082端口）
- Web界面提供lsusb功能
- 支持远程重新烧录触发
- 服务管理功能

**访问地址：** `http://设备B-IP:8082`

## 🎯 烧录流程

系统自动执行以下步骤：

1. **DFU模式烧写** - 烧写引导程序
   - 执行命令：`fly-flash -d auto -u -f /usr/lib/firmware/bootloader/hid_bootloader_h723_v1.0.bin`
   - 成功标志：`File downloaded successfully`

2. **HID模式烧写** - 烧写固件
   - 执行命令：`fly-flash -d auto -h -f /usr/lib/firmware/klipper-h723-128k-usb.bin`
   - 成功标志：`> Finish`

3. **USB设备验证** - 确认设备识别
   - 执行命令：`lsusb`
   - 成功标志：检测到 `1d50:614e` 设备

4. **自动关机** - 完成所有步骤后5秒倒计时关机

## 🛠️ 日常使用

### 启动烧录流程
设备B开机后会自动开始烧录流程，或手动启动：
```bash
./Utility_script/service_control.sh
```
选择选项 1 启动服务

### 监控状态
**方法1：Web界面 - 设备A**
在浏览器中访问设备A的地址：
```
http://192.168.101.239:8081
```

**方法2：Web界面 - 设备B**
在浏览器中访问设备B的地址：
```
http://设备B-IP:8082
```

**方法3：命令行监控**
```bash
./Utility_script/monitor_status.sh
```

### 设备A Web界面功能
- **实时进度显示** - 显示当前烧录步骤和进度百分比
- **状态指示灯** - 彩色状态标识（等待/运行中/成功/错误）
- **实时日志** - 显示烧录过程的详细日志
- **刷新按钮** - 手动刷新页面获取最新状态
- **重置按钮** - 清空所有日志和进度，重置为初始状态
- **重新烧录按钮** - 远程触发设备B重新烧录（仅在错误状态显示）

### 设备B Web界面功能
- **设备信息** - 显示设备B的IP地址和服务状态
- **USB设备检测** - 运行lsusb命令查看连接的USB设备
- **烧录控制** - 手动触发重新烧录流程
- **服务管理** - 重启烧录服务、检查服务状态

### 系统工具功能
- **设备搜索**：
  - USB设备搜索 (lsusb)
  - 设备ID搜索 (串口和CAN设备)
- **文档指令** - 常用文档相关命令
- **设备指令** - 设备识别和管理命令
- **系统指令** - 系统配置和诊断命令

### 服务管理
```bash
./Utility_script/service_control.sh
```

**菜单选项：**
- 1 - 启动烧录服务
- 2 - 停止烧录服务  
- 3 - 重启烧录服务
- 4 - 查看服务状态
- 5 - 查看服务日志
- 6 - 禁用开机启动
- 7 - 启用开机启动

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
tail -f /var/log/fly-flash.log
```

### 测试连接
```bash
./Utility_script/test_connection.sh
```

### 常见问题

1. **复制按钮不工作**
   - 确保使用兼容的浏览器
   - 检查浏览器控制台是否有错误信息
   - 使用系统工具页面测试复制功能

2. **设备ID识别异常**
   - 检查串口设备连接状态
   - 验证CAN总线配置
   - 查看命令执行输出

3. **重新烧录失败**
   - 检查设备B的HTTP服务状态
   - 验证网络连通性
   - 查看设备B的服务日志

4. **连接失败**
   - 检查设备A和设备B的网络连通性
   - 确认设备A的8081端口和设备B的8082端口在防火墙中开放
   - 验证IP地址配置是否正确

5. **服务启动失败**
   - 检查脚本执行权限
   - 验证Python依赖：`pip3 install requests`
   - 查看systemd服务状态

6. **烧录过程异常**
   - 检查USB设备连接
   - 验证固件文件路径是否正确
   - 查看详细日志定位问题

### 重新部署
```bash
# 设备A重新部署
./Deployment_script/deploy_device_a.sh

# 设备B重新部署  
./Deployment_script/deploy_device_b.sh
./Device_B/deploy-device-b-http.sh
```

## ⚙️ 网络配置

- **设备A IP**: `192.168.101.239` (可在脚本中修改)
- **设备A端口**: `8081`
- **设备B端口**: `8082`
- **网络要求**: 设备A和设备B需要在同一局域网
- **防火墙**: 确保设备A的8081端口和设备B的8082端口可访问
