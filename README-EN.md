# EInk Quick Flasher

A fast backup and flashing tool for ESP32-C3 e-ink readers.

Supported devices: xteink X3, X4

[中文](README.md) | [📖 Guide](X3-FLASHER-GUIDE.md)

## Features

- Direct esptool integration — same speed as command line
- Standalone exe — no Python or dependencies needed
- Auto-detect COM port, read device info
- Supports X3 and X4 devices
- Flash backup (1/4/8/16MB) with cancel support
- Firmware flash (full write / OTA update / restore) with risk confirmation
- Real-time log with progress bar
- Bilingual UI (Chinese / English) with one-click toggle
- Modern light theme

## Usage

Download `EInk-Quick-Flasher.exe` from [Releases](../../releases). No installation needed.

### Connection

- **X3**: Hold power button → connect magnetic pogo cable → COM port detected
- **X4**: Connect USB-C cable → COM port detected

### Backup

1. Select port → click "Read Info" to confirm
2. Choose save path and size
3. Click "Backup"

### Flash

- **Full write**: bootloader.bin, partitions.bin, firmware.bin must be in the same directory
- **OTA update**: flash app partition only
- **Restore**: select backup file. Stock firmware in `firmware/` directory. CN/EN designation only indicates default UI language — firmware content is identical, language can be switched in settings.

| File | Description |
|---|---|
| x3_cn_v5.2.13_stock.bin | V5.2.13 (Chinese default) |
| x3_en_v5.2.13_stock.bin | V5.2.13 (English default) |
| x3_en_v1.0.7_stock.bin | V1.0.7 (English default) |

## Partition Table

Both X3 and X4 use the same partition layout for CrossPoint:

| Partition | Offset | Size |
|---|---|---|
| Bootloader | 0x0 | 18KB |
| Partition Table | 0x8000 | 3KB |
| App0 | 0x10000 | 6.25MB |
| App1 | 0x650000 | 6.25MB |
| SPIFFS | 0xC90000 | 3.37MB |

First-time CrossPoint flash requires full write. Subsequent updates can use OTA.

Official firmware is a full 16MB image. Use "Restore" mode, no partition concerns.

## Build from source

```powershell
pip install pyserial esptool
python main.py
```

## Related

- [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) — Open-source e-reader firmware
- [xteink-flasher](https://github.com/crosspoint-reader/xteink-flasher) — Web-based flasher

## Disclaimer

This tool is for educational and personal use only. Non-profit, shared free of charge for user convenience. Flashing firmware carries risks. Users bear all consequences. The developer is not responsible for any damage.

## License

MIT
