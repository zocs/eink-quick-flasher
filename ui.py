"""X3 Flasher - PyQt5 GUI"""
import sys, os
from datetime import datetime
from threading import Event
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import flasher

CSS = """
QMainWindow { background: #F5F5F5; }
QWidget { background: #F5F5F5; color: #1A1A2E; font-family: 'Segoe UI','Microsoft YaHei'; font-size: 13px; }
QGroupBox { background: white; border: 1px solid #E0E0E0; border-radius: 10px; margin-top: 14px; padding: 18px 10px 10px 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; color: #E43F5A; font-weight: bold; font-size: 14px; }
QPushButton { background: #E43F5A; border: none; border-radius: 8px; padding: 8px 16px; color: white; font-weight: bold; }
QPushButton:hover { background: #FF5A7A; }
QPushButton:pressed { background: #C0354A; }
QPushButton:disabled { background: #D0D0D0; color: #999; }
QPushButton[flat="true"] { background: white; color: #E43F5A; border: 1px solid #E43F5A; }
QPushButton[flat="true"]:hover { background: #FFF0F3; }
QLineEdit { background: white; border: 1px solid #D0D0D0; border-radius: 8px; padding: 6px 10px; color: #1A1A2E; }
QLineEdit:focus { border: 1px solid #E43F5A; }
QComboBox { background: white; border: 1px solid #D0D0D0; border-radius: 8px; padding: 6px 10px; color: #1A1A2E; min-width: 80px; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background: white; border: 1px solid #E0E0E0; selection-background-color: #E43F5A; color: #1A1A2E; }
QProgressBar { background: #F0F0F0; border: 1px solid #E0E0E0; border-radius: 8px; height: 24px; text-align: center; color: #1A1A2E; font-weight: bold; }
QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #E43F5A, stop:1 #FF8A65); border-radius: 7px; margin: 1px; }
QTextEdit { background: #FAFAFA; border: 1px solid #E0E0E0; border-radius: 8px; padding: 8px; color: #444; font-family: 'Cascadia Code','Consolas'; font-size: 12px; }
QRadioButton { spacing: 6px; color: #333; }
QRadioButton::indicator { width: 16px; height: 16px; border-radius: 8px; border: 2px solid #CCC; background: white; }
QRadioButton::indicator:checked { background: #E43F5A; border-color: #E43F5A; }
QLabel { color: #555; }
"""

class Worker(QThread):
    sig_progress = pyqtSignal(float, str)
    sig_done = pyqtSignal(bool, str)
    def __init__(self, fn, cancel, *a):
        super().__init__()
        self.fn = fn
        self.cancel = cancel
        self.a = a
    def run(self):
        try:
            ok, msg = self.fn(*self.a, cancel_event=self.cancel, progress_callback=lambda p, s: self.sig_progress.emit(p, s))
            self.sig_done.emit(ok, msg)
        except Exception as e:
            self.sig_done.emit(False, str(e))

class Win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EInk Quick Flasher")
        self.setMinimumSize(620, 700)
        self.bak_w = self.flash_w = None
        self.bak_ev = Event()
        self.flash_ev = Event()
        self._ui()
        self.setStyleSheet(CSS)
        self._ports()

    def _ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        lay = QVBoxLayout(c)
        lay.setSpacing(12)
        lay.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("EInk Quick Flasher")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #E43F5A; padding: 4px 0;")
        lay.addWidget(title)

        subtitle = QLabel("ESP32-C3 墨水屏阅读器备份与刷机工具  |  X3 / X4")
        subtitle.setStyleSheet("font-size: 12px; color: #999; padding: 0 0 8px 0;")
        lay.addWidget(subtitle)

        # Device
        dg = QGroupBox("设备连接")
        dl = QHBoxLayout(dg)
        dl.addWidget(QLabel("串口:"))
        self.port_cb = QComboBox()
        self.port_cb.setMinimumWidth(260)
        self.port_cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dl.addWidget(self.port_cb)
        rb = QPushButton("刷新")
        rb.setStyleSheet("background: #4A90D9;")
        rb.clicked.connect(self._ports)
        dl.addWidget(rb)
        dl.addWidget(QLabel("波特率:"))
        self.baud_cb = QComboBox()
        self.baud_cb.addItems(["921600", "460800", "115200"])
        dl.addWidget(self.baud_cb)
        ib = QPushButton("读取信息")
        ib.setStyleSheet("background: #4A90D9;")
        ib.clicked.connect(self._info)
        dl.addWidget(ib)
        dl.addStretch()
        lay.addWidget(dg)

        self.status_lb = QLabel("未连接")
        self.status_lb.setStyleSheet("color: #999; font-size: 12px; padding: 2px 0;")
        lay.addWidget(self.status_lb)

        # Backup
        bg = QGroupBox("备份 Flash")
        bl = QVBoxLayout(bg)
        bl.setSpacing(8)
        bh = QHBoxLayout()
        bh.addWidget(QLabel("保存到:"))
        self.bak_le = QLineEdit()
        self.bak_le.setPlaceholderText("选择保存路径...")
        self.bak_le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bh.addWidget(self.bak_le)
        bb = QPushButton("浏览")
        bb.setStyleSheet("background: #4A90D9;")
        bb.clicked.connect(lambda: self._browse(self.bak_le, "保存备份", "x3_backup.bin"))
        bh.addWidget(bb)
        self.bak_sz = QComboBox()
        self.bak_sz.addItems(["16MB", "8MB", "4MB", "1MB"])
        bh.addWidget(self.bak_sz)
        self.btn_bak = QPushButton("备份")
        self.btn_bak.clicked.connect(self._start_bak)
        bh.addWidget(self.btn_bak)
        self.btn_bak_c = QPushButton("终止")
        self.btn_bak_c.setProperty("flat", True)
        self.btn_bak_c.setEnabled(False)
        self.btn_bak_c.clicked.connect(lambda: self.bak_ev.set())
        bh.addWidget(self.btn_bak_c)
        bl.addLayout(bh)
        self.bak_pb = QProgressBar()
        self.bak_pb.setFormat("就绪")
        bl.addWidget(self.bak_pb)
        lay.addWidget(bg)

        # Flash
        fg = QGroupBox("刷入固件")
        fl = QVBoxLayout(fg)
        fl.setSpacing(8)
        self.m_full = QRadioButton("完整写入 (自动检测 bootloader.bin + partitions.bin + 固件文件)")
        self.m_full.setChecked(True)
        fl.addWidget(self.m_full)
        self.m_ota = QRadioButton("OTA 更新 (仅写应用)")
        fl.addWidget(self.m_ota)
        self.m_res = QRadioButton("恢复原厂 (从备份文件)")
        fl.addWidget(self.m_res)
        fh = QHBoxLayout()
        fh.addWidget(QLabel("文件:"))
        self.flash_le = QLineEdit()
        self.flash_le.setPlaceholderText("选择固件文件...")
        self.flash_le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        fh.addWidget(self.flash_le)
        fb = QPushButton("浏览")
        fb.setStyleSheet("background: #4A90D9;")
        fb.clicked.connect(lambda: self._browse(self.flash_le, "选择固件", "", "Binary (*.bin)"))
        fh.addWidget(fb)
        self.btn_fl = QPushButton("刷入")
        self.btn_fl.clicked.connect(self._start_fl)
        fh.addWidget(self.btn_fl)
        self.btn_fl_c = QPushButton("终止")
        self.btn_fl_c.setProperty("flat", True)
        self.btn_fl_c.setEnabled(False)
        self.btn_fl_c.clicked.connect(lambda: self.flash_ev.set())
        fh.addWidget(self.btn_fl_c)
        fl.addLayout(fh)
        self.fl_pb = QProgressBar()
        self.fl_pb.setFormat("就绪")
        fl.addWidget(self.fl_pb)
        lay.addWidget(fg)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(130)
        lay.addWidget(self.log)

        self._log("就绪。请连接设备。")

    def _log(self, m):
        self.log.append(f"<span style='color:#999'>[{datetime.now():%H:%M:%S}]</span> {m}")

    def _ports(self):
        self.port_cb.clear()
        for p in flasher.list_ports():
            self.port_cb.addItem(f"{p['device']} - {p['description']}", p['device'])
        self._log(f"串口: {self.port_cb.count()} 个")

    def _port(self):
        return self.port_cb.itemData(self.port_cb.currentIndex())

    def _baud(self):
        return int(self.baud_cb.currentText())

    def _browse(self, le, title, defname, filt="Binary (*.bin)"):
        if defname:
            p, _ = QFileDialog.getSaveFileName(self, title, defname, filt)
        else:
            p, _ = QFileDialog.getOpenFileName(self, title, "", filt)
        if p:
            le.setText(p)

    def _info(self):
        port = self._port()
        if not port:
            self._log("请选择串口")
            return
        self._log(f"连接 {port}...")
        self.status_lb.setText("连接中...")
        self.status_lb.setStyleSheet("color: #E43F5A; font-size: 12px;")
        r = flasher.get_flash_info(port)
        if r.get("error"):
            self.status_lb.setText(f"连接失败: {r['error']}")
            self.status_lb.setStyleSheet("color: #E43F5A; font-size: 12px;")
            self._log(f"失败: {r['error']}")
        else:
            self.status_lb.setText("已连接")
            self.status_lb.setStyleSheet("color: #27AE60; font-weight: bold; font-size: 12px;")
            self._log(r.get("output", "已连接"))

    def _confirm(self, title, msg):
        return QMessageBox.warning(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes

    def _start_bak(self):
        port = self._port()
        if not port:
            self._log("请选择串口")
            return
        path = self.bak_le.text().strip()
        if not path:
            self._log("请选择保存路径")
            return
        sz = self.bak_sz.currentText()
        size = {"16MB": 0x1000000, "8MB": 0x800000, "4MB": 0x400000, "1MB": 0x100000}[sz]
        if not self._confirm("确认备份", f"将提取 {sz} Flash 内容到：\n{path}\n\n请保持数据线连接。\n\n确认开始？"):
            self._log("已取消")
            return
        self.bak_ev.clear()
        self.bak_pb.setValue(0)
        self.bak_pb.setFormat("0%  -  连接...")
        self.btn_bak.setEnabled(False)
        self.btn_bak_c.setEnabled(True)
        self.bak_w = Worker(flasher.read_flash, self.bak_ev, port, self._baud(), 0, size, path)
        self.bak_w.sig_progress.connect(lambda p, s: (self.bak_pb.setValue(int(p)), self.bak_pb.setFormat(f"{p:.0f}%  -  {s}")))
        self.bak_w.sig_done.connect(self._bak_done)
        self.bak_w.start()

    def _bak_done(self, ok, m):
        self.btn_bak.setEnabled(True)
        self.btn_bak_c.setEnabled(False)
        self.bak_pb.setFormat("100%  -  完成" if ok else m)
        self.bak_pb.setValue(100 if ok else 0)
        self._log(f"{'✅' if ok else '❌'} {m}")
        if ok:
            self._log("拔线 → 按一下 Reset 键 → 长按电源键重启")

    def _start_fl(self):
        port = self._port()
        if not port:
            self._log("请选择串口")
            return
        path = self.flash_le.text().strip()
        if not path or not os.path.exists(path):
            self._log("请选择有效文件")
            return
        baud = self._baud()
        if self.m_full.isChecked():
            d = os.path.dirname(path)
            pairs = [(0x0, f"{d}/bootloader.bin"), (0x8000, f"{d}/partitions.bin"), (0x10000, path)]
            missing = [f for a, f in pairs if not os.path.exists(f)]
            if missing:
                self._log("完整写入需要以下文件在同一目录:")
                for addr, fp in pairs:
                    self._log(f"  {os.path.basename(fp)}")
                for m in missing:
                    self._log(f"缺少: {os.path.basename(m)}")
                return
            warn = "⚠️ 完整写入会改变分区布局！\n\n• 确保已完成备份\n• 写入中请保持连接\n• 断开有变砖风险\n\n确认？"
        elif self.m_ota.isChecked():
            pairs = [(0x10000, path)]
            warn = "即将 OTA 更新\n\n• 写入中请保持连接\n• 断开有变砖风险\n\n确认？"
        else:
            pairs = [(0x0, path)]
            warn = "⚠️ 恢复原厂！覆盖整个 Flash\n\n• 写入中请保持连接\n• 断开有变砖风险\n\n确认？"
        if not self._confirm("风险提示", warn):
            self._log("已取消")
            return
        self.flash_ev.clear()
        self.fl_pb.setValue(0)
        self.fl_pb.setFormat("0%  -  准备写入")
        self.btn_fl.setEnabled(False)
        self.btn_fl_c.setEnabled(True)
        self.flash_w = Worker(flasher.write_flash, self.flash_ev, port, baud, pairs)
        self.flash_w.sig_progress.connect(lambda p, s: (self.fl_pb.setValue(int(p)), self.fl_pb.setFormat(f"{p:.0f}%  -  {s}")))
        self.flash_w.sig_done.connect(self._fl_done)
        self.flash_w.start()

    def _fl_done(self, ok, m):
        self.btn_fl.setEnabled(True)
        self.btn_fl_c.setEnabled(False)
        self.fl_pb.setFormat("100%  -  完成" if ok else m)
        self.fl_pb.setValue(100 if ok else 0)
        self._log(f"{'✅' if ok else '❌'} {m}")
        if ok:
            self._log("拔线 → 按一下 Reset 键 → 长按电源键重启")
