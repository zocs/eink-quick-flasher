import serial.tools.list_ports
import sys
import os
import io
from threading import Thread, Event
from concurrent.futures import Future

# ── PyInstaller frozen detection ──────────────────────────────
def _is_frozen():
    return getattr(sys, 'frozen', False)

if _is_frozen() and sys.platform == "win32":
    import subprocess
    _CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
else:
    import subprocess
    _CREATE_NO_WINDOW = 0

class _StdoutCapture:
    """Captures writes to extract esptool progress and full output."""
    def __init__(self):
        self._buf = []

    def write(self, s):
        self._buf.append(s)
        return len(s)

    def flush(self):
        pass

    def get(self):
        return "".join(self._buf)

def _run_esptool_in_thread(args, cancel_event, progress_callback, status_label):
    """Run esptool.main() in a thread with stdout captured."""
    import esptool
    import traceback

    captured = _StdoutCapture()

    def _parse_and_report(text):
        if progress_callback and "%" in text:
            text = text.replace("\r", " ")
            parts = text.split()
            for part in reversed(parts):
                p = part.rstrip("%) ")
                try:
                    v = float(p)
                    if 0 <= v <= 100:
                        progress_callback(v, status_label)
                        return
                except ValueError:
                    continue

    def worker(fut):
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = captured, captured
        try:
            code = esptool.main(args)
            fut.set_result(code or 0)
        except SystemExit as e:
            fut.set_result(e.code if isinstance(e.code, int) else (1 if e.code else 0))
        except Exception:
            traceback.print_exc(file=captured)
            fut.set_result(1)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

    fut = Future()
    t = Thread(target=worker, args=(fut,), daemon=True)
    t.start()

    # Poll for progress + cancel while esptool runs
    while t.is_alive():
        if cancel_event and cancel_event.is_set():
            return False, "cancelled"

        output = captured.get()
        _parse_and_report(output[-2000:])
        t.join(timeout=0.1)

    # Final output parsing
    output = captured.get()
    _parse_and_report(output[-2000:])

    try:
        code = fut.result(timeout=2)
    except Exception:
        code = 1

    if cancel_event and cancel_event.is_set():
        return False, "cancelled"

    ok = (code == 0)
    if not ok:
        return False, f"failed (code {code})\n{output.strip()}"
    return True, output.strip()

# ── Fallback: subprocess (non-frozen / dev mode) ─────────────
def _get_python_executable():
    for candidate in ['python', 'python3', 'py']:
        try:
            r = subprocess.run([candidate, '--version'], capture_output=True, timeout=3,
                             creationflags=_CREATE_NO_WINDOW)
            if r.returncode == 0:
                return candidate
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None

def _build_esptool_cmd(args):
    py = _get_python_executable()
    if py:
        return [py, '-m', 'esptool'] + args
    return ['esptool'] + args

def _run_with_progress(cmd, cancel_event, progress_callback, status_label):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, bufsize=1, creationflags=_CREATE_NO_WINDOW)
    done = Event()

    def read_stream(stream):
        for line in stream:
            if done.is_set():
                break
            if "%" in line:
                try:
                    pct = float(line.split("%")[0].split()[-1])
                    if progress_callback:
                        progress_callback(pct, status_label)
                except:
                    pass

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

    if proc.returncode == 0 and progress_callback:
        progress_callback(100, "done")

    return proc.returncode == 0, proc.returncode

def _run_esptool(args, cancel_event, progress_callback, status_label):
    if _is_frozen():
        return _run_esptool_in_thread(args, cancel_event, progress_callback, status_label)
    cmd = _build_esptool_cmd(args)
    return _run_with_progress(cmd, cancel_event, progress_callback, status_label)

# ── Public API ────────────────────────────────────────────────
def list_ports():
    ports = []
    for p in serial.tools.list_ports.comports():
        if "USB" in p.description or "COM" in p.device:
            ports.append({"device": p.device, "description": p.description})
    return ports

def get_flash_info(port):
    try:
        ok, output = _run_esptool(["--port", port, "--after", "no-reset", "flash-id"],
                                   None, None, "info")
        return {"output": output, "error": None if ok else output}
    except Exception as e:
        return {"output": "", "error": str(e)}

def read_flash(port, baud, offset, size, output_file, cancel_event=None, progress_callback=None):
    try:
        if progress_callback:
            progress_callback(0, "connecting")
        ok, msg = _run_esptool(["--port", port, "--baud", str(baud),
                                 "--after", "no-reset", "read-flash", hex(offset), hex(size), output_file],
                                cancel_event, progress_callback, "extracting")
        if not ok:
            if msg == "cancelled":
                try: os.remove(output_file)
                except: pass
            return False, msg
        return True, f"saved: {output_file}"
    except Exception as e:
        return False, str(e)

def write_flash(port, baud, address_file_pairs, cancel_event=None, progress_callback=None):
    try:
        if progress_callback:
            progress_callback(0, "connecting")
        args = ["--port", port, "--baud", str(baud),
                "--after", "no-reset", "write-flash"]
        for addr, fp in address_file_pairs:
            args.extend([hex(addr), fp])
        ok, msg = _run_esptool(args, cancel_event, progress_callback, "writing")
        if not ok:
            if msg == "cancelled":
                return False, "cancelled"
            return False, msg
        return True, "flash complete"
    except Exception as e:
        return False, str(e)
