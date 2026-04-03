"""EInk Quick Flasher - tkinter GUI with bilingual support"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from threading import Event, Thread

import flasher

# ── Color palette ──────────────────────────────────────────────
BG = "#F5F5F5"
CARD = "#FFFFFF"
ACCENT = "#E43F5A"
ACCENT_HOVER = "#FF5A7A"
ACCENT_PRESSED = "#C0354A"
SECONDARY = "#4A90D9"
SECONDARY_HOVER = "#3A7BC0"
BORDER = "#E0E0E0"
INPUT_BG = "#FFFFFF"
TEXT_COLOR = "#1A1A2E"
TEXT_DIM = "#999999"
LOG_BG = "#FAFAFA"
GREEN = "#27AE60"
PB_TROUGH = "#F0F0F0"

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SUBTITLE = ("Segoe UI", 9)
FONT_STATUS = ("Segoe UI", 9)
FONT_LOG = ("Cascadia Code", 9)
FONT_LOG_TS = ("Cascadia Code", 9)

# ── i18n ───────────────────────────────────────────────────────
LANG = {
    "zh": {
        "title": "EInk Quick Flasher",
        "subtitle": "ESP32-C3 墨水屏阅读器备份与刷机工具  |  X3 / X4",
        "device_group": "设备连接",
        "port": "串口:",
        "refresh": "刷新",
        "baud": "波特率:",
        "read_info": "读取信息",
        "status_disconnected": "未连接",
        "status_connecting": "连接中...",
        "status_connected": "已连接",
        "status_failed": "连接失败",
        "log_select_port": "请选择串口",
        "log_ports_found": "串口: {n} 个",
        "log_connecting": "连接 {port}...",
        "log_failed": "失败: {err}",
        "backup_group": "备份 Flash",
        "save_to": "保存到:",
        "browse": "浏览",
        "size": "大小:",
        "backup": "备份",
        "cancel": "终止",
        "ready": "就绪",
        "extracting": "提取中...",
        "placeholder_save": "选择保存路径...",
        "save_backup_title": "保存备份",
        "confirm_backup_title": "确认备份",
        "confirm_backup_msg": "将提取 {sz} Flash 内容到：\n{path}\n\n请保持数据线连接。\n\n确认开始？",
        "log_cancelled": "已取消",
        "cancel_warn": "刷入过程中取消可能导致 bootloader 损坏，设备变砖。\n\n确认取消？",
        "flash_group": "刷入固件",
        "mode_full": "完整写入 (自动检测 bootloader.bin + partitions.bin + 固件文件)",
        "mode_ota": "OTA 更新 (仅写应用)",
        "mode_restore": "恢复原厂 (从备份文件)",
        "file": "文件:",
        "flash": "刷入",
        "placeholder_flash": "选择固件文件...",
        "select_fw_title": "选择固件",
        "log_select_valid_file": "请选择有效文件",
        "log_full_requires": "完整写入需要以下文件在同一目录:",
        "log_missing": "缺少: {name}",
        "warn_full_title": "风险提示",
        "warn_full_msg": "⚠️ 完整写入会改变分区布局！\n\n• 确保已完成备份\n• 写入中请保持连接\n• 断开有变砖风险\n\n确认？",
        "warn_ota_msg": "即将 OTA 更新\n\n• 写入中请保持连接\n• 断开有变砖风险\n\n确认？",
        "warn_restore_msg": "⚠️ 恢复原厂！覆盖整个 Flash\n\n• 写入中请保持连接\n• 断开有变砖风险\n\n确认？",
        "pb_ready": "就绪",
        "pb_connecting": "连接...",
        "pb_done": "完成",
        "pb_done_wait": "✅ 完成，请稍等...",
        "pb_preparing": "0%  -  准备写入",
        "log_ready": "就绪。请连接设备。",
        "log_restart_tip": "拔线 → 按一下 Reset 键 → 长按电源键重启",
        "bak_success": "✅ 备份完成！{msg}\n→ 拔线 → 按一下 Reset 键 → 长按电源键重启",
        "flash_success": "✅ 刷入完成！\n→ 拔线 → 按一下 Reset 键 → 长按电源键重启",
        "writing_status": "写入中 · 请保持连接",
        "lang_btn": "EN",
    },
    "en": {
        "title": "EInk Quick Flasher",
        "subtitle": "ESP32-C3 E-Ink Reader Backup & Flash Tool  |  X3 / X4",
        "device_group": "Device",
        "port": "Port:",
        "refresh": "Refresh",
        "baud": "Baud Rate:",
        "read_info": "Read Info",
        "status_disconnected": "Not connected",
        "status_connecting": "Connecting...",
        "status_connected": "Connected",
        "status_failed": "Connection failed",
        "log_select_port": "Please select a port",
        "log_ports_found": "Ports found: {n}",
        "log_connecting": "Connecting {port}...",
        "log_failed": "Failed: {err}",
        "backup_group": "Backup Flash",
        "save_to": "Save to:",
        "browse": "Browse",
        "size": "Size:",
        "backup": "Backup",
        "cancel": "Cancel",
        "ready": "Ready",
        "extracting": "Extracting...",
        "placeholder_save": "Select save path...",
        "save_backup_title": "Save Backup",
        "confirm_backup_title": "Confirm Backup",
        "confirm_backup_msg": "Extract {sz} Flash content to:\n{path}\n\nPlease keep the data cable connected.\n\nConfirm to start?",
        "log_cancelled": "Cancelled",
        "cancel_warn": "Cancelling during flash may damage the bootloader and brick the device.\n\nConfirm cancel?",
        "flash_group": "Flash Firmware",
        "mode_full": "Full Write (auto-detect bootloader.bin + partitions.bin + firmware)",
        "mode_ota": "OTA Update (flash app only)",
        "mode_restore": "Restore (from backup file)",
        "file": "File:",
        "flash": "Flash",
        "placeholder_flash": "Select firmware file...",
        "select_fw_title": "Select Firmware",
        "log_select_valid_file": "Please select a valid file",
        "log_full_requires": "Full write requires these files in the same directory:",
        "log_missing": "Missing: {name}",
        "warn_full_title": "Warning",
        "warn_full_msg": "⚠️ Full write will change partition layout!\n\n• Make sure backup is complete\n• Keep connected during write\n• Disconnecting may brick the device\n\nConfirm?",
        "warn_ota_msg": "OTA Update\n\n• Keep connected during write\n• Disconnecting may brick the device\n\nConfirm?",
        "warn_restore_msg": "⚠️ Restore! Will overwrite entire Flash\n\n• Keep connected during write\n• Disconnecting may brick the device\n\nConfirm?",
        "pb_ready": "Ready",
        "pb_connecting": "Connecting...",
        "pb_done": "Done",
        "pb_done_wait": "✅ Done, please wait...",
        "pb_preparing": "0%  -  Preparing",
        "log_ready": "Ready. Please connect device.",
        "log_restart_tip": "Disconnect → Press Reset → Hold power button to restart",
        "bak_success": "✅ Backup complete! {msg}\n→ Disconnect → Press Reset → Hold power button to restart",
        "flash_success": "✅ Flash complete!\n→ Disconnect → Press Reset → Hold power button to restart",
        "writing_status": "Writing · Keep connected",
        "lang_btn": "中文",
    },
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "zh"
        self.L = LANG[self.lang]
        self.title("EInk Quick Flasher")
        self.configure(bg=BG)
        self.minsize(600, 680)
        self.geometry("640x720")

        self.bak_cancel = Event()
        self.flash_cancel = Event()
        self._bak_thread = None
        self._flash_thread = None

        # ttk style
        self._setup_styles()
        self._build_ui()
        self._refresh_ports()
        self._log(self.L["log_ready"])

    # ── Styles ─────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        # Card frame (LabelFrame)
        s.configure("Card.TLabelframe", background=CARD, borderwidth=2, relief="solid",
                     bordercolor=BORDER)
        s.configure("Card.TLabelframe.Label", background=CARD, foreground=ACCENT,
                     font=FONT_BOLD, padding=(10, 0))

        # Labels
        s.configure("TLabel", background=BG, foreground=TEXT_COLOR, font=FONT)
        s.configure("Card.TLabel", background=CARD, foreground=TEXT_COLOR, font=FONT)
        s.configure("Dim.TLabel", background=BG, foreground=TEXT_DIM, font=FONT_SUBTITLE)

        # Entry
        s.configure("TEntry", fieldbackground=INPUT_BG, borderwidth=1, relief="solid",
                     padding=(8, 6))

        # Combobox
        s.configure("TCombobox", fieldbackground=INPUT_BG, borderwidth=1, padding=(8, 6))

        # Buttons
        s.configure("Accent.TButton", background=ACCENT, foreground="white",
                     font=FONT_BOLD, padding=(16, 8), borderwidth=0)
        s.map("Accent.TButton",
               background=[("active", ACCENT_HOVER), ("pressed", ACCENT_PRESSED), ("disabled", "#D0D0D0")],
               foreground=[("disabled", "#999999")])

        s.configure("Secondary.TButton", background=SECONDARY, foreground="white",
                     font=FONT_BOLD, padding=(12, 8), borderwidth=0)
        s.map("Secondary.TButton",
               background=[("active", SECONDARY_HOVER), ("pressed", "#2D6AA0"), ("disabled", "#D0D0D0")],
               foreground=[("disabled", "#999999")])

        s.configure("Outline.TButton", background=CARD, foreground=ACCENT,
                     font=FONT_BOLD, padding=(12, 8), borderwidth=1, relief="solid")
        s.map("Outline.TButton",
               background=[("active", "#FFF0F3"), ("disabled", "#F5F5F5")],
               foreground=[("disabled", "#AAAAAA")],
               bordercolor=[("!disabled", ACCENT)])

        # Radio buttons
        s.configure("Card.TRadiobutton", background=CARD, foreground=TEXT_COLOR, font=FONT)
        s.map("Card.TRadiobutton",
               indicatorbackground=[("selected", ACCENT), ("!selected", "#CCCCCC")])

        # Progress bar
        s.configure("Accent.Horizontal.TProgressbar", troughcolor=PB_TROUGH,
                     background=ACCENT, borderwidth=0, thickness=22)

    # ── Build UI ───────────────────────────────────────────────
    def _build_ui(self):
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=16)
        main.columnconfigure(0, weight=1)

        # ── Header row ──
        header = tk.Frame(main, bg=BG)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.title_lbl = tk.Label(header, text=self.L["title"], font=FONT_TITLE,
                                   bg=BG, fg=ACCENT)
        self.title_lbl.grid(row=0, column=0, sticky="w")

        # Language toggle
        self.lang_btn = tk.Button(header, text=self.L["lang_btn"], font=FONT_BOLD,
                                   bg=SECONDARY, fg="white", activebackground=SECONDARY_HOVER,
                                   activeforeground="white", bd=0, padx=14, pady=4,
                                   cursor="hand2", command=self._toggle_lang)
        self.lang_btn.grid(row=0, column=1, sticky="e", padx=(0, 4))

        self.subtitle_lbl = tk.Label(header, text=self.L["subtitle"], font=FONT_SUBTITLE,
                                      bg=BG, fg=TEXT_DIM)
        self.subtitle_lbl.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 10))

        # ── Device group ──
        self.device_frame = ttk.Labelframe(main, text=" " + self.L["device_group"] + " ",
                                            style="Card.TLabelframe")
        self.device_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        self.device_frame.columnconfigure(1, weight=1)

        self.port_lbl = ttk.Label(self.device_frame, text=self.L["port"], style="Card.TLabel")
        self.port_lbl.grid(row=0, column=0, padx=(12, 4), pady=10, sticky="w")

        self.port_var = tk.StringVar()
        self.port_cb = ttk.Combobox(self.device_frame, textvariable=self.port_var,
                                     state="readonly", width=36)
        self.port_cb.grid(row=0, column=1, padx=4, pady=10, sticky="ew")

        self.refresh_btn = ttk.Button(self.device_frame, text=self.L["refresh"],
                                       style="Secondary.TButton", command=self._refresh_ports)
        self.refresh_btn.grid(row=0, column=2, padx=4, pady=10)

        self.baud_lbl = ttk.Label(self.device_frame, text=self.L["baud"], style="Card.TLabel")
        self.baud_lbl.grid(row=0, column=3, padx=(10, 4), pady=10, sticky="w")

        self.baud_var = tk.StringVar(value="921600")
        self.baud_cb = ttk.Combobox(self.device_frame, textvariable=self.baud_var,
                                     values=["921600", "460800", "115200"], width=8, state="readonly")
        self.baud_cb.grid(row=0, column=4, padx=4, pady=10)

        self.info_btn = ttk.Button(self.device_frame, text=self.L["read_info"],
                                    style="Secondary.TButton", command=self._read_info)
        self.info_btn.grid(row=0, column=5, padx=(4, 12), pady=10)

        # Status
        self.status_lbl = tk.Label(main, text=self.L["status_disconnected"],
                                    font=FONT_STATUS, bg=BG, fg=TEXT_DIM)
        self.status_lbl.grid(row=2, column=0, sticky="w", pady=(0, 6))

        # ── Backup group ──
        self.bak_frame = ttk.Labelframe(main, text=" " + self.L["backup_group"] + " ",
                                         style="Card.TLabelframe")
        self.bak_frame.grid(row=3, column=0, sticky="ew", pady=(0, 6))
        self.bak_frame.columnconfigure(1, weight=1)

        self.save_lbl = ttk.Label(self.bak_frame, text=self.L["save_to"], style="Card.TLabel")
        self.save_lbl.grid(row=0, column=0, padx=(12, 4), pady=(10, 4), sticky="w")

        self.bak_path = tk.StringVar()
        self.bak_entry = ttk.Entry(self.bak_frame, textvariable=self.bak_path)
        self.bak_entry.grid(row=0, column=1, columnspan=3, padx=4, pady=(10, 4), sticky="ew")

        self.bak_browse_btn = ttk.Button(self.bak_frame, text=self.L["browse"],
                                           style="Secondary.TButton",
                                           command=lambda: self._browse_save(self.bak_path, self.L["save_backup_title"]))
        self.bak_browse_btn.grid(row=0, column=4, padx=4, pady=(10, 4))

        self.size_lbl = ttk.Label(self.bak_frame, text=self.L["size"], style="Card.TLabel")
        self.size_lbl.grid(row=1, column=0, padx=(12, 4), pady=4, sticky="w")

        self.bak_size_var = tk.StringVar(value="16MB")
        self.bak_size_cb = ttk.Combobox(self.bak_frame, textvariable=self.bak_size_var,
                                          values=["16MB", "8MB", "4MB", "1MB"], width=6, state="readonly")
        self.bak_size_cb.grid(row=1, column=1, padx=4, pady=4, sticky="w")

        self.bak_btn = ttk.Button(self.bak_frame, text=self.L["backup"],
                                   style="Accent.TButton", command=self._start_backup)
        self.bak_btn.grid(row=1, column=3, padx=4, pady=4)

        self.bak_cancel_btn = ttk.Button(self.bak_frame, text=self.L["cancel"],
                                           style="Outline.TButton",
                                           command=lambda: self.bak_cancel.set())
        self.bak_cancel_btn.grid(row=1, column=4, padx=(4, 12), pady=4)
        self.bak_cancel_btn.state(["disabled"])

        self.bak_pb_var = tk.DoubleVar(value=0)
        self.bak_pb = ttk.Progressbar(self.bak_frame, variable=self.bak_pb_var,
                                        maximum=100, style="Accent.Horizontal.TProgressbar")
        self.bak_pb.grid(row=2, column=0, columnspan=5, padx=12, pady=(4, 0), sticky="ew")
        self.bak_pb_text = tk.Label(self.bak_frame, text=self.L["ready"],
                                      font=FONT_STATUS, bg=CARD, fg=TEXT_DIM)
        self.bak_pb_text.grid(row=3, column=0, columnspan=5, padx=12, pady=(0, 10), sticky="")
        self.bak_start_time = None

        # ── Flash group ──
        self.flash_frame = ttk.Labelframe(main, text=" " + self.L["flash_group"] + " ",
                                           style="Card.TLabelframe")
        self.flash_frame.grid(row=4, column=0, sticky="ew", pady=(0, 6))
        self.flash_frame.columnconfigure(1, weight=1)

        self.flash_mode = tk.StringVar(value="full")

        self.radio_full = ttk.Radiobutton(self.flash_frame, text=self.L["mode_full"],
                                           variable=self.flash_mode, value="full",
                                           style="Card.TRadiobutton")
        self.radio_full.grid(row=0, column=0, columnspan=5, padx=12, pady=(10, 2), sticky="w")

        self.radio_ota = ttk.Radiobutton(self.flash_frame, text=self.L["mode_ota"],
                                           variable=self.flash_mode, value="ota",
                                           style="Card.TRadiobutton")
        self.radio_ota.grid(row=1, column=0, columnspan=5, padx=12, pady=2, sticky="w")

        self.radio_restore = ttk.Radiobutton(self.flash_frame, text=self.L["mode_restore"],
                                               variable=self.flash_mode, value="restore",
                                               style="Card.TRadiobutton")
        self.radio_restore.grid(row=2, column=0, columnspan=5, padx=12, pady=(2, 6), sticky="w")

        self.file_lbl = ttk.Label(self.flash_frame, text=self.L["file"], style="Card.TLabel")
        self.file_lbl.grid(row=3, column=0, padx=(12, 4), pady=4, sticky="w")

        self.flash_path = tk.StringVar()
        self.flash_entry = ttk.Entry(self.flash_frame, textvariable=self.flash_path)
        self.flash_entry.grid(row=3, column=1, columnspan=3, padx=4, pady=4, sticky="ew")

        self.flash_browse_btn = ttk.Button(self.flash_frame, text=self.L["browse"],
                                              style="Secondary.TButton",
                                              command=lambda: self._browse_open(self.flash_path, self.L["select_fw_title"]))
        self.flash_browse_btn.grid(row=3, column=4, padx=4, pady=4)

        self.flash_btn = ttk.Button(self.flash_frame, text=self.L["flash"],
                                     style="Accent.TButton", command=self._start_flash)
        self.flash_btn.grid(row=4, column=3, padx=4, pady=(4, 10))

        self.flash_cancel_btn = ttk.Button(self.flash_frame, text=self.L["cancel"],
                                             style="Outline.TButton",
                                             command=self._confirm_cancel_flash)
        self.flash_cancel_btn.grid(row=4, column=4, padx=(4, 12), pady=(4, 10))
        self.flash_cancel_btn.state(["disabled"])

        self.flash_pb_var = tk.DoubleVar(value=0)
        self.flash_pb = ttk.Progressbar(self.flash_frame, variable=self.flash_pb_var,
                                          maximum=100, style="Accent.Horizontal.TProgressbar")
        self.flash_pb.grid(row=5, column=0, columnspan=5, padx=12, pady=(0, 0), sticky="ew")
        self.flash_pb_text = tk.Label(self.flash_frame, text=self.L["ready"],
                                        font=FONT_STATUS, bg=CARD, fg=TEXT_DIM)
        self.flash_pb_text.grid(row=6, column=0, columnspan=5, padx=12, pady=(0, 10), sticky="")
        self.flash_start_time = None

        # ── Log area ──
        self.log_text = scrolledtext.ScrolledText(main, height=8, font=FONT_LOG,
                                                   bg=LOG_BG, fg="#444444",
                                                   relief="solid", bd=1, highlightthickness=0,
                                                   wrap="word", state="disabled")
        self.log_text.grid(row=5, column=0, sticky="nsew", pady=(0, 0))
        self.log_text.tag_configure("ts", foreground="#AAAAAA")
        main.rowconfigure(5, weight=1)

    # ── i18n helpers ───────────────────────────────────────────
    def _t(self, key):
        return self.L.get(key, key)

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.L = LANG[self.lang]
        self._apply_lang()

    def _apply_lang(self):
        L = self.L
        self.title_lbl.config(text=L["title"])
        self.subtitle_lbl.config(text=L["subtitle"])
        self.lang_btn.config(text=L["lang_btn"])
        self.device_frame.config(text=" " + L["device_group"] + " ")
        self.port_lbl.config(text=L["port"])
        self.refresh_btn.config(text=L["refresh"])
        self.baud_lbl.config(text=L["baud"])
        self.info_btn.config(text=L["read_info"])
        status = self.status_lbl.cget("text")
        if status in (LANG["zh"]["status_disconnected"], LANG["en"]["status_disconnected"]):
            self.status_lbl.config(text=L["status_disconnected"])
        elif status in (LANG["zh"]["status_connecting"], LANG["en"]["status_connecting"]):
            self.status_lbl.config(text=L["status_connecting"])
        elif status in (LANG["zh"]["status_connected"], LANG["en"]["status_connected"]):
            self.status_lbl.config(text=L["status_connected"])

        self.bak_frame.config(text=" " + L["backup_group"] + " ")
        self.save_lbl.config(text=L["save_to"])
        self.bak_browse_btn.config(text=L["browse"])
        self.size_lbl.config(text=L["size"])
        self.bak_btn.config(text=L["backup"])
        self.bak_cancel_btn.config(text=L["cancel"])
        self.bak_entry.delete(0, "end")
        self.bak_entry.insert(0, self.bak_path.get())

        self.flash_frame.config(text=" " + L["flash_group"] + " ")
        self.radio_full.config(text=L["mode_full"])
        self.radio_ota.config(text=L["mode_ota"])
        self.radio_restore.config(text=L["mode_restore"])
        self.file_lbl.config(text=L["file"])
        self.flash_browse_btn.config(text=L["browse"])
        self.flash_btn.config(text=L["flash"])
        self.flash_cancel_btn.config(text=L["cancel"])

        # Update progress bar texts
        self.bak_pb_text.config(text=L["ready"])
        self.flash_pb_text.config(text=L["ready"])

    # ── Log ────────────────────────────────────────────────────
    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{ts}] ", "ts")
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ── Ports ──────────────────────────────────────────────────
    def _selected_port(self):
        sel = self.port_cb.current()
        if sel < 0:
            return None
        return self.port_cb["values"][sel].split(" - ")[0]

    def _refresh_ports(self):
        self.port_cb["values"] = []
        try:
            ports = flasher.list_ports()
            items = [f"{p['device']} - {p['description']}" for p in ports]
            self.port_cb["values"] = items
            if items:
                self.port_cb.current(0)
            self._log(self._t("log_ports_found").format(n=len(items)))
        except Exception as e:
            self._log(str(e))

    # ── Device info ────────────────────────────────────────────
    def _read_info(self):
        port = self._selected_port()
        if not port:
            self._log(self._t("log_select_port"))
            return
        self._log(self._t("log_connecting").format(port=port))
        self.status_lbl.config(text=self._t("status_connecting"), fg=ACCENT)
        self.update_idletasks()
        try:
            r = flasher.get_flash_info(port)
        except Exception as e:
            self.status_lbl.config(text=self._t("status_failed"), fg=ACCENT)
            self._log(self._t("log_failed").format(err=str(e)))
            return
        if r.get("error"):
            self.status_lbl.config(text=self._t("status_failed"), fg=ACCENT)
            self._log(self._t("log_failed").format(err=r["error"]))
        else:
            self.status_lbl.config(text=self._t("status_connected"), fg=GREEN)
            self._log(r.get("output", self._t("status_connected")))

    # ── Browse dialogs ─────────────────────────────────────────
    def _browse_save(self, var, title):
        p = filedialog.asksaveasfilename(title=title, defaultextension=".bin",
                                          filetypes=[("Binary", "*.bin"), ("All", "*.*")])
        if p:
            var.set(p)

    def _browse_open(self, var, title):
        p = filedialog.askopenfilename(title=title,
                                        filetypes=[("Binary", "*.bin"), ("All", "*.*")])
        if p:
            var.set(p)

    # ── Backup ─────────────────────────────────────────────────
    def _start_backup(self):
        port = self._selected_port()
        if not port:
            self._log(self._t("log_select_port"))
            return
        path = self.bak_path.get().strip()
        if not path:
            self._log(self._t("log_select_valid_file"))
            return
        sz = self.bak_size_var.get()
        size_map = {"16MB": 0x1000000, "8MB": 0x800000, "4MB": 0x400000, "1MB": 0x100000}
        size = size_map[sz]

        if not messagebox.askyesno(self._t("confirm_backup_title"),
                                    self._t("confirm_backup_msg").format(sz=sz, path=path)):
            self._log(self._t("log_cancelled"))
            return

        self.bak_cancel.clear()
        self.bak_pb_var.set(0)
        self.bak_pb_text.config(text=self._t("pb_connecting"), bg=CARD)
        self.bak_btn.state(["disabled"])
        self.bak_cancel_btn.state(["!disabled"])
        baud = int(self.baud_var.get())
        self.bak_start_time = datetime.now()

        def run():
            from datetime import datetime as dt
            status_map = {
                "connecting": self.L["status_connecting"],
                "extracting": self.L["extracting"],
                "writing": self.L["writing_status"],
                "done": self.L["pb_done"],
                "cancelled": self.L["log_cancelled"],
            }
            def progress(pct, status):
                translated = status_map.get(status, status)
                elapsed = dt.now() - self.bak_start_time
                elapsed_str = f"{int(elapsed.total_seconds())//60}:{int(elapsed.total_seconds())%60:02d}"
                self.after(0, lambda: self.bak_pb_var.set(pct))
                if pct >= 100:
                    self.after(0, lambda: self.bak_pb_text.config(
                        text=f"✅ {translated} ({elapsed_str})", fg="#27AE60", bg=CARD))
                else:
                    self.after(0, lambda: self.bak_pb_text.config(
                        text=f"{pct:.0f}%  -  {translated}  [{elapsed_str}]", fg=TEXT_DIM, bg=CARD))
            try:
                ok, msg = flasher.read_flash(port, baud, 0, size, path,
                                              self.bak_cancel, progress)
                self.after(0, lambda: self._bak_done(ok, msg))
            except Exception as e:
                self.after(0, lambda: self._bak_done(False, str(e)))

        self._bak_thread = Thread(target=run, daemon=True)
        self._bak_thread.start()

    def _bak_done(self, ok, msg):
        self.bak_btn.state(["!disabled"])
        self.bak_cancel_btn.state(["disabled"])
        self.bak_pb_var.set(100 if ok else 0)
        if ok:
            self._log(self._t("bak_success").format(msg=msg))
        else:
            # Keep progress label short, dump full error to log area
            short_msg = "❌ " + msg.splitlines()[0]
            self.bak_pb_text.config(text=short_msg, fg=ACCENT)
            self._log(f"❌ {msg}")

    # ── Flash ──────────────────────────────────────────────────
    def _start_flash(self):
        port = self._selected_port()
        if not port:
            self._log(self._t("log_select_port"))
            return
        path = self.flash_path.get().strip()
        if not path or not os.path.exists(path):
            self._log(self._t("log_select_valid_file"))
            return
        baud = int(self.baud_var.get())
        mode = self.flash_mode.get()

        if mode == "full":
            d = os.path.dirname(path)
            pairs = [(0x0, f"{d}/bootloader.bin"), (0x8000, f"{d}/partitions.bin"), (0x10000, path)]
            missing = [f for _, f in pairs if not os.path.exists(f)]
            if missing:
                self._log(self._t("log_full_requires"))
                for addr, fp in pairs:
                    self._log(f"  {os.path.basename(fp)}")
                for m in missing:
                    self._log(self._t("log_missing").format(name=os.path.basename(m)))
                return
            warn_key = "warn_full_msg"
        elif mode == "ota":
            pairs = [(0x10000, path)]
            warn_key = "warn_ota_msg"
        else:
            pairs = [(0x0, path)]
            warn_key = "warn_restore_msg"

        if not messagebox.askyesno(self._t("warn_full_title"), self._t(warn_key)):
            self._log(self._t("log_cancelled"))
            return

        self.flash_cancel.clear()
        self.flash_pb_var.set(0)
        self.flash_pb_text.config(text=self._t("pb_preparing"), bg=CARD)
        self.flash_btn.state(["disabled"])
        self.flash_cancel_btn.state(["!disabled"])
        self.flash_start_time = datetime.now()

        def run():
            from datetime import datetime as dt
            status_map = {
                "connecting": self.L["status_connecting"],
                "extracting": self.L["extracting"],
                "writing": self.L["writing_status"],
                "done": self.L["pb_done"],
                "cancelled": self.L["log_cancelled"],
            }
            def progress(pct, status):
                translated = status_map.get(status, status)
                elapsed = dt.now() - self.flash_start_time
                elapsed_str = f"{int(elapsed.total_seconds())//60}:{int(elapsed.total_seconds())%60:02d}"
                self.after(0, lambda: self.flash_pb_var.set(pct))
                if pct >= 100:
                    self.after(0, lambda: self.flash_pb_text.config(
                        text=f"✅ {translated} ({elapsed_str})", fg="#27AE60", bg=CARD))
                else:
                    self.after(0, lambda: self.flash_pb_text.config(
                        text=f"{pct:.0f}%  -  {translated}  [{elapsed_str}]", fg=TEXT_DIM, bg=CARD))
            try:
                ok, msg = flasher.write_flash(port, baud, pairs,
                                                self.flash_cancel, progress)
                self.after(0, lambda: self._flash_done(ok, msg))
            except Exception as e:
                self.after(0, lambda: self._flash_done(False, str(e)))

        self._flash_thread = Thread(target=run, daemon=True)
        self._flash_thread.start()

    def _confirm_cancel_flash(self):
        warn = self.L.get("cancel_warn",
            "Cancelling during flash may damage the bootloader.\nAre you sure?")
        if messagebox.askyesno("Warning" if self.lang == "en" else "警告", warn):
            self.flash_cancel.set()
            self._log(self.L["log_cancelled"])

    def _flash_done(self, ok, msg):
        self.flash_btn.state(["!disabled"])
        self.flash_cancel_btn.state(["disabled"])
        self.flash_pb_var.set(100 if ok else 0)
        if ok:
            self._log(self._t("flash_success"))
        else:
            # Keep progress label short, dump full error to log area
            short_msg = "❌ " + msg.splitlines()[0]
            self.flash_pb_text.config(text=short_msg, fg=ACCENT)
            self._log(f"❌ {msg}")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
