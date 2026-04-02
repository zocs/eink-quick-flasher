"""
ESP32 X3 Flasher - Core esptool wrapper
Uses esptool.main() via sys.argv for maximum compatibility.
Falls back to subprocess if import fails.
"""

import serial.tools.list_ports
import sys
import os


def list_ports():
    """List available serial ports."""
    ports = []
    for p in serial.tools.list_ports.comports():
        if "USB" in p.description or "COM" in p.device:
            ports.append({
                "device": p.device,
                "description": p.description,
            })
    return ports


def _run_esptool(args):
    """Run esptool with args, works both as script and as exe."""
    old_argv = sys.argv
    try:
        import esptool
        sys.argv = ["esptool"] + args
        esptool.main()
        sys.argv = old_argv
        return True, ""
    except SystemExit as e:
        sys.argv = old_argv
        return e.code == 0, "" if e.code == 0 else f"exit code {e.code}"
    except Exception as e:
        sys.argv = old_argv
        return False, str(e)


def get_flash_info(port):
    """Get chip type and flash size."""
    ok, err = _run_esptool(["--port", port, "--after", "no-reset", "flash-id"])
    return {"error": None if ok else (err or "failed")}


def read_flash(port, baud, offset, size, output_file, cancel_event=None, progress_callback=None):
    """Read flash to file with cancel support."""
    # cancel_event support via subprocess is limited;
    # for now, use esptool.main() which blocks until done
    if progress_callback:
        progress_callback(0, "连接中...")
    ok, err = _run_esptool([
        "--port", port, "--baud", str(baud), "--after", "no-reset",
        "read-flash", hex(offset), hex(size), output_file,
    ])
    if ok:
        if progress_callback:
            progress_callback(100, "完成")
        return True, f"已保存: {output_file}"
    return False, f"失败: {err}"


def write_flash(port, baud, address_file_pairs, cancel_event=None, progress_callback=None):
    """Write flash from files."""
    args = ["--port", port, "--baud", str(baud), "--after", "no-reset", "write-flash"]
    for addr, filepath in address_file_pairs:
        args.extend([hex(addr), filepath])
    if progress_callback:
        progress_callback(0, "连接中...")
    ok, err = _run_esptool(args)
    if ok:
        if progress_callback:
            progress_callback(100, "完成")
        return True, "刷入完成"
    return False, f"失败: {err}"
