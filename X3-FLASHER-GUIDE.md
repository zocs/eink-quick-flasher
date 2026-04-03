# 阅星瞳 X3 固件定制指南

[🇬🇧 English Version](X3-FLASHER-GUIDE-EN.md)

## 目录

- [推荐工具](#推荐工具)
- [前置软件安装](#前置软件安装)
- [硬件信息](#硬件信息)
- [固件文件说明](#固件文件说明)
- [刷机前备份](#刷机前备份)
- [刷机操作](#刷机操作)
  - [首次刷入 CrossPoint](#首次刷入-crosspoint)
  - [OTA 更新固件](#ota-更新固件)
  - [恢复原厂固件](#恢复原厂固件)
- [编译固件](#编译固件)
- [中文支持](#中文支持)
- [命令参考](#命令参考)
- [故障排除](#故障排除)

---

## 推荐工具

### EInk Quick Flasher（本仓库）⭐

图形化刷机工具，无需命令行，下载即用。

- 下载：[Releases](../../releases) → `EInk-Quick-Flasher.exe`
- 功能：备份（1/4/8/16MB）、完整写入、OTA 更新、恢复原厂
- 特点：实时进度条、中英文界面、自动检测 COM 口
- 依赖：无（单文件 exe，内置 esptool）

### 其他工具

| 工具 | 说明 |
|---|---|
| [esptool](https://docs.espressif.com/projects/esptool/) | 命令行刷机工具，本指南后半部分详细说明 |
| [xteink-flasher](https://xteink-flasher.vercel.app) | 网页版刷机工具，无需安装，速度较慢（约 25 分钟备份） |

## 前置软件安装

### Python

CrossPoint 编译和字体转换需要 Python。

```powershell
# 安装 Python（如未安装）
scoop install python

# 安装 PlatformIO（ESP32 编译工具链）
pip install platformio

# 安装 esptool（ESP32 刷机工具）
pip install esptool

# 安装 freetype-py（字体转换用，可选）
pip install freetype-py
```

### 驱动

ESP32-C3 原生 USB，Windows 10/11 自带驱动，通常不需要额外安装。

如果设备管理器不显示 COM 口，安装：
- [CP210x 驱动](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
- [CH340 驱动](https://www.wch.cn/downloads/CH341SER_EXE.html)

### Git（编译用）

```powershell
scoop install git
```

### 验证安装

```powershell
python --version          # 应显示 Python 3.x
pio --version             # 应显示 PlatformIO x.x.x
python -m esptool version # 应显示 esptool v5.x
```

---

## 硬件信息

| 项目 | 值 |
|---|---|
| 设备 | 阅星瞳 X3 墨水屏阅读器 |
| 芯片 | ESP32-C3 (RISC-V, 单核, 160MHz) |
| Flash | 16MB |
| 屏幕 | SSD1677 定制驱动, 528×792, 3.68" 墨水屏 |
| 电池 | I2C 燃料计 BQ27220 (0x55) |
| RTC | DS3231 (0x68) |
| IMU | QMI8658 (0x6B) |
| I2C | SDA=GPIO20, SCL=GPIO0 |
| 连接方式 | 4触点磁吸 pogo 线 = USB (5V/GND/D+/D-) |
| 原厂固件 | XTOS V5.2.13 (2026-03-26) |

### 连接操作步骤

1. **X3 长按电源键开机**（屏幕亮起）
2. **接上磁吸线**（极性固定，只有一种方向）
3. **电脑识别 COM 口**（设备管理器显示 `USB Serial/JTAG (COM3)`）

> ⚠️ 必须先开机再接线，否则电脑无法识别。

---

## 固件文件说明

### 备份文件

| 文件 | 路径 | 大小 | 说明 |
|---|---|---|---|
| `x3_backup.bin` | `./` | 16MB | **完整 Flash 备份**。含 bootloader + 分区表 + 应用 + NVS + 文件系统。用于恢复原厂 |
| `x3_v5.2.13_official.bin` | `./` | 5.96MB | **官方 OTA 固件**。2026-03-26 最新版，仅含应用分区，用于官方 OTA 更新 |
| `x3_firmware_full.bin` | `./` | 16MB | 网上下载的旧版完整镜像（不建议使用，版本较旧） |

### 编译产物

编译输出目录：`./crosspoint-reader/.pio\build\default\`

| 文件 | 大小 | 写入位置 | 说明 |
|---|---|---|---|
| `bootloader.bin` | 18KB | `0x00000` | ESP32-C3 引导程序。首次刷入需要 |
| `partitions.bin` | 3KB | `0x08000` | 分区表。定义各分区的偏移和大小，首次刷入需要 |
| `firmware.bin` | ~5.5MB | `0x10000` | CrossPoint 应用固件。包含阅读器全部功能 |

### Flash 分区布局

```
偏移地址        大小        内容
0x00000        18KB        Bootloader (引导程序)
0x08000        3KB         Partition Table (分区表)
0x09000        20KB        NVS (配置存储)
0x0E000        8KB         OTA Data (OTA 启动信息)
0x10000        6.25MB      App0 (主应用分区，CrossPoint 运行于此)
0x650000       6.25MB      App1 (备份/OTA 更新分区)
0xC90000       3.37MB      SPIFFS (文件系统)
0xFF0000       64KB        Core Dump (崩溃日志)
```

> ⚠️ **原厂布局不同**：原厂固件的应用在 `0x780000`，不是 `0x10000`。首次刷入 CrossPoint 会改变分区表，所以必须用完整写入（bootloader + 分区表 + 应用）。

---

## 刷机前备份

> ⚠️ **刷机前必须备份！** 这是恢复原厂的唯一保障。

### 方式一：esptool 命令行（推荐，3-4 分钟）

```powershell
# 1. X3 长按电源键开机
# 2. 接上磁吸线，确认设备管理器出现 COM3
# 3. 执行备份命令

python -m esptool --port COM3 --baud 921600 read-flash 0x0 0x1000000 x3_backup.bin
```

参数说明：
- `--port COM3` — 串口号，根据设备管理器实际显示修改
- `--baud 921600` — 波特率，越高越快
- `read-flash` — 读取 Flash 命令
- `0x0` — 起始地址（从头开始）
- `0x1000000` — 读取大小（16MB = 0x1000000）
- `x3_backup.bin` — 输出文件名

完成后将 `x3_backup.bin` 保存到安全位置。

### 方式二：xteink-flasher 网页（约 25 分钟）

1. 打开 https://xteink-flasher.vercel.app
2. X3 开机 → 接磁吸线
3. 点击 **Save full flash**
4. 浏览器弹出串口选择 → 选 COM3
5. 等待完成，浏览器自动下载 `flash.bin`

> 网页版读取速度较慢（约 25 分钟），但操作更直观。

---

## 刷机操作

### 首次刷入 CrossPoint

> ⚠️ 首次刷入必须**完整写入**三个文件（bootloader + 分区表 + 应用），因为原厂分区布局与 CrossPoint 不同。

**步骤：**

1. 确认已完成备份
2. X3 长按电源键开机
3. 接上磁吸线，确认 COM3 出现
4. 执行以下命令：

```powershell
cd ./crosspoint-reader/.pio\build\default

python -m esptool --port COM3 --baud 921600 write-flash 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin
```

这条命令一次写入三个区域：
- `0x0 bootloader.bin` — 引导程序（18KB）
- `0x8000 partitions.bin` — 分区表（3KB）
- `0x10000 firmware.bin` — 应用固件（~5.5MB）

5. 完成后：
   - 拔掉磁吸线
   - 按设备底部 **Reset** 按钮（小孔，用针按）
   - 长按电源键 **3 秒** 开机

### OTA 更新固件

首次刷入成功后，分区布局已变为标准格式，后续可以只更新应用固件。

#### 方式零：EInk Quick Flasher（推荐）

1. 打开 EInk Quick Flasher
2. 选择串口 → 点击「读取信息」确认连接
3. 刷入模式选择 **OTA 更新 (仅写应用)**
4. 选择 `firmware.bin` 文件
5. 点击「刷入」→ 确认弹窗 → 等待完成

#### 方式一：esptool 命令行

```powershell
# 只写应用分区，不覆盖 bootloader 和分区表
python -m esptool --port COM3 --baud 921600 write-flash 0x10000 firmware.bin
```

#### 方式二：xteink-flasher 网页

1. 打开 https://xteink-flasher.vercel.app
2. 连接设备
3. 点击 **Flash firmware from file**
4. 选择 `firmware.bin`
5. 等待完成

> xteink-flasher 会自动将固件写入备份分区并切换 OTA 启动，保留旧固件作为回滚。

### 恢复原厂固件

> ⚠️ 恢复原厂会**覆盖整个 Flash**（16MB），包括分区布局。CrossPoint 的分区表会被原厂布局替换。

#### 方式零：EInk Quick Flasher（推荐）

1. 打开 EInk Quick Flasher
2. 选择串口 → 点击「读取信息」确认连接
3. 刷入模式选择 **恢复原厂 (从备份文件)**
4. 选择备份文件（如 `x3_cn_v5.2.13_full.bin`）
5. 点击「刷入」→ 确认弹窗 → 等待完成

#### 方式一：esptool 命令行

```powershell
python -m esptool --port COM3 --baud 921600 write-flash 0x0 "./x3_backup.bin"
```

参数说明：
- `write-flash` — 写入 Flash 命令
- `0x0` — 从头开始写入
- `x3_backup.bin` — 你的完整备份文件

过程约 **3-4 分钟**。完成后：
1. 拔掉磁吸线
2. 按 Reset 按钮
3. 长按电源键开机
4. 设备恢复到备份时的状态

---

## 编译固件

参见 [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) 项目文档。

---

## 中文支持

CrossPoint 主线不支持中文界面和中文显示。通过 SD 卡加载自定义字体实现中文显示。

### 支持的字体格式

固件支持两种 SD 卡字体格式：

| 格式 | 扩展名 | 说明 |
|---|---|---|
| `.bin` | 原始位图 | **推荐**。原厂格式，直接复制到 SD 卡即可使用 |
| `.epdfont` | CrossPoint 格式 | 需要转换工具，支持 2-bit 灰度抗锯齿 |

### 使用原厂 .bin 字体（推荐）

原厂字体格式：按 Unicode 码点直接索引的 1-bit 位图，每个字符固定大小。

**步骤：**

1. 将字体文件复制到 SD 卡 `/fonts/` 目录
2. 文件名格式：`字体名.宽×高.bin`（如 `阿里常规体.38×53.bin`）
3. 刷入支持字体加载的固件

**SD 卡目录结构：**

```
SD卡/
├── fonts/
│   └── 阿里常规体.38×53.bin
├── 书籍文件.epub
└── ...
```

**字体文件命名规则：**

- `字体名.W×H.bin` — 家族名=字体名, 宽=W, 高=H
- `字体名.bin` — 需在代码中指定宽高（默认 38×53）
- 宽高分隔符支持：`×`（乘号）、`x`、`X`

### 在设置中启用自定义字体

1. 进入 Settings → Font Family
2. 选择 **Custom**（第 4 个选项）
3. 设置 `customFontFamily` 为字体家族名（如 `阿里常规体`）

### 技术细节

**渲染流程：**

```
GfxRenderer::renderChar()
  → EpdFontFamily::loadGlyphBitmap()
    → EpdFont::loadGlyphBitmap()         (内置字体，直接返回 flash 指针)
    → CustomEpdFont::loadGlyphBitmap()   (.epdfont，从 SD 卡按需加载)
    → RawBitmapFont::loadGlyphBitmap()   (.bin，从 SD 卡按需加载)
```

**加载机制：**

- 字体启动时不预加载，按需从 SD 卡读取
- 位图缓存 512 字节/字形（一个 38×53 的字形 = 252 字节）
- Glyph 元数据缓存 64 个条目

---

## 命令参考

### esptool 基础语法

```
python -m esptool [选项] <命令> [命令参数]
```

### 全局选项

| 选项 | 说明 | 示例 |
|---|---|---|
| `--port <COM>` | 指定串口号 | `--port COM3` |
| `--baud <速率>` | 通信波特率，越高越快 | `--baud 921600` |
| `--before <动作>` | 连接前操作 | `--before default_reset` |
| `--after <动作>` | 完成后操作 | `--after hard_reset` |

常用波特率：`115200`（稳定）、`460800`（推荐）、`921600`（最快）

### flash_id — 查看 Flash 信息

```powershell
python -m esptool --port COM3 flash_id
```

输出：芯片型号、Flash 大小、MAC 地址。用于确认设备连接正常。

### read-flash — 读取 Flash（备份）

```powershell
python -m esptool --port COM3 --baud 921600 read-flash <起始地址> <大小> <输出文件>
```

| 参数 | 说明 | 示例 |
|---|---|---|
| `<起始地址>` | 读取起始位置，16进制 | `0x0` |
| `<大小>` | 读取大小，16进制 | `0x1000000` (16MB) |
| `<输出文件>` | 保存文件名 | `backup.bin` |

**完整备份命令：**

```powershell
python -m esptool --port COM3 --baud 921600 read-flash 0x0 0x1000000 x3_backup.bin
```

- `0x0` — 从 Flash 最开头读取
- `0x1000000` — 读取 16MB（= 0x1000000 字节）
- 约 3-4 分钟完成

**部分读取示例：**

```powershell
# 只读前 64KB（快速验证用）
python -m esptool --port COM3 read-flash 0x0 0x10000 verify.bin

# 只读应用分区（6.25MB）
python -m esptool --port COM3 --baud 921600 read-flash 0x10000 0x640000 app.bin
```

### write-flash — 写入 Flash（刷机）

```powershell
python -m esptool --port COM3 --baud 921600 write-flash [选项] <地址1> <文件1> [<地址2> <文件2> ...]
```

| 参数 | 说明 |
|---|---|
| `<地址>` | 写入目标地址，16进制 |
| `<文件>` | 要写入的二进制文件 |

**写入选项：**

| 选项 | 说明 |
|---|---|
| `--flash-size <大小>` | 指定 Flash 大小（detect/keep/4MB/8MB/16MB） |
| `--erase-all` | 写入前擦除整个 Flash |

**完整写入（首次刷 CrossPoint）：**

```powershell
python -m esptool --port COM3 --baud 921600 write-flash 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin
```

- `0x0 bootloader.bin` — 写引导程序到地址 0
- `0x8000 partitions.bin` — 写分区表到地址 0x8000
- `0x10000 firmware.bin` — 写应用到地址 0x10000
- 可以一次写多个区域，用空格分隔

**OTA 更新（只更新应用）：**

```powershell
python -m esptool --port COM3 --baud 921600 write-flash 0x10000 firmware.bin
```

- 只写 0x10000 位置，不碰 bootloader 和分区表
- 适用于 CrossPoint 之间的版本更新

**恢复原厂（写入完整备份）：**

```powershell
python -m esptool --port COM3 --baud 921600 write-flash 0x0 x3_backup.bin
```

- 从地址 0 写入完整 16MB 镜像
- 恢复出厂分区布局和固件

### 常见地址对照表

| 地址 | 十进制 | 用途 |
|---|---|---|
| `0x0` | 0 | Flash 起始（Bootloader） |
| `0x8000` | 32,768 | 分区表 |
| `0x9000` | 36,864 | NVS 配置区 |
| `0xE000` | 57,344 | OTA 数据区 |
| `0x10000` | 65,536 | App0 分区起始 |
| `0x650000` | 6,619,136 | App1 分区起始 |
| `0xC90000` | 13,172,736 | SPIFFS 文件系统 |
| `0x1000000` | 16,777,216 | Flash 末尾（16MB） |

### PlatformIO 编译命令

```powershell
pio run -e default
```

| 选项 | 说明 |
|---|---|
| `-e default` | 使用 default 环境编译 |
| `-t clean` | 清理编译缓存 |
| `-t upload` | 编译并直接上传到设备（需连接） |
| `-v` | 显示详细编译日志 |

### 字体转换工具

```powershell
python generate_epdfont.py <输入字体> <输出文件> [字号]
```

| 参数 | 说明 | 示例 |
|---|---|---|
| `<输入字体>` | TTF/OTF 字体文件路径 | `"C:\fonts\NotoSansSC.ttf"` |
| `<输出文件>` | 输出 .epdfont 文件名 | `"NotoSansSC-14.epdfont"` |
| `[字号]` | 可选，默认 14 | `14`、`16`、`18` |

---

## 故障排除

### 电脑不识别 COM 口

1. 确认 X3 已开机（屏幕亮起）
2. 确认磁吸线已接好
3. 检查设备管理器是否出现未知设备
4. 如果有未知设备，安装 CP210x 或 CH340 驱动
5. 尝试翻转磁吸线方向

### esptool 报 "port busy"

1. 拔掉磁吸线
2. X3 关机
3. 重新开机
4. 重新接磁吸线
5. 重试命令

### 首次刷入后无法开机

1. 按 Reset 按钮后长按电源键 3 秒
2. 如果还是不行，恢复原厂固件
3. 恢复后重新尝试刷入

### 中文显示方块

1. 确认 SD 卡 `/fonts/` 目录下有字体文件
2. 确认字体文件包含 CJK 字符
3. 确认设置中 fontFamily 设为 Custom
4. 确认 customFontFamily 设为正确名称（与文件名一致）
5. 连接串口查看日志，搜索 `[FONTS]` 或 `[FONT]` 错误

### 刷机中断后 USB 端口卡死（Windows）

备份/刷入过程中意外断开连接后，可能会出现以下情况：
- 设备报错且进度条卡住
- 重启阅读器、重新拔插磁吸线后电脑仍不识别 COM 口
- 设备管理器中也不出现任何相关设备

**原因**：Windows USB-CDC 驱动在传输中断后进入异常状态，需要重置 USB 控制器或重启系统。

**临时方案**（按顺序尝试）：
1. **设备管理器扫描**：设备管理器 → 右键顶部电脑名 → "扫描检测硬件改动"
2. **重启阅读器 USB**：X3 关机 → 拔线 → 长按电源键 10 秒（重置 USB 控制器），重新开机 → 接线
3. **卸载并重新识别**：设备管理器中出现带黄色感叹号的 "Unknown Device" → 右键卸载 → 拔线 → 等 5 秒 → 重新开机接线
4. **重启电脑**：以上都无效时的最终方案

### 刷机中断/失败

1. **不要慌**，ESP32-C3 有 ROM 引导，不会变砖
2. 重新连接设备
3. 再次执行刷机命令
4. 如果无法连接，尝试：拔线 → 按住 Reset → 接线 → 松开 Reset

---

## 相关资源

| 资源 | 链接 |
|---|---|
| CrossPoint 主线 | https://github.com/crosspoint-reader/crosspoint-reader |
| X3 分支 (zocs fork) | https://github.com/zocs/crosspoint-reader (x3-support 分支) |
| SDK (zocs fork) | https://github.com/zocs/community-sdk |
| 汉化参考 | https://github.com/icannotttt/crosspoint-chinesetype |
| 网页刷机工具 | https://xteink-flasher.vercel.app |
| X3 固件分析 Issue | https://github.com/crosspoint-reader/crosspoint-reader/issues/695 |
| esptool 文档 | https://docs.espressif.com/projects/esptool/en/latest/ |


