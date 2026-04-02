# X3 Flasher

ESP32-C3 阅星瞳 X3 备份与刷机工具

## 功能

- 🔌 自动检测 COM 口，读取设备信息
- 📦 Flash 备份（1MB / 4MB / 8MB / 16MB）
- ⚡ 固件刷入（完整写入 / OTA 更新 / 恢复原厂）
- ⏹ 备份和刷入均可终止
- 🌙 暗色主题界面

## 使用

### 下载

从 [Releases](../../releases) 下载 `X3-Flasher.exe`，双击运行。

### 连接设备

1. X3 长按电源键开机
2. 接上磁吸线（4触点 pogo 线）
3. 电脑识别到 COM 口

### 备份

1. 点击「刷新」选择串口
2. 点击「读取信息」确认连接
3. 选择保存路径和大小
4. 点击「备份」

### 刷入

- **完整写入**：bootloader.bin、partitions.bin、firmware.bin 需在同一目录，选择 firmware.bin 即可
- **OTA 更新**：仅更新应用分区，选择 firmware.bin
- **恢复原厂**：选择完整备份文件 (16MB)

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

## 依赖

- Python 3.10+
- PyQt5
- esptool
- pyserial

## 相关项目

- [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) - 开源墨水屏阅读器固件
- [xteink-flasher](https://github.com/crosspoint-reader/xteink-flasher) - 网页版刷机工具

## License

MIT
