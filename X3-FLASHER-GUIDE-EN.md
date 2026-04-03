# XTeink X3 Firmware Flashing Guide

[🇨🇳 中文版刷机指南](X3-FLASHER-GUIDE.md)

## Table of Contents

- [Recommended Tools](#recommended-tools)
- [Prerequisites](#prerequisites)
- [Hardware Info](#hardware-info)
- [Firmware Files](#firmware-files)
- [Backup Before Flashing](#backup-before-flashing)
- [Flashing](#flashing)
  - [First-Time CrossPoint Flash](#first-time-crosspoint-flash)
  - [OTA Update](#ota-update)
  - [Restore Stock](#restore-stock)
- [Compiling Firmware](#compiling-firmware)
- [Chinese Language Support](#chinese-language-support)
- [Command Reference](#command-reference)
- [Troubleshooting](#troubleshooting)

---

## Recommended Tools

### EInk Quick Flasher (in this repo)⭐

Graphical flash tool, no command line needed.

- Download: [Releases](../../releases) → `EInk-Quick-Flasher-v0.2.3.exe`
- Features: backup (1/4/8/16 MB), full write, OTA, factory restore
- Single file .exe, no Python required

### Other Tools

| Tool | Description |
|---|---|
| [esptool](https://docs.espressif.com/projects/esptool/) | Command-line flash tool, detailed below |
| [xteink-flasher](https://xteink-flasher.vercel.app) | Web-based flash tool, no install, slower (~25 min backup) |

## Prerequisites

### Python

Required for CrossPoint compilation and font conversion.

```powershell
# Install Python (if not installed)
scoop install python

# Install PlatformIO (ESP32 build toolchain)
pip install platformio

# Install esptool (ESP32 flash tool)
pip install esptool

# Install freetype-py (font conversion, optional)
pip install freetype-py
```

### Drivers

ESP32-C3 has native USB, Windows 10/11 includes drivers automatically.

If the device manager doesn't show a COM port, install:
- [CP210x Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
- [CH340 Driver](https://www.wch.cn/downloads/CH341SER_EXE.html)

### Git (for compilation)

```powershell
scoop install git
```

### Verify Installation

```powershell
python --version          # Should show Python 3.x
pio --version             # Should show PlatformIO x.x.x
python -m esptool version # Should show esptool v5.x
```

---

## Hardware Info

| Item | Value |
|---|---|
| Device | XTeink X3 E-Ink Reader |
| Chip | ESP32-C3 (RISC-V, single core, 160 MHz) |
| Flash | 16 MB |
| Screen | SSD1677 custom driver, 528×792, 3.68" E-Ink |
| Battery | I2C fuel gauge BQ27220 (0x55) |
| RTC | DS3231 (0x68) |
| IMU | QMI8658 (0x6B) |
| I2C | SDA=GPIO20, SCL=GPIO0 |
| Connection | 4-pin magnetic pogo cable = USB (5V/GND/D+/D-) |
| Stock Firmware | XTOS V5.2.13 (2026-03-26) |

### Connection Steps

1. **Hold power button on X3 to turn on** (screen lights up)
2. **Connect pogo cable** (polarity is fixed, only one way)
3. **PC detects COM port** (Device Manager shows `USB Serial/JTAG (COM3)`)

> ⚠️ Turn on the device first, then connect the cable. Otherwise the PC won't detect it.

---

## Firmware Files

### Backup Files

| File | Path | Size | Description |
|---|---|---|---|
| `x3_backup.bin` | `./` | 16 MB | **Full Flash backup**. Bootloader + partition table + app + NVS + filesystem. For restore to stock |
| `x3_v5.2.13_official.bin` | `./` | 5.96 MB | **Official OTA firmware**. Latest from 2026-03-26, app partition only |
| `x3_firmware_full.bin` | `./` | 16 MB | Old full image from the internet (not recommended, outdated) |

### Build Artifacts

Build output directory: `./crosspoint-reader/.pio/build/default/`

| File | Size | Write Address | Description |
|---|---|---|---|
| `bootloader.bin` | 18 KB | `0x00000` | ESP32-C3 bootloader. Needed for first-time flash |
| `partitions.bin` | 3 KB | `0x08000` | Partition table. Defines partition offsets and sizes |
| `firmware.bin` | ~5.5 MB | `0x10000` | CrossPoint application firmware |

### Flash Partition Layout

```
Offset          Size        Content
0x00000         18 KB       Bootloader
0x08000         3 KB        Partition Table
0x09000         20 KB       NVS (config storage)
0x0E000         8 KB        OTA Data
0x10000         6.25 MB     App0 (main app, CrossPoint runs here)
0x650000        6.25 MB     App1 (backup/OTA partition)
0xC90000        3.37 MB     SPIFFS (filesystem)
0xFF0000        64 KB       Core Dump (crash log)
```

> ⚠️ **Stock layout differs**: Stock firmware's app is at `0x780000`, not `0x10000`. First-time CrossPoint flash changes the partition table, so you must use full write (bootloader + partition table + app).

---

## Backup Before Flashing

> ⚠️ **Always backup before flashing!** This is the only way to restore stock.

### Method 1: esptool CLI (recommended, 3-4 min)

```powershell
# 1. Turn on X3 (hold power button)
# 2. Connect pogo cable, confirm COM3 appears in Device Manager
# 3. Run the backup command

python -m esptool --port COM3 --baud 921600 read-flash 0x0 0x1000000 x3_backup.bin
```

Parameters:
- `--port COM3` — serial port, adjust based on Device Manager
- `--baud 921600` — baud rate, higher is faster
- `read-flash` — read Flash command
- `0x0` — start address (from the beginning)
- `0x1000000` — read size (16 MB)
- `x3_backup.bin` — output filename

Save `x3_backup.bin` to a safe location after completion.

### Method 2: xteink-flasher web (~25 min)

1. Open https://xteink-flasher.vercel.app
2. Turn on X3 → connect pogo cable
3. Click **Save full flash**
4. Browser pops up serial port selector → select COM3
5. Wait for completion, browser auto-downloads `flash.bin`

> The web version is slow (~25 min), but more visual.

---

## Flashing

### First-Time CrossPoint Flash

> ⚠️ First-time flash must **write all three files** (bootloader + partition table + app), because stock partition layout differs from CrossPoint.

**Steps:**

1. Confirm you have a backup
2. Turn on X3 (hold power button)
3. Connect pogo cable, confirm COM3
4. Run:

```powershell
cd ./crosspoint-reader/.pio\build\default

python -m esptool --port COM3 --baud 921600 write-flash 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin
```

This writes three regions at once:
- `0x0 bootloader.bin` — bootloader (18 KB)
- `0x8000 partitions.bin` — partition table (3 KB)
- `0x10000 firmware.bin` — application firmware (~5.5 MB)

5. After completion:
   - Disconnect cable
   - Press **Reset** button on the bottom (small hole, use a pin)
   - Hold power button for **3 seconds** to boot

### OTA Update

After first-time flash, the partition layout is now standard, so you can update just the app firmware.

#### Method 1: EInk Quick Flasher (recommended)

1. Open EInk Quick Flasher
2. Select port → click "Read Info" to confirm connection
3. Select **OTA Update** mode
4. Pick `firmware.bin`
5. Click "Flash" → confirm popup → wait

#### Method 2: esptool CLI

```powershell
# Only write the app partition, don't touch bootloader or partition table
python -m esptool --port COM3 --baud 921600 write-flash 0x10000 firmware.bin
```

#### Method 3: xteink-flasher web

1. Open https://xteink-flasher.vercel.app
2. Connect device
3. Click **Flash firmware from file**
4. Select `firmware.bin`
5. Wait for completion

> xteink-flasher automatically writes to the backup partition and switches OTA boot, keeping the old firmware as rollback.

### Restore Stock

> ⚠️ Restoring stock **overwrites the entire Flash** (16 MB), including partition layout. The CrossPoint partition table will be replaced by the stock layout.

#### Method 1: EInk Quick Flasher

1. Open EInk Quick Flasher
2. Select port → click "Read Info"
3. Select **Restore** mode
4. Pick backup file (e.g. `x3_cn_v5.2.13_full.bin`)
5. Click "Flash" → confirm → wait

#### Method 2: esptool CLI

```powershell
python -m esptool --port COM3 --baud 921600 write-flash 0x0 "./x3_backup.bin"
```

Takes **3-4 minutes**. After completion:
1. Disconnect cable
2. Press Reset
3. Hold power button to boot
4. Device is restored to the state of your backup

---

## Compiling Firmware

See [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) docs.

---

## Chinese Language Support

CrossPoint mainline does not support Chinese UI or font display. Custom fonts are loaded from the SD card.

### Supported Font Formats

The firmware supports two SD card font formats:

| Format | Extension | Description |
|---|---|---|
| `.bin` | Raw bitmap | **Recommended**. Stock format, just copy to SD card |
| `.epdfont` | CrossPoint format | Needs conversion tool, supports 2-bit grayscale AA |

### Using Stock .bin Fonts (recommended)

1. Copy font file to SD card `/fonts/` directory
2. Name format: `FontName.Width×Height.bin` (e.g. `阿里常规体.38×53.bin`)
3. Flash firmware supporting font loading

**SD card structure:**

```
SD Card/
├── fonts/
│   └── 阿里常规体.38×53.bin
├── book.epub
└── ...
```

### Enabling Custom Fonts in Settings

1. Go to Settings → Font Family
2. Select **Custom** (4th option)
3. Set `customFontFamily` to the font family name (e.g. `阿里常规体`)

### Technical Details

**Rendering pipeline:**

```
GfxRenderer::renderChar()
  → EpdFontFamily::loadGlyphBitmap()
    → EpdFont::loadGlyphBitmap()         (built-in fonts, direct flash pointer)
    → CustomEpdFont::loadGlyphBitmap()   (.epdfont, lazy-loaded from SD)
    → RawBitmapFont::loadGlyphBitmap()   (.bin, lazy-loaded from SD)
```

**Loading mechanism:**
- Fonts are not pre-loaded, loaded on-demand from SD card
- Bitmap cache: 512 bytes per glyph (a 38×53 glyph = 252 bytes)
- Glyph metadata cache: 64 entries

---

## Command Reference

### esptool Basic Syntax

```
python -m esptool [options] <command> [command args]
```

### Global Options

| Option | Description | Example |
|---|---|---|
| `--port <COM>` | Serial port | `--port COM3` |
| `--baud <rate>` | Baud rate, higher is faster | `--baud 921600` |
| `--before <action>` | Before connection action | `--before default_reset` |
| `--after <action>` | After completion action | `--after hard_reset` |

Common baud rates: `115200` (stable), `460800` (recommended), `921600` (fastest)

### flash_id

```powershell
python -m esptool --port COM3 flash_id
```

Output: chip model, Flash size, MAC address. Confirms device is connected.

### read-flash

```powershell
python -m esptool --port COM3 --baud 921600 read-flash 0x0 0x1000000 x3_backup.bin
```

### write-flash

```powershell
python -m esptool --port COM3 --baud 921600 write-flash 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin
```

### Address Reference Table

| Address | Decimal | Description |
|---|---|---|
| `0x0` | 0 | Flash start (Bootloader) |
| `0x8000` | 32,768 | Partition Table |
| `0x9000` | 36,864 | NVS config |
| `0xE000` | 57,344 | OTA Data |
| `0x10000` | 65,536 | App0 partition start |
| `0x650000` | 6,619,136 | App1 partition start |
| `0xC90000` | 13,172,736 | SPIFFS filesystem |
| `0x1000000` | 16,777,216 | End of Flash (16 MB) |

### PlatformIO Build Command

```powershell
pio run -e default
```

---

## Troubleshooting

### USB Port Dead After Interrupted Flash (Windows)

After a backup or flash interruption, you may encounter:
- An error displayed in the tool, progress bar stuck
- After rebooting the reader and reconnecting, the PC doesn't detect any COM port
- Device Manager doesn't show any related device

**Cause**: Windows USB-CDC driver enters an abnormal state after interrupted transfer. The USB controller needs resetting or a system reboot.

**Workarounds** (try in order):
1. **Device Manager scan**: Device Manager → right-click the PC name at top → "Scan for hardware changes"
2. **Reader USB reset**: Turn off X3 → disconnect cable → hold power button for 10 seconds (resets USB controller) → turn on again → reconnect cable
3. **Uninstall unknown device**: If a yellow "Unknown Device" appears in Device Manager → right-click Uninstall → disconnect → wait 5 seconds → turn on and reconnect
4. **Restart the PC**: Final resort if nothing else works

### PC Doesn't Detect COM Port

1. Confirm X3 is on (screen lit)
2. Confirm pogo cable is connected properly
3. Check Device Manager for unknown devices
4. If there's an unknown device, install CP210x or CH340 drivers
5. Try flipping the pogo cable

### esptool reports "port busy"

1. Disconnect cable
2. Turn off X3
3. Turn on again
4. Reconnect cable
5. Retry command

### Can't Boot After First Flash

1. Press Reset, then hold power button for 3 seconds
2. If still failing, restore stock firmware
3. Retry after restore

### Chinese Characters Show as Squares

1. Confirm font file exists in SD card `/fonts/`
2. Confirm font file contains CJK characters
3. Confirm Settings has fontFamily set to Custom
4. Confirm `customFontFamily` matches the file name
5. Connect serial, search logs for `[FONTS]` or `[FONT]` errors

### Flashing Interrupted / Failed

1. **Don't panic** — ESP32-C3 has a ROM bootloader, it won't brick
2. Reconnect device
3. Retry the flash command
4. If connection fails: disconnect → hold Reset → connect → release Reset

---

## Resources

| Resource | Link |
|---|---|
| CrossPoint Main | https://github.com/crosspoint-reader/crosspoint-reader |
| X3 Branch (zocs fork) | https://github.com/zocs/crosspoint-reader (x3-support branch) |
| SDK (zocs fork) | https://github.com/zocs/community-sdk |
| Chinese Font Reference | https://github.com/icannotttt/crosspoint-chinesetype |
| Web Flash Tool | https://xteink-flasher.vercel.app |
| X3 Firmware Analysis Issue | https://github.com/crosspoint-reader/crosspoint-reader/issues/695 |
| esptool Docs | https://docs.espressif.com/projects/esptool/en/latest/ |
