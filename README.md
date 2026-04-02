# X3 Flasher

ESP32-C3 阅星瞳 X3 备份与刷机工具 | Backup & Flash Tool

## 为什么用 X3 Flasher？

| | X3 Flasher (本工具) | 网页版 (xteink-flasher) |
|---|---|---|
| 备份 16MB | **~3 分钟** | ~25 分钟 |
| 刷入 5.5MB | **~1 分钟** | ~5 分钟 |
| 安装 | 下载 exe 即用 | 无需安装 |
| 依赖 | 无（内置 esptool） | 浏览器 + WebSerial |

本工具直接调用 esptool，和命令行完全一样的速度，比网页版快 **6-8 倍**。

## 功能

- 🔌 自动检测 COM 口，读取设备信息
- 📦 Flash 备份（1MB / 4MB / 8MB / 16MB），支持终止
- ⚡ 固件刷入（完整写入 / OTA 更新 / 恢复原厂），带风险确认
- 📋 实时日志，进度条显示
- 🎨 现代浅色主题

## 使用

### 下载

从 [Releases](../../releases) 下载 `X3-Flasher.exe`，双击运行。无需安装 Python 或其他依赖。

### 连接设备

1. X3 长按电源键开机
2. 接上 4 触点磁吸线
3. 电脑识别到 COM 口

### 备份

1. 选择串口 → 点击「读取信息」确认连接
2. 选择保存路径和大小
3. 点击「备份」→ 确认

### 刷入

- **完整写入**：bootloader.bin、partitions.bin、firmware.bin 需在同一目录，选择 firmware.bin 即可自动检测
- **OTA 更新**：仅更新应用分区，选择 firmware.bin
- **恢复原厂**：选择完整备份文件

---

# X3 Flasher

A backup and flashing tool for ESP32-C3-based Xingyan Tong X3 e-reader.

## Why X3 Flasher?

| | X3 Flasher | Web (xteink-flasher) |
|---|---|---|
| Backup 16MB | **~3 min** | ~25 min |
| Flash 5.5MB | **~1 min** | ~5 min |
| Install | Download exe, double-click | None needed |
| Dependencies | None (esptool bundled) | Browser + WebSerial |

This tool calls esptool directly, matching command-line speed. **6-8x faster** than the web version.

## Features

- Auto-detect COM port, read device info
- Flash backup (1/4/8/16MB) with cancel support
- Firmware flash (full write / OTA update / restore) with risk confirmation
- Real-time log with progress bar
- Modern light theme

## Usage

Download `X3-Flasher.exe` from [Releases](../../releases). No installation needed.

## Build from source

```powershell
pip install pyqt5 pyserial esptool
python main.py
```

Package as exe:

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name "X3-Flasher" --hidden-import esptool --hidden-import serial --collect-all esptool main.py
```

## Related

- [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) - Open-source e-reader firmware
- [xteink-flasher](https://github.com/crosspoint-reader/xteink-flasher) - Web-based flasher
- [X3 Flasher Guide](X3-FLASHER-GUIDE.md) - Detailed operation guide

## License

MIT
