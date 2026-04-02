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

1. X3/X4 长按电源键开机
2. 接上数据线（X3 为 4 触点磁吸线，X4 为 USB-C）
3. 电脑识别到 COM 口

### 备份

1. 选择串口 → 点击「读取信息」确认连接
2. 选择保存路径和大小
3. 点击「备份」

### 刷入

- **完整写入**：bootloader.bin、partitions.bin、firmware.bin 需在同一目录，选择 firmware.bin 自动检测
- **OTA 更新**：仅更新应用分区
- **恢复原厂**：选择完整备份文件

## 从源码构建

```powershell
pip install pyqt5 pyserial esptool
python main.py
```

打包：

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name "X3-Flasher" --hidden-import esptool --hidden-import serial --collect-all esptool main.py
```

## 相关项目

- [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) - 开源墨水屏阅读器固件
- [xteink-flasher](https://github.com/crosspoint-reader/xteink-flasher) - 网页版刷机工具

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

### Build from source

```powershell
pip install pyqt5 pyserial esptool
python main.py
```

### Related

- [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) — Open-source e-reader firmware
- [xteink-flasher](https://github.com/crosspoint-reader/xteink-flasher) — Web-based flasher
- [Guide](X3-FLASHER-GUIDE.md) — Detailed operation guide

## X3 / X4 Partition Table

Both devices use ESP32-C3 with the same standard partition layout (compatible with CrossPoint):

| Partition | Offset | Size |
|---|---|---|
| NVS | 0x9000 | 20KB |
| OTA Data | 0xE000 | 8KB |
| App0 | 0x10000 | 6.25MB |
| App1 | 0x650000 | 6.25MB |
| SPIFFS | 0xC90000 | 3.37MB |
| Core Dump | 0xFF0000 | 64KB |

**Note:** Stock X3 firmware uses a different partition layout (app at 0x780000). First-time CrossPoint flash requires full write (bootloader + partition table + app).

## License

MIT
