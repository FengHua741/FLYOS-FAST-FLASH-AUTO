# Fly-Flash 自动烧录系统

## 项目简介

这是一个用于自动化烧录 Fly-C8P 控制器的分布式系统，包含两个设备的协同工作：

- **设备A**：Web 状态服务器，提供实时状态监控界面，支持刷新和重置功能
- **设备B**：烧录设备，自动执行固件烧录流程，5秒关机倒计时，并实时上报状态

## 🚀 最新更新

### v1.1 更新内容
- ✅ 设备A Web界面添加"刷新页面"和"重置状态"按钮
- ✅ 设备B关机倒计时优化为5秒
- ✅ 完整的项目结构整理
- ✅ 一键部署脚本优化

## 系统架构

```
设备A (Web服务器)         设备B (烧录设备)
     │                         │
     ├─ 显示实时状态界面         ├─ 执行DFU烧录
     ├─ 接收状态更新            ├─ 执行HID烧录  
     ├─ 提供刷新/重置功能       └─ 上报状态到设备A
     └─ 提供Web访问界面         
```

## 📁 项目文件结构

```
fly-flash-system/
├── 📄 README.md                          # 项目说明文档（本文档）
├── 🔧 部署脚本/
│   ├── deploy_all.sh                     # 一键部署脚本（自动检测设备类型）
│   ├── deploy_device_a.sh                # 设备A部署脚本
│   └── deploy_device_b.sh                # 设备B部署脚本
├── 🖥️ 设备A文件 (Web服务器)/
│   ├── flash-web-server.py               # Web状态服务器脚本（含刷新按钮）
│   └── flash-web-server.service          # Web服务器systemd服务文件
├── 🔌 设备B文件 (烧录设备)/
│   ├── fly-flash-auto.sh                 # 主烧录脚本（5秒关机版本）
│   ├── fly-flash-auto.service            # 烧录服务systemd服务文件
│   └── send-status.py                    # 状态上报脚本
└── 🛠️ 工具脚本/
    ├── service_control.sh                 # 服务管理脚本
    ├── monitor_status.sh                  # 状态监控脚本
    └── test_connection.sh                 # 连接测试脚本
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
访问设备A的Web界面：
```
http://192.168.101.239:8081
```

## 🔧 详细部署指南

### 设备A配置 (Web服务器)

设备A运行Web状态服务器，提供实时监控界面。

**部署命令：**
```bash
./deploy_device_a.sh
```

**部署过程：**
- 复制Web服务器脚本到系统目录
- 配置systemd服务并启用开机启动
- 启动Web服务器
- 验证服务状态

**访问地址：** `http://设备A-IP:8081`

### 设备B配置 (烧录设备)

设备B执行实际的烧录操作并上报状态。

**部署命令：**
```bash
./deploy_device_b.sh
```

**部署过程：**
- 安装系统依赖 (Python3, pip, requests)
- 部署烧录脚本到系统目录
- 配置systemd服务并启用开机启动
- 验证脚本权限

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
./service_control.sh
```
选择选项 1 启动服务

### 监控状态
**方法1：Web界面**
在浏览器中访问设备A的地址：
```
http://192.168.101.239:8081
```

**方法2：命令行监控**
```bash
./monitor_status.sh
```

### Web界面功能
- **实时进度显示** - 显示当前烧录步骤和进度百分比
- **状态指示灯** - 彩色状态标识（等待/运行中/成功/错误）
- **实时日志** - 显示烧录过程的详细日志
- **刷新按钮** - 手动刷新页面获取最新状态
- **重置按钮** - 清空所有日志和进度，重置为初始状态

### 服务管理
```bash
./service_control.sh
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
./test_connection.sh
```

### 常见问题

1. **连接失败**
   - 检查设备A和设备B的网络连通性
   - 确认设备A的8081端口在防火墙中开放
   - 验证IP地址配置是否正确

2. **服务启动失败**
   - 检查脚本执行权限：`chmod +x *.sh`
   - 验证Python依赖：`pip3 install requests`
   - 查看systemd服务状态

3. **烧录过程异常**
   - 检查USB设备连接
   - 验证固件文件路径是否正确
   - 查看详细日志定位问题

### 重新部署
```bash
# 设备A重新部署
./deploy_device_a.sh

# 设备B重新部署  
./deploy_device_b.sh
```

## ⚙️ 网络配置

- **设备A IP**: `192.168.101.239` (可在脚本中修改)
- **服务端口**: `8081`
- **网络要求**: 设备A和设备B需要在同一局域网
- **防火墙**: 确保设备A的8081端口可访问


## 🚨 注意事项

- ⚠️ **克隆仓库路径**：设备A和设备B的克隆路径不同，请严格按照上述说明操作
- ⚠️ 首次部署请先手动测试烧录流程
- ⚠️ 确保烧录设备连接正常
- ⚠️ 烧录过程中不要断开电源或网络
- ⚠️ 成功完成后设备B会自动关机（5秒倒计时）
- ⚠️ 重置状态会清空所有日志，谨慎操作

## 📞 技术支持

如有问题请按以下步骤排查：

1. **基础检查**
   - 网络连接是否正常
   - 服务状态是否运行
   - 设备间能否互相访问

2. **日志分析**
   - 查看systemd服务日志
   - 检查烧录详细日志
   - 验证Web服务器访问

3. **功能测试**
   - 测试设备间连接
   - 手动运行烧录脚本
   - 验证Web界面功能
