import serial.tools.list_ports
import subprocess
import sys
import os

def list_ports():
    ports = []
    for p in serial.tools.list_ports.comports():
        if "USB" in p.description or "COM" in p.device:
            ports.append({"device": p.device, "description": p.description})
    return ports

def get_flash_info(port):
    try:
        r = subprocess.run([sys.executable, "-m", "esptool", "--port", port, "--after", "no-reset", "flash-id"],
                          capture_output=True, text=True, timeout=15)
        return {"output": r.stdout + r.stderr, "error": None if r.returncode == 0 else r.stderr}
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "timeout"}
    except Exception as e:
        return {"output": "", "error": str(e)}

def read_flash(port, baud, offset, size, output_file, cancel_event=None, progress_callback=None):
    try:
        cmd = [sys.executable, "-m", "esptool", "--port", port, "--baud", str(baud),
               "--after", "no-reset", "read-flash", hex(offset), hex(size), output_file]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            if cancel_event and cancel_event.is_set():
                proc.terminate(); proc.wait(timeout=5)
                try: os.remove(output_file)
                except: pass
                return False, "cancelled"
            if "%" in line and "bytes" in line:
                try:
                    pct = float(line.split("%")[0].split()[-1])
                    if progress_callback: progress_callback(pct, "extracting")
                except: pass
        proc.wait()
        if proc.returncode == 0:
            if progress_callback: progress_callback(100, "done")
            return True, f"saved: {output_file}"
        return False, f"failed (code {proc.returncode})"
    except Exception as e:
        return False, str(e)

def write_flash(port, baud, address_file_pairs, cancel_event=None, progress_callback=None):
    try:
        args = [sys.executable, "-m", "esptool", "--port", port, "--baud", str(baud),
                "--after", "no-reset", "write-flash"]
        for addr, fp in address_file_pairs:
            args.extend([hex(addr), fp])
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            if cancel_event and cancel_event.is_set():
                proc.terminate(); proc.wait(timeout=5)
                return False, "cancelled"
            if "%" in line and "bytes" in line:
                try:
                    pct = float(line.split("%")[0].split()[-1])
                    if progress_callback: progress_callback(pct, "writing")
                except: pass
        proc.wait()
        if proc.returncode == 0:
            if progress_callback: progress_callback(100, "done")
            return True, "flash complete"
        return False, f"failed (code {proc.returncode})"
    except Exception as e:
        return False, str(e)
