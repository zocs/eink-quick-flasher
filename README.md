# X3 / X4 Flasher

xteink 阅星瞳 X3 / X4 备份与刷机工具 | Backup & Flash Tool

[🇺🇸 English](#english) | [📖 刷机指南](X3-FLASHER-GUIDE.md)

## 特点

- 🚀 直接调用 esptool，备份刷机速度与命令行一致
- 📦 单文件 exe，无需安装 Python 或其他依赖
- 🔌 自动检测 COM 口，读取设备信息
- ⚡ 支持 X3 和 X4 设备
- 📦 Flash 备份（1MB / 4MB / 8MB / 16MB），支持终止
- ⚡ 固件刷入（完整写入 / OTA 更新 / 恢复原厂），带风险确认
- 📋 实时日志，进度条显示
- 🎨 现代浅色主题

## 使用

### 下载

从 [Releases](../../releases) 下载 `X3-Flasher.exe`，双击运行。

### 连接设备

- **X3**：长按电源键开机 → 接上 4 触点磁吸线 → 识别到 COM 口
- **X4**：USB-C 直连 → 识别到 COM 口

### 备份

1. 选择串口 → 点击「读取信息」确认连接
2. 选择保存路径和大小
3. 点击「备份」

### 刷入

- **完整写入**：bootloader.bin、partitions.bin、firmware.bin 需在同一目录，选择 firmware.bin 自动检测
- **OTA 更新**：仅更新应用分区，选择 firmware.bin
- **恢复原厂**：选择完整备份文件

## X3 / X4 分区表

### CrossPoint 固件

X3 和 X4 刷 CrossPoint 使用**相同的分区布局**，esptool 命令完全一致：

| 分区 | 偏移 | 大小 |
|---|---|---|
| Bootloader | 0x0 | 18KB |
| Partition Table | 0x8000 | 3KB |
| NVS | 0x9000 | 20KB |
| OTA Data | 0xE000 | 8KB |
| App0 | 0x10000 | 6.25MB |
| App1 | 0x650000 | 6.25MB |
| SPIFFS | 0xC90000 | 3.37MB |
| Core Dump | 0xFF0000 | 64KB |

首次刷入 CrossPoint 需要完整写入（bootloader + 分区表 + app），因为原厂分区布局不同。

### 官方固件

官方固件为完整 16MB 镜像（含 bootloader + 分区表 + 应用 + 数据），直接从地址 0x0 写入即可，无需关心分区布局。使用「恢复原厂」模式，选择备份文件即可。

## 从源码构建

```powershell
pip install pyqt5 pyserial esptool
python main.py
```

打包 exe：

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name "X3-Flasher" --hidden-import esptool --hidden-import serial --collect-all esptool main.py
```

## 相关项目

- [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) - 开源墨水屏阅读器固件
- [xteink-flasher](https://github.com/crosspoint-reader/xteink-flasher) - 网页版刷机工具

## 免责声明

本工具仅供学习交流和个人使用，基于友好分享、便捷刷机和开源精神制作。使用本工具刷写设备固件存在风险，包括但不限于设备无法启动、数据丢失等。使用者需自行评估风险并承担使用本工具导致的一切后果。开发者不对因使用本工具造成的任何损失负责。

---

<a name="english"></a>

## English

A backup and flashing tool for xteink X3 / X4 e-readers (ESP32-C3).

### Features

- Direct esptool integration — same speed as command line
- Standalone exe — no Python or dependencies needed
- Auto-detect COM port, read device info
- Supports both X3 and X4 devices
- Flash backup (1/4/8/16MB) with cancel support
- Firmware flash (full write / OTA update / restore) with risk confirmation
- Real-time log with progress bar
- Modern light theme

### Usage

Download `X3-Flasher.exe` from [Releases](../../releases). No installation needed.

**Connection:**
- **X3**: Hold power button to turn on → connect magnetic pogo cable → COM port detected
- **X4**: Connect USB-C cable → COM port detected

### Partition Table

Both X3 and X4 use the same partition layout for CrossPoint firmware. The flasher commands are identical for both devices.

Official firmware is a full 16MB image (includes bootloader + partition table + app + data). Use "Restore" mode and select the backup file.

### Build from source

```powershell
pip install pyqt5 pyserial esptool
python main.py
```

### Related

- [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) — Open-source e-reader firmware
- [xteink-flasher](https://github.com/crosspoint-reader/xteink-flasher) — Web-based flasher
- [Guide](X3-FLASHER-GUIDE.md) — Detailed operation guide

### Disclaimer

This tool is provided for educational and personal use only, created with the spirit of friendly sharing, convenient flashing, and open source. Flashing device firmware carries risks including but not limited to device failure and data loss. Users should evaluate the risks and bear all consequences of using this tool. The developer is not responsible for any damage caused by the use of this tool.

## License

MIT
