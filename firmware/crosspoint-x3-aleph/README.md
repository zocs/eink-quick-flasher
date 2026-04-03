# CrossPoint X3 Alpha 固件

基于 [itsthisjustin/crosspoint-reader](https://github.com/itsthisjustin/crosspoint-reader) 的 `x3-support` 分支编译。

## 文件说明

| 文件 | 写入地址 | 说明 |
|---|---|---|
| bootloader.bin | 0x00000 | ESP32-C3 引导程序 |
| partitions.bin | 0x08000 | 分区表 |
| firmware.bin | 0x10000 | CrossPoint 应用固件 |

## 编译信息

- **来源仓库**: itsthisjustin/crosspoint-reader (x3-support 分支)
- **编译环境**: PlatformIO, espressif32 55.3.37
- **环境**: `gh_release`
- **语言**: 19 种（中文暂缺，因固件未内置 CJK 字体支持）
- **日志级别**: Error（release 模式，静默）

## 刷机方式

使用 EInk Quick Flasher 工具的「完整写入」模式：
1. 选择 `firmware.bin` 文件
2. 选择「完整写入」模式（自动检测 bootloader + partitions）
3. 点击「刷入」→ 确认 → 等待完成

刷完后：拔线 → 按顶部左边 Reset → 长按顶部右边电源键 3 秒开机。

## 已知问题

- 中文语言显示空白（字体文件未内置，需 SD 卡加载方案）
- 此为测试版固件，可能存在不稳定情况

## 恢复原厂

刷入固件文件夹中的 X3 官方完整备份即可恢复。
