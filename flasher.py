import serial.tools.list_ports
import subprocess
import sys
import os
from threading import Thread, Event

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

def _parse_progress(line):
    if "%" in line:
        try:
            return float(line.split("%")[0].split()[-1])
        except:
            pass
    return None

def _run_with_progress(cmd, cancel_event, progress_callback, status_label):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    done = Event()

    def read_stream(stream):
        for line in stream:
            if done.is_set():
                break
            pct = _parse_progress(line)
            if pct is not None and progress_callback:
                progress_callback(pct, status_label)

    t_out = Thread(target=read_stream, args=(proc.stdout,), daemon=True)
    t_err = Thread(target=read_stream, args=(proc.stderr,), daemon=True)
    t_out.start()
    t_err.start()

    while proc.poll() is None:
        if cancel_event and cancel_event.is_set():
            done.set()
            proc.terminate()
            proc.wait(timeout=5)
            return False, "cancelled"

    done.set()
    t_out.join(timeout=2)
    t_err.join(timeout=2)
    return proc.returncode == 0, proc.returncode

def read_flash(port, baud, offset, size, output_file, cancel_event=None, progress_callback=None):
    try:
        cmd = [sys.executable, "-m", "esptool", "--port", port, "--baud", str(baud),
               "--after", "no-reset", "read-flash", hex(offset), hex(size), output_file]
        ok, code = _run_with_progress(cmd, cancel_event, progress_callback, "extracting")
        if not ok:
            if code == "cancelled":
                try: os.remove(output_file)
                except: pass
                return False, "cancelled"
            return False, f"failed (code {code})"
        if progress_callback:
            progress_callback(100, "done")
        return True, f"saved: {output_file}"
    except Exception as e:
        return False, str(e)

def write_flash(port, baud, address_file_pairs, cancel_event=None, progress_callback=None):
    try:
        args = [sys.executable, "-m", "esptool", "--port", port, "--baud", str(baud),
                "--after", "no-reset", "write-flash"]
        for addr, fp in address_file_pairs:
            args.extend([hex(addr), fp])
        ok, code = _run_with_progress(args, cancel_event, progress_callback, "writing")
        if not ok:
            if code == "cancelled":
                return False, "cancelled"
            return False, f"failed (code {code})"
        if progress_callback:
            progress_callback(100, "done")
        return True, "flash complete"
    except Exception as e:
        return False, str(e)
